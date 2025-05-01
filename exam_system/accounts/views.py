from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

def root_view(request):
    return redirect('accounts:login')

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')
            
            if not all([username, email, password, role]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role.lower()  # Convert to lowercase to match our role field
            )
            
            if role.lower() == 'student':
                return JsonResponse({'redirect': '/accounts/student-details/'})
            elif role.lower() == 'teacher':
                return JsonResponse({'redirect': '/accounts/teacher-details/'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
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
            
            user = User.objects.get(username=username)
            user.department = department
            user.semester = semester
            user.status = 'active'
            user.save()
            
            return JsonResponse({'redirect': '/accounts/login/'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'accounts/student-details.html')

def teacher_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            subject = data.get('subject')
            
            user = User.objects.get(username=username)
            user.subject = subject
            user.status = 'active'
            user.save()
            
            return JsonResponse({'redirect': '/accounts/login/'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'accounts/teacher-details.html')

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            user_type = data.get('userType')
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.status == 'active':
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
                        'error': 'Your account is not active. Please contact admin.'
                    }, status=400)
            else:
                return JsonResponse({
                    'error': 'Invalid username or password.'
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
    user = request.user
    context = {'user': user}

    if user.role == 'admin':
        return render(request, 'accounts/admin-dashboard.html', context)
    elif user.role == 'teacher':
        return render(request, 'accounts/teacher-dashboard.html', context)
    elif user.role == 'student':
        return render(request, 'accounts/student-dashboard.html', context)

    return render(request, 'accounts/dashboard.html', context)

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
    return render(request, 'accounts/create_exam.html')

@login_required
def manage_exams(request):
    if request.user.role != 'teacher':
        raise PermissionDenied
    return render(request, 'accounts/manage_exams.html')

@login_required
def view_results(request):
    if request.user.role != 'teacher':
        raise PermissionDenied
    return render(request, 'accounts/view_results.html')

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
    return render(request, 'accounts/take_exam.html')

@login_required
def view_student_results(request):
    if request.user.role != 'student':
        raise PermissionDenied
    return render(request, 'accounts/view_student_results.html')

# Placeholder views for future implementation
@login_required
def placeholder_view(request):
    messages.info(request, 'This feature is coming soon!')
    return redirect('accounts:dashboard')