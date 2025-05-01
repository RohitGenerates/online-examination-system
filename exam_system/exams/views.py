from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exam, Question, Subject, StudentExam, StudentAnswer
from accounts.models import User
from datetime import datetime, timedelta

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