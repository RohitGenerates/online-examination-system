from django.db import models
from accounts.models import User, Student, Teacher
from datetime import datetime, timedelta
from django.utils import timezone

class Question(models.Model):
    text = models.TextField()
    options = models.JSONField()  # Will store all available options as a list
    correct_answer = models.CharField(max_length=1)  # a, b, c, etc. based on option index
    marks = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.text[:50]}..."

    def is_true_false(self):
        """Check if this is effectively a True/False question"""
        return len(self.options) == 2

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    @classmethod
    def ensure_departments(cls):
        """
        Ensure that all default departments exist
        Called in AppConfig.ready() to ensure departments exist
        """
        dept_mapping = {
            'cg': 'Computer Science Design',
            'cs': 'Computer Science Engineering',
            'is': 'Information Science Engineering',
            'ml': 'Artificial Intelligence & Machine Learning',
            'ds': 'Artificial Intelligence & Data Science'
        }
        
        for code, name in dept_mapping.items():
            cls.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Exam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=[(i, f'Semester {i}') for i in range(1, 9)])
    duration = models.IntegerField(help_text="Duration in minutes")
    passing_score = models.IntegerField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    late_submission_end = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    questions = models.ManyToManyField(Question)
    total_questions = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[   
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='draft'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.subject} - Semester {self.semester}"

    # @property
    # def total_questions(self):
    #     return self.questions.count()

    # @property
    # def total_marks(self):
    #     return sum(question.marks for question in self.questions.all())

    def is_available(self, current_time=None):
        """Check if exam is currently available"""
        current_time = current_time or timezone.now()
        return self.start_time <= current_time <= self.late_submission_end

    def is_late_submission(self, submission_time):
        """Check if submission is late"""
        return self.end_time < submission_time <= self.late_submission_end

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

class ExamAttempt(models.Model):
    STATUS_CHOICES = (
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('abandoned', 'Abandoned')
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    answers = models.JSONField(default=dict)  # Store student's answers
    is_late_submission = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser_info = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'exam')  # One attempt per exam per student
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title} - {self.status}"

    def calculate_duration(self):
        """Calculate actual duration of attempt"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return None

    def is_time_exceeded(self):
        """Check if attempt duration exceeds exam duration"""
        duration = self.calculate_duration()
        return duration and duration > self.exam.duration

    def submit(self):
        """Submit the exam attempt"""
        self.end_time = timezone.now()
        self.status = 'submitted'
        self.is_late_submission = self.exam.is_late_submission(self.end_time)
        self.save()

    def abandon(self):
        """Mark attempt as abandoned"""
        self.end_time = timezone.now()
        self.status = 'abandoned'
        self.save()

# dont know yet if to add this or not
# class ExamQuestion(models.Model):
#     exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ['order']
#         unique_together = ('exam', 'question')

#     def __str__(self):
#         return f"{self.exam.title} - Q{self.order}"