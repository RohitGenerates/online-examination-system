from django.db import models
from accounts.models import User, Student, Teacher
from datetime import datetime, timedelta

class Question(models.Model):
    text = models.TextField()
    options = models.JSONField()  # Store options as JSON array
    correct_answer = models.CharField(max_length=1)  # a, b, c, d for MCQ; t/f for True/False
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.text[:50]}..."

class Exam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    semester = models.IntegerField()
    duration = models.IntegerField(help_text="Duration in minutes")
    passing_score = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    late_submission_end = models.DateTimeField(
        help_text="5 days after end_time for late submissions",
        default=datetime.now
    )
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    questions = models.JSONField()
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.late_submission_end:
            # Set late submission end to 5 days after end_time
            self.late_submission_end = self.end_time + timedelta(days=5)
        super().save(*args, **kwargs)

    def is_late_submission(self, submission_time):
        return self.end_time < submission_time <= self.late_submission_end

    def is_available(self, current_time):
        return self.start_time <= current_time <= self.late_submission_end

    def __str__(self):
        return self.title

class StudentExamResult(models.Model):
    STATUS_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    obtained_marks = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'exam')  # Prevent multiple attempts

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title} - {self.obtained_marks}"