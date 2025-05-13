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
    phone_number = models.CharField(max_length=15, blank=True, null=True)

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

    def save(self, *args, **kwargs):
        # Set role based on ID format if not explicitly set
        role_from_id = self.get_role_from_id()
        if role_from_id:
            print(f"[INFO] Setting role for {self.username} to {role_from_id} based on ID format")
            self.role = role_from_id
        else:
            print(f"[WARNING] Could not determine role from ID for {self.username}")
        
        # Call the original save method
        super().save(*args, **kwargs)
        print(f"[INFO] User {self.username} saved with role {self.role}")

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    # Use string reference to avoid circular imports during migrations
    department = models.ForeignKey('exams.Department', on_delete=models.CASCADE, null=True, blank=True)
    semester = models.IntegerField(choices=[(i, f'Semester {i}') for i in range(1, 9)])
    
    def __str__(self):
        return f"{self.user.username} - {self.department} - Semester {self.semester}"

    def get_available_exams(self):
        """Get exams available for this student"""
        # Import here to avoid circular imports
        from exams.models import Exam
        return Exam.objects.filter(
            department=self.department,
            semester=self.semester,
            status='active'
        ).exclude(
            studentexamresult__student=self
        )
    
    @classmethod
    def update_departments_from_username(cls):
        """
        Update student departments based on username pattern.
        Called in AppConfig.ready() to update departments for existing students.
        """
        # Import here to avoid circular imports
        from exams.models import Department
        
        for student in cls.objects.filter(department__isnull=True):
            # Assuming username format where position 5-7 contains department code
            if len(student.user.username) >= 7:
                dept_code = student.user.username[5:7]
                try:
                    department = Department.objects.get(code=dept_code)
                    student.department = department
                    # Also update semester from username if needed
                    if student.semester is None and student.user.username[0] in '12345678':
                        student.semester = int(student.user.username[0])
                    student.save()
                except Department.DoesNotExist:
                    print(f"Department not found for code: {dept_code}")

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', null=True, blank=True)
    # Use string reference to avoid circular imports during migrations
    department = models.ForeignKey('exams.Department', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.department}"
    
    @classmethod
    def update_departments_from_username(cls):
        """
        Update teacher departments based on username pattern.
        Called in AppConfig.ready() to update departments for existing teachers.
        """
        # Import here to avoid circular imports
        from exams.models import Department
        
        for teacher in cls.objects.filter(department__isnull=True):
            # Assuming username format where position 5-7 contains department code
            if len(teacher.user.username) >= 7:
                dept_code = teacher.user.username[5:7]
                try:
                    department = Department.objects.get(code=dept_code)
                    teacher.department = department
                    teacher.save()
                except Department.DoesNotExist:
                    print(f"Department not found for code: {dept_code}")

# Signal handlers are in signals.py