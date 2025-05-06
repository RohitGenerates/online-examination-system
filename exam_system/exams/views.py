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

@login_required
def exam_list(request):
    user = request.user
    now = datetime.now()

    if user.role == 'teacher':
        exams = Exam.objects.filter(created_by=user)
    elif user.role == 'student':
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
    
    # Check if exam is currently available
    now = timezone.now()
    if now < exam.start_time or now > exam.end_time:
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
            
            # Create exam result
            status = 'pass' if obtained_marks >= exam.passing_score else 'fail'
            StudentExamResult.objects.create(
                student=student,
                exam=exam,
                obtained_marks=obtained_marks,
                status=status
            )
            
            return JsonResponse({
                'message': 'Exam submitted successfully',
                'score': obtained_marks,
                'total': total_marks,
                'status': status
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

    