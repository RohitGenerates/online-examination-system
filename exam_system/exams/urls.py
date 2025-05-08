from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # path('', views.exam_list, name='exam-list'),
    path('create/', views.create_exam, name='create-exam'),
    path('take/<int:exam_id>/', views.take_exam, name='take-exam'),
    path('results/', views.view_results, name='view-results'),
    # API endpoints
    path('subjects/', views.list_subjects, name='list_subjects'),
    path('exams/', views.list_exams, name='list_exams'),
    path('student-results/', views.api_student_results, name='student_results'),

    path('reports/<str:report_type>/', views.generate_report, name='generate_report'),
    path('performance-report/', views.get_performance_report, name='performance-report'),
    path('attendance-report/<int:exam_id>/', views.get_attendance_report, name='attendance-report'),
    path('question-analysis/<int:exam_id>/', views.get_question_analysis, name='question-analysis'),
]