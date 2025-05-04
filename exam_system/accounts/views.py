from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Student, Teacher
from exams.models import Exam, ExamResult, StudentExam
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
import json
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone

def root_view(request):
    return redirect('accounts:login')

@ensure_csrf_cookie
def signup(request):
    if request.method == 'GET':
        return render(request, 'accounts/signup.html')
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')
            department = data.get('department')
            semester = data.get('semester')
            
            if not all([username, email, password, role]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            # Create user with all fields
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role.lower(),
                status='active',
                department=department,
                semester=semester if role.lower() == 'student' else None
            )
            
            # Create appropriate profile based on role
            if role.lower() == 'student':
                if not all([department, semester]):
                    return JsonResponse({'error': 'Department and semester are required for students'}, status=400)
                Student.objects.create(
                    user=user,
                    department=department,
                    semester=semester
                )
            elif role.lower() == 'teacher':
                if not department:
                    return JsonResponse({'error': 'Department is required for teachers'}, status=400)
                Teacher.objects.create(
                    user=user,
                    department=department
                )
            
            # Redirect to login page after successful signup
            return JsonResponse({'redirect': '/accounts/login/'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    elif request.method == 'OPTIONS':
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response
        
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

def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username_or_email = data.get('username')
            password = data.get('password')
            user_type = data.get('userType')
            
            # Try to authenticate with username first
            user = authenticate(request, username=username_or_email, password=password)
            
            # If authentication fails, try with email
            if user is None:
                try:
                    user_with_email = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_with_email.username, password=password)
                except User.DoesNotExist:
                    pass

            if user is not None:
                if user.status == 'frozen':
                    return JsonResponse({
                        'error': 'Your account has been frozen. Please contact admin.'
                    }, status=400)
                
                if user.role.upper() != user_type:
                    return JsonResponse({
                        'error': f'Invalid login. You are registered as a {user.role}, not a {user_type}.'
                    }, status=400)
                
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': '/accounts/dashboard/',
                    'userType': user.role.upper()
                })
            else:
                return JsonResponse({
                    'error': 'Invalid username/email or password.'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)

    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def dashboard(request):
    if request.method == 'POST':
        # Handle profile update
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']
        
        if 'first_name' in request.POST:
            request.user.first_name = request.POST['first_name']
        
        if 'last_name' in request.POST:
            request.user.last_name = request.POST['last_name']
        
        if 'email' in request.POST:
            request.user.email = request.POST['email']
        
        if 'department' in request.POST:
            request.user.department = request.POST['department']
        
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:dashboard')

    if request.user.role == 'student':
        try:
            # Try to get existing student profile
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            # Check if required fields are set
            if not request.user.department or not request.user.semester:
                messages.error(request, 'Please complete your profile by setting your department and semester.')
                return render(request, 'accounts/student-dashboard.html', {
                    'student': None,
                    'available_exams': [],
                    'exam_results': [],
                    'average_score': None,
                    'show_profile_form': True
                })
            
            # Create new student profile if it doesn't exist
            student = Student.objects.create(
                user=request.user,
                department=request.user.department,
                semester=request.user.semester
            )
        
        # Get completed exam IDs
        completed_exam_ids = StudentExam.objects.filter(
            student=request.user,
            is_completed=True
        ).values_list('exam_id', flat=True)
        
        # Get available exams (published and not completed)
        available_exams = Exam.objects.filter(
            is_published=True,
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        ).exclude(id__in=completed_exam_ids)
        
        # Get completed exam results
        exam_results = StudentExam.objects.filter(
            student=request.user,
            is_completed=True
        ).select_related('exam')
        
        # Calculate average score
        average_score = None
        if exam_results.exists():
            total_score = sum(result.score for result in exam_results)
            average_score = total_score / exam_results.count()
        
        return render(request, 'accounts/student-dashboard.html', {
            'student': student,
            'available_exams': available_exams,
            'exam_results': exam_results,
            'average_score': average_score,
            'show_profile_form': False
        })
    elif request.user.role == 'teacher':
        try:
            # Try to get existing teacher profile
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            # Check if required fields are set
            if not request.user.department:
                messages.error(request, 'Please complete your profile by setting your department.')
                return render(request, 'accounts/teacher-dashboard.html', {
                    'teacher': None,
                    'created_exams': [],
                    'active_students_count': 0,
                    'completed_exams_count': 0,
                    'show_profile_form': True
                })
            
            # Create new teacher profile if it doesn't exist
            teacher = Teacher.objects.create(
                user=request.user,
                department=request.user.department
            )
        
        # Get teacher's created exams
        created_exams = Exam.objects.filter(created_by=request.user)
        
        # Get active students count (students who have taken at least one exam)
        active_students_count = StudentExam.objects.filter(
            exam__in=created_exams,
            is_completed=True
        ).values('student').distinct().count()
        
        # Get completed exams count
        completed_exams_count = StudentExam.objects.filter(
            exam__in=created_exams,
            is_completed=True
        ).count()
        
        return render(request, 'accounts/teacher-dashboard.html', {
            'teacher': teacher,
            'created_exams': created_exams,
            'active_students_count': active_students_count,
            'completed_exams_count': completed_exams_count,
            'show_profile_form': False
        })
    else:
        return redirect('accounts:login')

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

    return render(request, 'accounts/profile.html', {'user': request.user})

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
        exam_results = ExamResult.objects.filter(exam=exam)
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
            id__in=ExamResult.objects.filter(student=student).values_list('exam_id', flat=True)
        )
        
        return render(request, 'accounts/take_exam.html', {'exams': exams})
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('accounts:dashboard')

@login_required
def view_student_results(request):
    if request.user.role != 'student':
        raise PermissionDenied
    
    try:
        # Get student's profile
        student = Student.objects.get(user=request.user)
        
        # Get student's exam results
        results = ExamResult.objects.filter(student=student)
        
        return render(request, 'accounts/view_student_results.html', {'results': results})
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('accounts:dashboard')

# Placeholder views for future implementation
@login_required
def placeholder_view(request):
    messages.info(request, 'This feature is coming soon!')
    return redirect('accounts:dashboard')

def get_csrf(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})