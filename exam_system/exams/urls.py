from django.urls import path
from . import views

# This will be overridden by the namespace in the main urls.py
app_name = 'exams'

urlpatterns = [
    # View endpoints (under /exams/)
    path('create/<int:exam_id>/', views.create_exam, name='create_exam_with_id'),  # Load question editor
    path('take/<int:exam_id>/', views.take_exam, name='take-exam'),
    path('results/', views.view_results, name='view-results'),
    
    # API endpoints (under /api/exams/)
    path('create/', views.create_exam, name='create_exam'),  # Create exam with basic info
    path('<int:exam_id>/', views.get_exam, name='get_exam'),  # Get exam details
    path('<int:exam_id>/questions/', views.add_questions, name='add_questions'),  # Add questions to exam
    path('available/', views.get_available_exams, name='available_exams'),
    path('subjects/', views.list_subjects, name='list_subjects'),
    path('list/', views.list_exams, name='list_exams'),
    path('student-results/', views.api_student_results, name='student_results'),
    path('reports/<str:report_type>/', views.generate_report, name='generate_report'),
    path('performance-report/', views.get_performance_report, name='performance-report'),
    path('attendance-report/<int:exam_id>/', views.get_attendance_report, name='attendance-report'),
    path('question-analysis/<int:exam_id>/', views.get_question_analysis, name='question-analysis'),
]