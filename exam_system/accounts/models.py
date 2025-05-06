from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('frozen', 'Frozen'),
    )
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
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
        max_length=30,
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
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')  # Default to student
    phone_number = models.CharField(max_length=15, blank=True)

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

    # Override the save method to ensure role is set based on ID format
    def user_save(self, *args, **kwargs):
        # Set role based on ID format if not explicitly set
        if not self.role or self.role not in [choice[0] for choice in self.ROLE_CHOICES]:
            role_from_id = self.get_role_from_id()
            if role_from_id:
                self.role = role_from_id
        # If this is a new user, ensure department is set
        if not self.pk:
            department = self.get_department_from_id()
        super(type(self), self).save(*args, **kwargs)

    # Add this method to your User model
    save = user_save

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    department = models.CharField(max_length=100)
    semester = models.CharField(max_length=2)
    
    def __str__(self):
        return f"{self.user.username} - {self.department} - Semester {self.semester}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username} - {self.department}"

# Signal handler to create student/teacher profiles
def create_user_profile(sender, instance, created, **kwargs):
    """Create corresponding profile when user is created"""
    if created:
        # Get department from ID
        department = instance.get_department_from_id()
        if instance.role == 'student':
            # Create student profile - extract semester from ID or set default
            semester = '1'  # Default semester
            Student.objects.create(user=instance, department=department, semester=semester)
        elif instance.role == 'teacher':
            # Create teacher profile
            Teacher.objects.create(user=instance, department=department)

# Connect the signal
post_save.connect(create_user_profile, sender=User)