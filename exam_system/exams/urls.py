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
    
    # Teacher/Exam APIs
    path('api/exams/subjects/', views.list_subjects, name='list_subjects'),
    path('api/exams/<int:exam_id>/questions/', views.get_exam_questions, name='get_exam_questions'),
    path('api/exams/list/', views.list_exams, name='list_exams'),
    
    # Additional Teacher APIs
    path('api/exams/<int:exam_id>/', views.get_exam, name='get_exam'),
    path('api/exams/<int:exam_id>/add-questions/', views.add_questions, name='add_questions'),
    path('api/student/results/', views.api_student_results, name='api_student_results'),
    path('api/exams/<int:exam_id>/attendance/', views.get_attendance_report, name='get_attendance_report'),
    path('api/exams/<int:exam_id>/question-analysis/', views.get_question_analysis, name='get_question_analysis'),
    path('api/performance-report/', views.get_performance_report, name='get_performance_report'),
    
    # Student APIs
    path('api/exams/submit/', views.submit_exam, name='submit_exam'),
    path('api/exams/available/', views.get_available_exams, name='get_available_exams'),
]