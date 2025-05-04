from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Exam, Question, Subject, StudentExam, StudentAnswer
from accounts.models import User
from datetime import datetime, timedelta
import json

@login_required
def exam_list(request):
    user = request.user
    now = datetime.now()

    if user.role == 'teacher':
        exams = Exam.objects.filter(created_by=user)
    elif user.role == 'student':
        exams = Exam.objects.filter(
            is_published=True,
            start_time__lte=now,
            end_time__gte=now
        )
    else:  # admin
        exams = Exam.objects.all()

    context = {'exams': exams}
    return render(request, 'exams/exam_list.html', context)

@login_required
def create_exam(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can create exams.')
        return redirect('exams:exam_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        duration = request.POST.get('duration')
        passing_score = request.POST.get('passing_score')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        instructions = request.POST.get('instructions', '')

        try:
            subject = Subject.objects.get(id=subject_id)
            exam = Exam.objects.create(
                title=title,
                subject=subject,
                created_by=request.user,
                duration=duration,
                passing_score=passing_score,
                start_time=start_time,
                end_time=end_time,
                instructions=instructions
            )
            messages.success(request, 'Exam created successfully!')
            return redirect('exams:manage_exam', exam_id=exam.id)
        except Exception as e:
            messages.error(request, f'Error creating exam: {str(e)}')

    subjects = Subject.objects.all()
    return render(request, 'exams/create_exam.html', {'subjects': subjects})

@login_required
def manage_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = Question.objects.filter(subject=exam.subject)
    exam_questions = exam.examquestion_set.all().order_by('order')

    if request.method == 'POST':
        # Handle adding/removing questions
        if 'add_question' in request.POST:
            question_id = request.POST.get('question_id')
            order = request.POST.get('order')

            try:
                question = Question.objects.get(id=question_id)
                exam.questions.add(question, through_defaults={'order': order})
                messages.success(request, 'Question added to exam!')
            except Exception as e:
                messages.error(request, f'Error adding question: {str(e)}')

        elif 'remove_question' in request.POST:
            question_id = request.POST.get('question_id')
            try:
                exam.questions.remove(question_id)
                messages.success(request, 'Question removed from exam!')
            except Exception as e:
                messages.error(request, f'Error removing question: {str(e)}')

        elif 'publish_exam' in request.POST:
            exam.is_published = True
            exam.save()
            messages.success(request, 'Exam published successfully!')

        return redirect('exams:manage_exam', exam_id=exam.id)

    context = {
        'exam': exam,
        'questions': questions,
        'exam_questions': exam_questions,
    }
    return render(request, 'exams/manage_exam.html', context)

@login_required
def take_exam(request, exam_id):
    if request.user.role != 'student':
        messages.error(request, 'Only students can take exams.')
        return redirect('accounts:dashboard')

    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    now = datetime.now()

    if now < exam.start_time:
        messages.error(request, 'This exam has not started yet.')
        return redirect('exams:exam_list')

    if now > exam.end_time:
        messages.error(request, 'This exam has already ended.')
        return redirect('exams:exam_list')

    # Check if student already took this exam
    student_exam, created = StudentExam.objects.get_or_create(
        student=request.user,
        exam=exam,
        defaults={'start_time': now}
    )

    if not created and student_exam.is_completed:
        messages.error(request, 'You have already completed this exam.')
        return redirect('exams:exam_result', exam_id=exam.id)

    if request.method == 'POST':
        # Process exam submission
        score = 0
        total_questions = exam.questions.count()

        # Clear previous answers if any
        StudentAnswer.objects.filter(student_exam=student_exam).delete()

        # Process each question
        for question in exam.questions.all():
            answer_key = f'question_{question.id}'
            if answer_key in request.POST:
                answer = request.POST[answer_key]
                is_correct = (answer.lower() == question.correct_answer.lower())

                if is_correct:
                    score += question.marks

                StudentAnswer.objects.create(
                    student_exam=student_exam,
                    question=question,
                    answer=answer,
                    is_correct=is_correct
                )

        # Calculate percentage score
        total_marks = sum(q.marks for q in exam.questions.all())
        percentage_score = (score / total_marks) * 100 if total_marks > 0 else 0

        # Update student exam
        student_exam.end_time = datetime.now()
        student_exam.is_completed = True
        student_exam.score = percentage_score
        student_exam.save()

        messages.success(request, 'Exam submitted successfully!')
        return redirect('exams:exam_result', exam_id=exam.id)

    questions = exam.questions.order_by('examquestion__order')
    remaining_time = (student_exam.start_time + timedelta(minutes=exam.duration)) - now

    context = {
        'exam': exam,
        'questions': questions,
        'remaining_time': remaining_time.total_seconds(),
        'student_exam': student_exam,
    }
    return render(request, 'exams/take_exam.html', context)

@login_required
def exam_result(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user.role == 'student':
        student_exam = get_object_or_404(StudentExam, exam=exam, student=request.user)
        if not student_exam.is_completed:
            messages.error(request, 'You have not completed this exam yet.')
            return redirect('exams:take_exam', exam_id=exam.id)

        answers = StudentAnswer.objects.filter(student_exam=student_exam)
        context = {
            'exam': exam,
            'student_exam': student_exam,
            'answers': answers,
        }
        return render(request, 'exams/student_exam_result.html', context)

    elif request.user.role == 'teacher' and exam.created_by == request.user:
        student_exams = StudentExam.objects.filter(exam=exam, is_completed=True)
        context = {
            'exam': exam,
            'student_exams': student_exams,
        }
        return render(request, 'exams/teacher_exam_results.html', context)

    messages.error(request, 'You are not authorized to view these results.')
    return redirect('accounts:dashboard')

@csrf_exempt
@require_http_methods(["GET"])
def api_teacher_exams(request):
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized'
        }, status=401)

    try:
        exams = Exam.objects.filter(created_by=request.user)
        exam_data = [{
            'id': exam.id,
            'title': exam.title,
            'subject': exam.subject.name,
            'duration': exam.duration,
            'start_time': exam.start_time.isoformat(),
            'end_time': exam.end_time.isoformat(),
            'is_published': exam.is_published,
            'total_questions': exam.questions.count()
        } for exam in exams]

        return JsonResponse({
            'success': True,
            'data': exam_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_student_results(request):
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized'
        }, status=401)

    try:
        # Get all exams created by the teacher
        teacher_exams = Exam.objects.filter(created_by=request.user)
        
        # Get all completed student exams for these exams
        student_exams = StudentExam.objects.filter(
            exam__in=teacher_exams,
            is_completed=True
        ).select_related('student', 'exam')

        results_data = [{
            'student_name': se.student.get_full_name() or se.student.username,
            'exam_title': se.exam.title,
            'score': se.score,
            'date': se.end_time.isoformat(),
            'exam_id': se.exam.id,
            'student_id': se.student.id
        } for se in student_exams]

        return JsonResponse({
            'success': True,
            'data': results_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT"])
def api_teacher_profile(request):
    if not request.user.is_authenticated or request.user.role != 'teacher':
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized'
        }, status=401)

    try:
        if request.method == "GET":
            profile_data = {
                'name': request.user.get_full_name(),
                'email': request.user.email,
                'phone': request.user.phone_number,
                'department': request.user.department,
                'teacher_id': request.user.teacher_id
            }
            return JsonResponse({
                'success': True,
                'data': profile_data
            })
        
        elif request.method == "PUT":
            data = json.loads(request.body)
            
            # Update user profile
            if 'name' in data:
                request.user.first_name = data['name'].split()[0]
                request.user.last_name = ' '.join(data['name'].split()[1:]) if len(data['name'].split()) > 1 else ''
            
            if 'phone' in data:
                request.user.phone_number = data['phone']
            
            if 'department' in data:
                request.user.department = data['department']
            
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)