from django.db import models
from accounts.models import User, Student, Teacher

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
    department = models.CharField(max_length=100)  # Which department this exam is for
    semester = models.CharField(max_length=2)      # Which semester students can take this
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    passing_score = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    questions = models.JSONField()  # Store question IDs as JSON array

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