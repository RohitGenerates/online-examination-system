from rest_framework import serializers
from exams.models import Exam, StudentExamResult

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject', 'department', 'semester', 'duration', 
                 'passing_score', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['created_at']

class StudentExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    
    class Meta:
        model = StudentExamResult
        fields = ['id', 'student_name', 'exam_title', 'obtained_marks', 
                 'status', 'submitted_at', 'is_late_submission']
        read_only_fields = ['submitted_at'] 