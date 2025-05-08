from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Basic authentication URLs
    path('', views.root_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('get-csrf/', views.get_csrf, name='get_csrf'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('api/student/profile/', views.student_profile, name='student_profile'),
    path('api/teacher/profile/', views.teacher_profile, name='teacher_profile'),
    
    # Student Views
    path('take-exam/', views.take_exam, name='take-exam'),
    path('student-results/<int:student_id>/', views.view_student_results, name='view_student_results'),
    
    # Teacher Dashboard API endpoints
    path('api/exams/create/', views.create_exam, name='create_exam'),
    path('api/exams/', views.list_exams, name='list_exams'),
    path('api/student-results/', views.student_results, name='student_results'),
    path('api/reports/<str:report_type>/', views.generate_report, name='generate_report'),
]