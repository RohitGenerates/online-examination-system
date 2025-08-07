from django.urls import path
from . import views
from .views import start_exam_attempt

# Split URL patterns into views and API endpoints
view_patterns = [
    # View endpoints (under /exams/)
    path('create/<int:exam_id>/', views.create_exam, name='create_exam_with_id'),  # Load question editor
    path('take/<int:exam_id>/', views.take_exam_page, name='take_exam_page'),  # Student-facing HTML page
    path('results/', views.view_results, name='view-results'),
    path('manage/<int:exam_id>/', views.add_questions_view, name='manage_exam'),  # Manage existing exam
]
# Do not define urlpatterns here. Only export view_patterns for use in project urls.py.

# API URLs
urlpatterns = [
    path('api/exams/<int:exam_id>/take/', views.take_exam, name='take_exam_api'),
    path('api/exams/<int:exam_id>/submit/', views.submit_exam, name='submit_exam_api'),
    path('api/start_attempt/<int:exam_id>/', start_exam_attempt, name='start_exam_attempt'),
]