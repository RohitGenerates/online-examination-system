from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('frozen', 'Frozen'),
    )
    
    DEPARTMENT_CHOICES = (
        ('cg', 'Computer Science Design'),
        ('cs', 'Computer Science Engineering'),
        ('is', 'Information Science Engineering'),
        ('ml', 'Artificial Intelligence & Machine Learning'),
        ('ds', 'Artificial Intelligence & Data Science'),
    )
    
    # Override username field to use college_id
    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^(admin\d{3}|[0-8]mp23(cg|cs|is|ml|ds)\d{3})$',
                message='Invalid ID format. Must be like: 1mp23cs001 for students, 0mp23cs001 for teachers, or admin001 for admin'
            )
        ],
        help_text='ID format: [0-8]mp23[dept_code][3 digits] for students/teachers, or admin[3 digits] for admin'
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return self.username
    
    def get_role_from_id(self):
        """Determine role based on ID format"""
        if self.username.startswith('admin'):
            return 'admin'
        elif self.username[0] in '12345678':
            return 'student'
        elif self.username[0] == '0':
            return 'teacher'
        return None
    
    def get_department_from_id(self):
        """Get department from ID"""
        if self.username.startswith('admin'):
            return 'Administration'
        dept_code = self.username[5:7]  # Extract department code (cg, cs, is, ml, ds)
        for code, name in self.DEPARTMENT_CHOICES:
            if code == dept_code:
                return name
        return None

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    semester = models.CharField(max_length=2)
    
    def __str__(self):
        return f"{self.user.username} - {self.department} - Semester {self.semester}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username} - {self.department}"