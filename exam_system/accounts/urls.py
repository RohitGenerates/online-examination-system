from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Basic authentication URLs
    path('', views.root_view, name='root'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('get-csrf/', views.get_csrf, name='get_csrf'),
    
    # Exam related URLs
    path('create-exam/', views.create_exam, name='create-exam'),
    path('manage-exams/', views.manage_exams, name='manage-exams'),
    path('view-results/', views.view_results, name='view_results'),
    path('take-exam/', views.take_exam, name='take-exam'),
    path('view-student-results/', views.view_student_results, name='view_student_results'),
]