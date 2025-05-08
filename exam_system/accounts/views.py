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
from django.db import transaction
import os
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from datetime import datetime, timedelta
from django.db.models import Q

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
            department = data.get('department')  # Get department from request
            
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
            
            # Get department from ID if not provided
            if not department and not is_admin:
                dept_code = user_id[5:7]
                department = dict(User.DEPARTMENT_CHOICES)[dept_code]
            
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=user_id,
                    email=email,
                    password=password,
                    status='active',
                    role='admin' if is_admin else 'student' if is_student_id else 'teacher'
                )
                # Do NOT manually create Student or Teacher profile here; let the post_save signal handle it
                if is_student_id and not semester:
                    raise ValueError('Semester is required for students')
            
            return JsonResponse({
                'message': 'User created successfully',
                'redirect': '/accounts/login/'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
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
        
        # Debug output to help diagnose issues
        print(f"Login attempt - Username: {username}, User Type: {user_type}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if the user account is active
            if not user.is_active:
                error_msg = 'Your account is disabled. Please contact support.'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
                    return JsonResponse({'success': False, 'error': error_msg}, status=403)
                messages.error(request, error_msg)
                return render(request, 'accounts/login.html')
            
            # Get user's actual role based on the model structure and ID format
            actual_role = user.role  # Use the role field from the User model
            
            # Convert user_type to lowercase for comparison, or use a default value
            selected_type = user_type.lower() if user_type else ''
            
            print(f"User roles - Model role: {actual_role}, Selected role: {selected_type}")
            print(f"Profile checks - Has student profile: {hasattr(user, 'student_profile')}, Has teacher profile: {hasattr(user, 'teacher_profile')}")
            
            # Check if the selected type matches the user's actual type
            type_matches = (selected_type == actual_role)
            
            if not type_matches:
                error_msg = 'Invalid user type selected'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json':
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
                return render(request, 'accounts/login.html')
            
            login(request, user)
            
            # Determine redirect URL based on user type
            if actual_role == 'admin':
                redirect_url = reverse('accounts:admin_dashboard')
            elif actual_role == 'student':
                redirect_url = reverse('accounts:student_dashboard')
            elif actual_role == 'teacher':
                redirect_url = reverse('accounts:teacher_dashboard')
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
        messages.error(request, 'You do not have permission to access the student dashboard')
        return redirect('accounts:dashboard')
    
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
        messages.error(request, 'You do not have permission to access the teacher dashboard')
        return redirect('accounts:dashboard')
    
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
        messages.error(request, 'You do not have permission to access the admin dashboard')
        return redirect('accounts:dashboard')
    
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
        messages.error(request, 'Invalid user type')
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

# Admin Views
@login_required
def manage_users(request):
    if not request.user.username.startswith('admin'):
        raise PermissionDenied
    users = User.objects.all()
    return render(request, 'accounts/manage_users.html', {'users': users})

@login_required
def system_settings(request):
    if not request.user.username.startswith('admin'):
        raise PermissionDenied
    return render(request, 'accounts/system_settings.html')

@login_required
def system_logs(request):
    if not request.user.username.startswith('admin'):
        raise PermissionDenied
    return render(request, 'accounts/system_logs.html')

# Student Views
@login_required
def take_exam(request):
    if not hasattr(request.user, 'student_profile'):
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

# Create Exam Endpoint
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):
    try:
        data = request.data
        # Validate required fields
        required_fields = ['title', 'subject', 'duration', 'deadline', 'totalQuestions']
        for field in required_fields:
            if field not in data:
                return Response({'success': False, 'message': f'Missing required field: {field}'}, status=400)

        # Create exam
        exam = Exam.objects.create(
            title=data['title'],
            subject_id=data['subject'],
            duration=data['duration'],
            deadline=data['deadline'],
            total_questions=data['totalQuestions'],
            created_by=request.user,
            status='draft'
        )

        return Response({
            'success': True,
            'message': 'Exam created successfully',
            'data': {
                'exam_id': exam.id,
                'title': exam.title
            }
        })
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)

# Manage Exams Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exams(request):
    try:
        # Get all exams created by the teacher
        exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')
        serializer = ExamSerializer(exams, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)

# View Student Results Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_results(request):
    try:
        # Get filter parameters
        exam_filter = request.GET.get('filter', '')
        
        # Base queryset
        results = StudentResult.objects.filter(exam__created_by=request.user)
        
        # Apply filters
        if exam_filter == 'recent':
            # Get results from last 7 days
            recent_date = datetime.now() - timedelta(days=7)
            results = results.filter(created_at__gte=recent_date)
        
        serializer = StudentResultSerializer(results, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)

# Generate Reports Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request, report_type):
    try:
        if report_type == 'performance':
            # Performance report - average scores by exam
            performance_data = StudentResult.objects.filter(
                exam__created_by=request.user
            ).values('exam__title').annotate(
                avg_score=Avg('score'),
                total_students=Count('student')
            )
            
            return Response({
                'success': True,
                'data': list(performance_data)
            })
            
        elif report_type == 'attendance':
            # Attendance report - number of students who took each exam
            attendance_data = StudentResult.objects.filter(
                exam__created_by=request.user
            ).values('exam__title').annotate(
                total_participants=Count('student')
            )
            
            return Response({
                'success': True,
                'data': list(attendance_data)
            })
            
        elif report_type == 'analysis':
            # Question analysis - performance by question
            analysis_data = StudentResult.objects.filter(
                exam__created_by=request.user
            ).values(
                'exam__title',
                'question__text'
            ).annotate(
                correct_answers=Count('is_correct', filter=Q(is_correct=True)),
                total_attempts=Count('is_correct')
            )
            
            return Response({
                'success': True,
                'data': list(analysis_data)
            })
            
        else:
            return Response({
                'success': False,
                'message': 'Invalid report type'
            }, status=400)
            
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)

@api_view(['GET', 'POST' , 'PUT'])
@permission_classes([IsAuthenticated])
def update_student_profile(request):
    if not hasattr(request.user, 'student_profile'):
        return Response({'success': False, 'message': 'Not a student account'}, status=403)
    
    if request.method == 'GET':
        # Return current profile data
        student = request.user.student_profile
        return Response({
            'success': True,
            'data': {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone_number': request.user.phone_number,
                'department': student.department,
                'semester': student.semester,
                'username': request.user.username
            }
        })
    
    elif request.method in ['POST' , 'PUT']:
        try:
            if request.method == 'PUT':
                data = json.loads(request.body)
            else:
                data = request.data

            user = request.user
            student = user.student_profile
            
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone_number' in data:
                user.phone_number = data['phone_number']
            
            # Update student profile fields
            if 'department' in data:
                student.department = data['department']
            if 'semester' in data:
                student.semester = data['semester']
            
            # Save both models
            user.save()
            student.save()
            
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'department': student.department,
                    'semester': student.semester,
                    'username': user.username
                }
            })
        except Exception as e:
            print(f"Error updating student profile: {str(e)}")  # Debug log
            return Response({'success': False, 'message': str(e)}, status=500)

@api_view(['GET', 'POST' , 'PUT'])
@permission_classes([IsAuthenticated])
def update_teacher_profile(request):
    if not hasattr(request.user, 'teacher_profile'):
        return Response({'success': False, 'message': 'Not a teacher account'}, status=403)
    
    if request.method == 'GET':
        teacher = request.user.teacher_profile
        return Response({
            'success': True,
            'data': {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone_number': request.user.phone_number,
                'department': teacher.department,
                'username': request.user.username
            }
        })
    
    elif request.method == 'POST':
        try:
            if request.method == 'PUT':
                data = json.loads(request.body)
            else:
                data = request.data

            user = request.user
            teacher = user.teacher_profile
            
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone_number' in data:
                user.phone_number = data['phone_number']
            
            # Update teacher profile fields
            if 'department' in data:
                teacher.department = data['department']
            
            # Save both models
            user.save()
            teacher.save()
            
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'department': teacher.department,
                    'username': user.username
                }
            })
        except Exception as e:
            print(f"Error updating teacher profile: {str(e)}")  # Debug log
            return Response({'success': False, 'message': str(e)}, status=500)