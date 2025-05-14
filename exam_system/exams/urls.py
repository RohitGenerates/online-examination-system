from django.urls import path
from . import views

# This will be overridden by the namespace in the main urls.py
app_name = 'exams'

urlpatterns = [
    # View endpoints (under /exams/)
    path('create/<int:exam_id>/', views.create_exam, name='create_exam_with_id'),  # Load question editor
    path('take/<int:exam_id>/', views.take_exam, name='take-exam'),
    path('results/', views.view_results, name='view-results'),
    path('manage/<int:exam_id>/', views.add_questions_view, name='manage_exam'),  # Manage existing exam
    
    # Student Dashboard API endpoints
    path('api/student/exams', views.api_student_exams, name='api_student_exams'),
    path('api/student/results', views.api_student_results, name='api_student_results'),
    # (Profile API is in accounts/urls.py and does not need to be added here)

]