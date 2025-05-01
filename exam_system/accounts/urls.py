from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Basic authentication URLs
    path('', views.root_view, name='root'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('student-details/', views.student_details, name='student_details'),
    path('teacher-details/', views.teacher_details, name='teacher_details'),
    
    # Placeholder URLs for future features
    path('manage-users/', views.placeholder_view, name='manage_users'),
    path('system-settings/', views.placeholder_view, name='system_settings'),
    path('system-logs/', views.placeholder_view, name='system_logs'),
    path('create-exam/', views.placeholder_view, name='create-exam'),
    path('manage-exams/', views.placeholder_view, name='manage-exams'),
    path('view-results/', views.placeholder_view, name='view_results'),
    path('generate-reports/', views.placeholder_view, name='generate_reports'),
    path('take-exam/', views.placeholder_view, name='take-exam'),
    path('view-student-results/', views.placeholder_view, name='view_student_results'),
]