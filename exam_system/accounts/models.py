from django.contrib.auth.models import AbstractUser
from django.db import models
import json

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('frozen', 'Frozen'),
        ('pending', 'Pending'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Student specific fields
    department = models.CharField(max_length=100, null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    student_marks = models.TextField(null=True, blank=True)  # Will store JSON string of exam_id: marks
    
    # Teacher specific fields
    subject = models.CharField(max_length=100, null=True, blank=True)
    
    def set_student_marks(self, marks_dict):
        self.student_marks = json.dumps(marks_dict)
    
    def get_student_marks(self):
        if self.student_marks:
            return json.loads(self.student_marks)
        return {}
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"