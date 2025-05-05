from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='exam-list'),
    path('create/', views.create_exam, name='create-exam'),
    path('take/<int:exam_id>/', views.take_exam, name='take-exam'),
    path('results/', views.view_results, name='view-results'),
]