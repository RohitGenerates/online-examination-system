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
    
    # Profile URL
    path('profile/', views.profile, name='profile'),
    
    # Exam related URLs
    path('create-exam/', views.create_exam, name='create-exam'),
    path('manage-exams/', views.manage_exams, name='manage-exams'),
    path('view-results/', views.view_results, name='view_results'),
    path('take-exam/', views.take_exam, name='take-exam'),
    path('student-results/<int:student_id>/', views.view_student_results, name='view_student_results'),
]