from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('create/', views.create_exam, name='create_-xam'),
    path('manage/<int:exam_id>/', views.manage_exam, name='manage-exam'),
    path('take/<int:exam_id>/', views.take_exam, name='take-exam'),
    path('result/<int:exam_id>/', views.exam_result, name='exam-result'),
]