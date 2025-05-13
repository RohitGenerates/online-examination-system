# In serializers.py
from rest_framework import serializers
from .models import Exam, Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class ExamSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), 
        source='subject', 
        write_only=True
    )

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject', 'subject_id', 'department', 'exam_type', 'total_marks', 'duration', 'total_questions']