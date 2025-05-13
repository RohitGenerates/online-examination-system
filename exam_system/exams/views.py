from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import Exam, Question, StudentExamResult, ExamAttempt, Subject, Department
from accounts.models import User, Student, Teacher
from datetime import datetime, timedelta
import json
from .serializers import ExamSerializer
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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


    context = {'exams': exams, 'departments': Department.objects.all()}
    return render(request, 'exams/exam_list.html', context)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_exam(request, exam_id=None):
    """Handles both exam creation (POST) and the question editor view (GET)."""

    # Ensure the user is a teacher
    if not hasattr(request.user, 'teacher_profile'):
        return Response({'success': False, 'message': 'Not a teacher'}, status=403)

    teacher = request.user.teacher_profile

    if request.method == 'GET':
        # Render question editor for an existing exam
        if exam_id:
            try:
                exam = Exam.objects.get(id=exam_id, created_by=teacher)
                return render(request, 'exams/create_exam.html', {'exam': exam, 'departments': Department.objects.all()})
            except Exam.DoesNotExist:
                return Response({'success': False, 'message': 'Exam not found'}, status=404)
        else:
            return Response({'success': False, 'message': 'Exam ID is required for GET'}, status=400)

    elif request.method == 'POST':
        try:
            # Copy and prepare incoming data
            data = request.data.copy()

            # Validate required fields
            required_fields = ['title', 'subject', 'duration', 'deadline', 'totalQuestions', 'semester']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Ensure subject exists
            subject_id = data.get('subject')
            try:
                subject = Subject.objects.get(id=subject_id)
                # Add subject_id to data for the serializer
                data['subject_id'] = subject_id
            except Subject.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Subject with ID {subject_id} does not exist'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Parse and validate deadline
            try:
                deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
                late_submission_end = deadline + timedelta(days=2)
                data['start_time'] = deadline
                data['end_time'] = deadline
                data['late_submission_end'] = late_submission_end
            except ValueError as e:
                return Response({'success': False, 'message': f'Invalid deadline format: {str(e)}'}, status=400)

            # Add additional fields to data
            data['created_by'] = teacher.id
            data['department'] = teacher.department.id if teacher.department else None
            data['passing_score'] = 50  # default
            data['questions'] = []
            
            # Map totalQuestions to total_questions (snake_case for Django model)
            if 'totalQuestions' in data:
                data['total_questions'] = int(data['totalQuestions'])
            else:
                # Default to 5 questions if not specified
                data['total_questions'] = 5

            if not teacher.department:
                return Response({'success': False, 'message': 'Teacher has no department assigned'}, status=400)

            # Serialize and save
            serializer = ExamSerializer(data=data)
            if serializer.is_valid():
                # Save with created_by and other fields manually
                exam = serializer.save(
                    created_by=teacher,
                    department=teacher.department,
                    late_submission_end=late_submission_end,
                    total_questions=int(data.get('totalQuestions', 5))  # Explicitly set total_questions
                )
                
                return Response({
                    'success': True,
                    'message': 'Exam created successfully',
                    'data': {
                        'exam_id': exam.id
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            import traceback
            print(traceback.format_exc())  # Optional debug logging
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_exam_view(request):
    """View for rendering the initial exam creation form"""
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('login')
    return render(request, 'exams/create_exam.html')

def add_questions_view(request, exam_id):
    """View for rendering the questions form"""
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('login')
    
    try:
        exam = Exam.objects.get(id=exam_id, created_by=request.user.teacher_profile)
        return render(request, 'exams/add_questions.html', {'exam': exam})
    except Exam.DoesNotExist:
        messages.error(request, 'Exam not found')
        return redirect('teacher_dashboard')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_questions(request, exam_id):
    """API endpoint for adding questions to an exam"""
    if not hasattr(request.user, 'teacher_profile'):
        return Response({'success': False, 'message': 'Not a teacher'}, status=403)
    
    try:
        exam = Exam.objects.get(id=exam_id, created_by=request.user.teacher_profile)
        data = request.data
        
        # Validate questions data
        if 'questions' not in data:
            return Response({'success': False, 'message': 'No questions provided'}, status=400)
        
        # Update exam with questions
        exam.questions = data['questions']
        exam.save()
        
        return Response({
            'success': True,
            'message': 'Questions added successfully',
            'data': {
                'exam_id': exam.id,
                'total_questions': len(exam.questions)
            }
        })
    except Exam.DoesNotExist:
        return Response({'success': False, 'message': 'Exam not found'}, status=404)
    except Exception as e:
        print(f"Error adding questions: {str(e)}")  # Debug log
        return Response({'success': False, 'message': str(e)}, status=500)

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
            'subject': exam.subject.name,
            'department': exam.department.name,
            'department_id': exam.department.id,
            'duration': exam.duration,
            'totalQuestions': getattr(exam, 'total_questions', 0),
            'deadline': exam.end_time.isoformat() if exam.end_time else '',
        }
        for exam in exams
    ]
    return JsonResponse(exam_list, safe=False)

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
    """List all exams created by the teacher"""
    if not hasattr(request.user, 'teacher_profile'):
        return Response({'success': False, 'message': 'Not a teacher'}, status=403)
    
    teacher = request.user.teacher_profile
    exams = Exam.objects.filter(created_by=teacher).order_by('-created_at')
    
    # Format the response data manually to include all required fields
    exams_data = [{
        'id': exam.id,
        'title': exam.title,
        'subject': exam.subject.name,
        'subject_id': exam.subject.id,
        'department': exam.department.name,
        'department_id': exam.department.id,
        'semester': exam.semester,
        'duration': exam.duration,
        'totalQuestions': len(exam.questions) if hasattr(exam, 'questions') else 0,
        'deadline': exam.end_time.isoformat() if exam.end_time else None,
        'status': exam.status
    } for exam in exams]
    
    return Response({
        'success': True,
        'data': exams_data
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_exams(request):
    if not hasattr(request.user, 'student_profile'):
        return Response({'success': False, 'message': 'Not a student'}, status=403)
    
    try:
        student = request.user.student_profile
        exams = Exam.objects.filter(
            semester=student.semester,
            subject__department=student.department,
            status='active'
        ).exclude(
            id__in=ExamAttempt.objects.filter(
                student=student
            ).values_list('exam_id', flat=True)
        )
        exams_data = [{
            'id': exam.id,
            'title': exam.title,
            'subject': exam.subject.name,
            'department': exam.department.name,
            'department_id': exam.department.id,
            'duration': exam.duration,
            'total_questions': len(exam.questions),
            'deadline': exam.end_time.isoformat(),
            'remaining_time': (exam.end_time - timezone.now()).total_seconds() // 60  # in minutes
        } for exam in exams]
        
        return Response({
            'success': True,
            'data': exams_data
        })
        
    except Exception as e:
        print(f"Error fetching available exams: {str(e)}")  # Debug log
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_student_results(request):
    """Get student results - for both teachers and students"""
    if hasattr(request.user, 'teacher_profile'):
        # For teachers: get results of all students for their exams
        teacher = request.user.teacher_profile
        
        # Get all exams created by this teacher
        exams = Exam.objects.filter(created_by=teacher)
        
        # Get all results for these exams
        results = StudentExamResult.objects.filter(exam__in=exams)
        
        results_data = [
            {
                'id': result.id,
                'student': result.student.user.username,
                'student_id': result.student.id,
                'exam': result.exam.title,
                'exam_id': result.exam.id,
                'subject': result.exam.subject.name,
                'score': result.obtained_marks,
                'status': result.status,
                'date': result.submitted_at.isoformat()
            }
            for result in results
        ]
        
        return Response({
            'success': True,
            'data': results_data
        })
        
    elif hasattr(request.user, 'student_profile'):
        # For students: get only their own results
        student = request.user.student_profile
        results = StudentExamResult.objects.filter(student=student)
        
        results_data = [
            {
                'id': result.id,
                'exam': result.exam.title,
                'exam_id': result.exam.id,
                'subject': result.exam.subject.name,
                'score': result.obtained_marks,
                'status': result.status,
                'date': result.submitted_at.isoformat()
            }
            for result in results
        ]
        
        return Response({
            'success': True,
            'data': results_data
        })
    
    else:
        return Response({'success': False, 'message': 'Not authorized'}, status=403)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_exam(request, exam_id):
    """Get, update or delete exam details"""
    try:
        # Ensure the user is a teacher
        if not hasattr(request.user, 'teacher_profile'):
            return Response({'success': False, 'message': 'Not a teacher'}, status=403)
            
        teacher = request.user.teacher_profile
        exam = Exam.objects.get(id=exam_id, created_by=teacher)
        
        if request.method == 'GET':
            return Response({
                'success': True,
                'data': {
                    'id': exam.id,
                    'title': exam.title,
                    'subject': {
                        'id': exam.subject.id,
                        'name': exam.subject.name
                    },
                    'semester': exam.semester,
                    'duration': exam.duration,
                    'totalQuestions': exam.total_questions,
                    'questions': exam.questions
                }
            })
        
        elif request.method == 'PUT':
            data = request.data
            
            # Update basic exam details
            if 'title' in data:
                exam.title = data['title']
            if 'duration' in data:
                exam.duration = data['duration']
            if 'semester' in data:
                exam.semester = data['semester']
            if 'subject_id' in data:
                try:
                    subject = Subject.objects.get(id=data['subject_id'])
                    exam.subject = subject
                except Subject.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': f"Subject with ID {data['subject_id']} does not exist"
                    }, status=400)
            if 'deadline' in data:
                try:
                    deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
                    exam.end_time = deadline
                    exam.late_submission_end = deadline + timedelta(days=2)
                except ValueError as e:
                    return Response({'success': False, 'message': f'Invalid deadline format: {str(e)}'}, status=400)
            
            exam.save()
            
            return Response({
                'success': True,
                'message': 'Exam updated successfully',
                'data': {
                    'id': exam.id,
                    'title': exam.title,
                    'subject': {
                        'id': exam.subject.id,
                        'name': exam.subject.name
                    },
                    'semester': exam.semester,
                    'duration': exam.duration
                }
            })
        
        elif request.method == 'DELETE':
            # Check if there are any attempts for this exam
            attempts = ExamAttempt.objects.filter(exam=exam).count()
            if attempts > 0:
                return Response({
                    'success': False,
                    'message': f'Cannot delete exam with {attempts} student attempts'
                }, status=400)
                
            # Delete the exam
            exam_title = exam.title
            exam.delete()
            
            return Response({
                'success': True,
                'message': f'Exam "{exam_title}" deleted successfully'
            })
            
    except Exam.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Exam not found'
        }, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Debug logging
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)