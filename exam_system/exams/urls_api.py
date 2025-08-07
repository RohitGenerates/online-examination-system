from django.urls import path
from . import views

api_patterns = [
    # API endpoints (will be mounted under /api/exams/)
    path('create/', views.create_exam, name='create_exam'),  # Create new exam
    path('subjects/', views.list_subjects, name='list_subjects'),  # Will be accessible at /api/exams/subjects/
    path('list/', views.list_exams, name='list_exams'),
    path('<int:exam_id>/questions/', views.get_exam_questions, name='get_exam_questions'),  # GET only
    path('<int:exam_id>/', views.get_exam, name='get_exam'),
    path('<int:exam_id>/add-questions/', views.add_questions, name='add_questions'),  # POST only
    path('<int:exam_id>/attendance/', views.get_attendance_report, name='get_attendance_report'),
    path('<int:exam_id>/question-analysis/', views.get_question_analysis, name='get_question_analysis'),
    path('performance-report/', views.get_performance_report, name='get_performance_report'),
    # Student-specific API endpoints
    path('<int:exam_id>/take/', views.take_exam, name='take_exam_api'),
    path('<int:exam_id>/submit/', views.submit_exam, name='submit_exam_api'),
    path('submit/', views.submit_exam, name='submit_exam'),
    path('available/', views.get_available_exams, name='get_available_exams'),
]

urlpatterns = api_patterns 