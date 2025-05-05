from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Student, Teacher
from exams.models import Exam, StudentExamResult
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
import os
from django.urls import reverse

def root_view(request):
    return redirect('accounts:login')

@ensure_csrf_cookie
def signup(request):
    if request.method == 'GET':
        return render(request, 'accounts/signup.html')
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('username')  # This will be the college ID or admin ID
            email = data.get('email')
            password = data.get('password')
            semester = data.get('semester')
            
            if not all([user_id, email, password]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            # Validate ID format
            is_admin = user_id.startswith('admin')
            is_student_id = (
                user_id[0] in '12345678' and
                user_id[1:5] == 'mp23' and
                user_id[5:7] in ['cg', 'cs', 'is', 'ml', 'ds']
            )
            is_teacher_id = (
                user_id[0] == '0' and
                user_id[1:5] == 'mp23' and
                user_id[5:7] in ['cg', 'cs', 'is', 'ml', 'ds']
            )
            
            if not (is_admin or is_student_id or is_teacher_id):
                return JsonResponse({'error': 'Invalid ID format'}, status=400)
            
            if User.objects.filter(username=user_id).exists():
                return JsonResponse({'error': 'ID already exists'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=user_id,
                email=email,
                password=password,
                status='active'
            )
            
            # Create appropriate profile based on ID
            if is_admin:
                # Admin users don't need additional profiles
                pass
            elif is_student_id:
                dept_code = user_id[5:7]
                department = dict(User.DEPARTMENT_CHOICES)[dept_code]
                if not semester:
                    return JsonResponse({'error': 'Semester is required for students'}, status=400)
                Student.objects.create(
                    user=user,
                    department=department,
                    semester=semester
                )
            elif is_teacher_id:
                dept_code = user_id[5:7]
                department = dict(User.DEPARTMENT_CHOICES)[dept_code]
                Teacher.objects.create(
                    user=user,
                    department=department
                )
            
            return JsonResponse({'message': 'User created successfully'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'accounts/signup.html')

def student_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            department = data.get('department')
            semester = data.get('semester')
            
            if not all([username, department, semester]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            user = User.objects.get(username=username)
            user.department = department
            user.semester = semester
            user.save()
            
            return JsonResponse({'redirect': '/accounts/login/'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'accounts/student-details.html')

def teacher_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            department = data.get('department')
            subject = data.get('subject')
            
            if not all([username, department, subject]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            user = User.objects.get(username=username)
            user.department = department
            user.subject = subject
            user.save()
            
            return JsonResponse({'redirect': '/accounts/login/'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'accounts/teacher-details.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('userType')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Determine redirect URL based on user type
            if user_type == 'student':
                redirect_url = reverse('accounts:student_dashboard')
            elif user_type == 'teacher':
                redirect_url = reverse('accounts:teacher_dashboard')
            elif user_type == 'admin':
                redirect_url = reverse('accounts:admin_dashboard')
            else:
                redirect_url = reverse('accounts:dashboard')
            
            # If AJAX, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
                return JsonResponse({'success': True, 'redirect': redirect_url})
            # Otherwise, do a normal redirect
            return HttpResponseRedirect(redirect_url)
        else:
            error_msg = 'Invalid username or password'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return render(request, 'accounts/login.html')
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'student_profile'):
        raise PermissionDenied
    
    student = request.user.student_profile
    available_exams = Exam.objects.filter(
        department=student.department,
        semester=student.semester,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    )
    
    results = StudentExamResult.objects.filter(student=student)
    return render(request, 'accounts/student_dashboard.html', {
        'student': student,
        'available_exams': available_exams,
        'results': results
    })

@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher_profile'):
        raise PermissionDenied
    
    teacher = request.user.teacher_profile
    created_exams = Exam.objects.filter(created_by=teacher)
    results = StudentExamResult.objects.filter(exam__in=created_exams)
    return render(request, 'accounts/teacher_dashboard.html', {
        'teacher': teacher,
        'exams': created_exams,
        'results': results
    })

@login_required
def admin_dashboard(request):
    if not request.user.username.startswith('admin'):
        raise PermissionDenied
    
    return render(request, 'accounts/admin_dashboard.html', {
        'user': request.user
    })

@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    if hasattr(request.user, 'student_profile'):
        return redirect('accounts:student_dashboard')
    elif hasattr(request.user, 'teacher_profile'):
        return redirect('accounts:teacher_dashboard')
    elif request.user.username.startswith('admin'):
        return redirect('accounts:admin_dashboard')
    else:
        raise PermissionDenied

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')

# Admin Views
@login_required
def manage_users(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    users = User.objects.all()
    return render(request, 'accounts/manage_users.html', {'users': users})

@login_required
def system_settings(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    return render(request, 'accounts/system_settings.html')

@login_required
def system_logs(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    return render(request, 'accounts/system_logs.html')

# Teacher Views
@login_required
def create_exam(request):
    if request.user.role != 'teacher':
        raise PermissionDenied
    
    if request.method == 'POST':
        try:
            exam_name = request.POST.get('exam_name')
            subject = request.POST.get('subject')
            department = request.POST.get('department')
            semester = request.POST.get('semester')
            duration = request.POST.get('duration')
            total_marks = request.POST.get('total_marks')
            passing_marks = request.POST.get('passing_marks')
            exam_date = request.POST.get('exam_date')
            
            if not all([exam_name, subject, department, semester, duration, total_marks, passing_marks, exam_date]):
                messages.error(request, 'All fields are required')
                return redirect('accounts:create-exam')
            
            # Create the exam
            exam = Exam.objects.create(
                name=exam_name,
                subject=subject,
                department=department,
                semester=semester,
                duration=duration,
                total_marks=total_marks,
                passing_marks=passing_marks,
                exam_date=exam_date,
                created_by=request.user
            )
            
            messages.success(request, 'Exam created successfully!')
            return redirect('accounts:manage-exams')
            
        except Exception as e:
            messages.error(request, f'Error creating exam: {str(e)}')
            return redirect('accounts:create-exam')
    
    return render(request, 'accounts/create_exam.html')

@login_required
def manage_exams(request):
    if request.user.role != 'teacher':
        raise PermissionDenied
    
    # Get exams created by the current teacher
    exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'accounts/manage_exams.html', {'exams': exams, 'now': timezone.now()})

@login_required
def view_results(request):
    if request.user.role != 'teacher':
        raise PermissionDenied
    
    # Get exams created by the current teacher
    exams = Exam.objects.filter(created_by=request.user)
    results = []
    
    for exam in exams:
        exam_results = StudentExamResult.objects.filter(exam=exam)
        if exam_results.exists():
            results.extend(exam_results)
    
    return render(request, 'accounts/view_results.html', {'results': results})

@login_required
def generate_reports(request):
    if request.user.role != 'teacher':
        raise PermissionDenied
    return render(request, 'accounts/generate_reports.html')

# Student Views
@login_required
def take_exam(request):
    if request.user.role != 'student':
        raise PermissionDenied
    
    try:
        # Get student's profile
        student = Student.objects.get(user=request.user)
        
        # Get available exams for the student's department and semester
        exams = Exam.objects.filter(
            department=student.department,
            semester=student.semester,
            exam_date__gt=timezone.now()
        ).exclude(
            id__in=StudentExamResult.objects.filter(student=student).values_list('exam_id', flat=True)
        )
        
        return render(request, 'accounts/take_exam.html', {'exams': exams})
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('accounts:dashboard')

@login_required
def view_student_results(request, student_id):
    if not hasattr(request.user, 'teacher_profile'):
        raise PermissionDenied
    
    try:
        student = Student.objects.get(id=student_id)
        if student.department != request.user.teacher_profile.department:
            raise PermissionDenied
            
        results = StudentExamResult.objects.filter(student=student)
        return render(request, 'accounts/view_student_results.html', {
            'student': student,
            'results': results
        })
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

# Placeholder views for future implementation
@login_required
def placeholder_view(request):
    messages.info(request, 'This feature is coming soon!')
    return redirect('accounts:dashboard')

def get_csrf(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})