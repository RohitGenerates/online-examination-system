from django.contrib.auth.models import AbstractUser
from django.db import models
import json
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('frozen', 'Frozen'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    department = models.CharField(max_length=100, blank=True, null=True)
    semester = models.CharField(max_length=2, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Student specific fields
    student_marks = models.TextField(null=True, blank=True)  # Will store JSON string of exam_id: marks
    
    def set_student_marks(self, marks_dict):
        self.student_marks = json.dumps(marks_dict)
    
    def get_student_marks(self):
        if self.student_marks:
            return json.loads(self.student_marks)
        return {}
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    department = models.CharField(max_length=100, blank=True, null=True)
    semester = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.department} - Semester {self.semester}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.department}"