from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Exam, Question, StudentExamResult
from accounts.models import User, Student, Teacher
from datetime import datetime, timedelta
import json
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.serializers import ExamSerializer
from django.db.models import Avg, Max, Min, Count
from django.db.models.functions import Cast
from django.db.models import FloatField

@login_required
def exam_list(request):
    user = request.user
    now = datetime.now()

    if hasattr(user, 'teacher_profile'):
        exams = Exam.objects.filter(created_by=user.teacher_profile)
    elif hasattr(user, 'student_profile'):
        exams = Exam.objects.filter(
            start_time__lte=now,
            end_time__gte=now
        )
    else:  # admin
        exams = Exam.objects.all()

    context = {'exams': exams}
    return render(request, 'exams/exam_list.html', context)

@login_required
def create_exam(request):
    if not hasattr(request.user, 'teacher_profile'):
        raise PermissionDenied
    
    if request.method == 'GET':
        return render(request, 'exams/create_exam.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            subject = data.get('subject')
            department = data.get('department')
            semester = data.get('semester')
            duration = data.get('duration')
            passing_score = data.get('passing_score')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            questions = data.get('questions', [])
            
            if not all([title, subject, department, semester, duration, passing_score, start_time, end_time]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Create exam
            exam = Exam.objects.create(
                title=title,
                subject=subject,
                department=department,
                semester=semester,
                duration=duration,
                passing_score=passing_score,
                start_time=start_time,
                end_time=end_time,
                created_by=request.user.teacher_profile,
                questions=questions
            )
            
            return JsonResponse({'message': 'Exam created successfully'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def take_exam(request, exam_id):
    if not hasattr(request.user, 'student_profile'):
        raise PermissionDenied
    
    exam = get_object_or_404(Exam, id=exam_id)
    student = request.user.student_profile
    
    # Check if student is eligible to take this exam
    if exam.department != student.department or exam.semester != student.semester:
        raise PermissionDenied
    
    # Check if exam is currently available (including late submission period)
    now = timezone.now()
    if not exam.is_available(now):
        return JsonResponse({'error': 'Exam is not currently available'}, status=400)
    
    # Check if student has already taken this exam
    if StudentExamResult.objects.filter(student=student, exam=exam).exists():
        return JsonResponse({'error': 'You have already taken this exam'}, status=400)
    
    if request.method == 'GET':
        return render(request, 'exams/take_exam.html', {'exam': exam})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
            
            # Calculate score
            total_marks = 0
            obtained_marks = 0
            
            for question_id, answer in answers.items():
                question = Question.objects.get(id=question_id)
                total_marks += question.marks
                if answer == question.correct_answer:
                    obtained_marks += question.marks
            
            # Check if this is a late submission
            is_late = exam.is_late_submission(now)
            
            # Create exam result
            status = 'pass' if obtained_marks >= exam.passing_score else 'fail'
            StudentExamResult.objects.create(
                student=student,
                exam=exam,
                obtained_marks=obtained_marks,
                status=status,
                is_late_submission=is_late,
                submitted_at=now
            )
            
            return JsonResponse({
                'message': 'Exam submitted successfully',
                'score': obtained_marks,
                'total': total_marks,
                'status': status,
                'is_late': is_late
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def view_results(request):
    if not hasattr(request.user, 'teacher_profile'):
        raise PermissionDenied
    
    teacher = request.user.teacher_profile
    exams = Exam.objects.filter(created_by=teacher)
    results = StudentExamResult.objects.filter(exam__in=exams)
    
    return render(request, 'exams/view_results.html', {
        'results': results
    })

@login_required
def api_student_exams(request):
    if not hasattr(request.user, 'student_profile'):
        return JsonResponse({'error': 'Not a student'}, status=403)
    student = request.user.student_profile
    now = timezone.now()
    exams = Exam.objects.filter(
        department=student.department,
        semester=student.semester,
        start_time__lte=now,
        end_time__gte=now
    )
    exam_list = [
        {
            'id': exam.id,
            'title': exam.title,
            'subject': exam.subject,
            'duration': exam.duration,
            'totalQuestions': getattr(exam, 'total_questions', 0),
            'deadline': exam.end_time.isoformat() if exam.end_time else '',
        }
        for exam in exams
    ]
    return JsonResponse(exam_list, safe=False)

@login_required
def api_student_profile(request):
    if not hasattr(request.user, 'student_profile'):
        return JsonResponse({'error': 'Not a student'}, status=403)
    student = request.user.student_profile
    user = request.user
    data = {
        'fullName': f"{user.first_name} {user.last_name}".strip(),
        'email': user.email,
        'phoneNumber': getattr(user, 'phone_number', ''),
        'department': student.department,
        'semester': student.semester,
        'studentId': user.username,
    }
    return JsonResponse(data)

@login_required
def api_student_results(request):
    if not hasattr(request.user, 'student_profile'):
        return JsonResponse({'error': 'Not a student'}, status=403)
    student = request.user.student_profile
    results = StudentExamResult.objects.filter(student=student).select_related('exam')
    data = [
        {
            'examTitle': result.exam.title,
            'obtainedMarks': result.obtained_marks,
            'status': result.status,
            'submittedAt': result.submitted_at.isoformat() if result.submitted_at else '',
        }
        for result in results
    ]
    return JsonResponse(data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_subjects(request):
    try:
        # Predefined list of all possible subjects
        subjects = [
            {"id": 1, "name": "Mathematics 1"},
            {"id": 2, "name": "Mathematics 2"},
            {"id": 3, "name": "Mathematics 3"},
            {"id": 4, "name": "Physics"},
            {"id": 5, "name": "Chemistry"},
            {"id": 6, "name": "Python"},
            {"id": 7, "name": "C"},
            {"id": 8, "name": "Digital Design and Computer Organization"},
            {"id": 9, "name": "Operating System"},
            {"id": 10, "name": "Data Structure and Algorithms"},
            {"id": 11, "name": "Analysis and Design of Algorithms"},
            {"id": 12, "name": "Database Management System"},
            {"id": 13, "name": "Data Science"},
            {"id": 14, "name": "Java"},
            {"id": 15, "name": "English"},
            {"id": 16, "name": "Computer Graphics"},
            {"id": 17, "name": "Artificial Intelligence"},
            {"id": 18, "name": "Machine Learning"},
            {"id": 19, "name": "Cyber Security"},
            {"id": 20, "name": "Internet of Things"}
        ]

        return Response({
            'success': True,
            'data': subjects
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exams(request):
    if not hasattr(request.user, 'teacher_profile'):
        return Response({'success': False, 'message': 'Not a teacher'}, status=403)
    teacher = request.user.teacher_profile
    exams = Exam.objects.filter(created_by=teacher).order_by('-created_at')
    serializer = ExamSerializer(exams, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_performance_report(request):
    try:
        # Get all students
        total_students = Student.objects.count()
        
        # Get all exam results
        results = StudentExamResult.objects.all()
        total_submissions = results.count()
        
        if total_submissions == 0:
            return Response({
                'success': True,
                'data': {
                    'totalStudents': total_students,
                    'passRate': 0,
                    'averageMark': 0,
                    'highestMark': 0,
                    'lowestMark': 0,
                    'gradeDistribution': {
                        'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0
                    }
                }
            })

        # Calculate pass rate
        passed_students = results.filter(status='pass').count()
        pass_rate = round((passed_students / total_submissions) * 100, 2)

        # Calculate marks statistics
        marks_stats = results.aggregate(
            avg_mark=Avg('obtained_marks'),
            max_mark=Max('obtained_marks'),
            min_mark=Min('obtained_marks')
        )

        # Calculate grade distribution
        grade_distribution = {
            'A': results.filter(obtained_marks__gte=85).count(),
            'B': results.filter(obtained_marks__gte=70, obtained_marks__lt=85).count(),
            'C': results.filter(obtained_marks__gte=55, obtained_marks__lt=70).count(),
            'D': results.filter(obtained_marks__gte=35, obtained_marks__lt=55).count(),
            'F': results.filter(obtained_marks__lt=35).count()
        }

        return Response({
            'success': True,
            'data': {
                'totalStudents': total_students,
                'passRate': pass_rate,
                'averageMark': round(marks_stats['avg_mark'], 2),
                'highestMark': marks_stats['max_mark'],
                'lowestMark': marks_stats['min_mark'],
                'gradeDistribution': grade_distribution
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attendance_report(request, exam_id):
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        
        # Get all students eligible for this exam
        eligible_students = Student.objects.filter(
            department=exam.department,
            semester=exam.semester
        )
        total_registered = eligible_students.count()
        
        # Get all submissions for this exam
        submissions = StudentExamResult.objects.filter(exam=exam)
        present = submissions.count()
        absent = total_registered - present
        
        # Calculate attendance rate
        attendance_rate = round((present / total_registered) * 100, 2) if total_registered > 0 else 0
        
        # Count late submissions
        late_submissions = submissions.filter(
            submitted_at__gt=exam.end_time,
            submitted_at__lte=exam.late_submission_end
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'totalRegistered': total_registered,
                'present': present,
                'absent': absent,
                'attendanceRate': attendance_rate,
                'lateSubmissions': late_submissions
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question_analysis(request, exam_id):
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        
        # Get all submissions for this exam
        submissions = StudentExamResult.objects.filter(exam=exam)
        total_submissions = submissions.count()
        
        if total_submissions == 0:
            return Response({
                'success': True,
                'data': {
                    'totalQuestions': len(exam.questions),
                    'questionAnalysis': [],
                    'message': 'No submissions yet'
                }
            })

        # Analyze each question
        question_analysis = []
        for question in exam.questions:
            # Get all answers for this question
            answers = []
            for submission in submissions:
                if hasattr(submission, 'answers') and submission.answers:
                    answers.append(submission.answers.get(str(question['id']), ''))
            
            # Calculate statistics
            total_answers = len(answers)
            correct_answers = answers.count(question['correct_answer'])
            accuracy = round((correct_answers / total_answers) * 100, 2) if total_answers > 0 else 0
            
            # Count answer distribution
            answer_distribution = {}
            for answer in answers:
                answer_distribution[answer] = answer_distribution.get(answer, 0) + 1
            
            # Sort by frequency
            common_wrong_answers = sorted(
                [(ans, count) for ans, count in answer_distribution.items() if ans != question['correct_answer']],
                key=lambda x: x[1],
                reverse=True
            )[:3]  # Top 3 wrong answers
            
            question_analysis.append({
                'questionId': question['id'],
                'questionText': question['text'],
                'totalAnswers': total_answers,
                'correctAnswers': correct_answers,
                'accuracy': accuracy,
                'commonWrongAnswers': [
                    {'answer': ans, 'count': count} 
                    for ans, count in common_wrong_answers
                ],
                'correctAnswer': question['correct_answer']
            })

        return Response({
            'success': True,
            'data': {
                'totalQuestions': len(exam.questions),
                'questionAnalysis': question_analysis
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request, report_type):
    try:
        if report_type == 'performance':
            return get_performance_report(request)
        elif report_type == 'attendance':
            exam_id = request.GET.get('exam_id')
            if not exam_id:
                return Response({
                    'success': False,
                    'message': 'Exam ID is required for attendance report'
                }, status=400)
            return get_attendance_report(request, exam_id)
        elif report_type == 'question-analysis':
            exam_id = request.GET.get('exam_id')
            if not exam_id:
                return Response({
                    'success': False,
                    'message': 'Exam ID is required for question analysis'
                }, status=400)
            return get_question_analysis(request, exam_id)
        else:
            return Response({
                'success': False,
                'message': f'Invalid report type: {report_type}'
            }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

    