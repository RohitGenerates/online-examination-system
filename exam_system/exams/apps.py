# exams/apps.py
from django.apps import AppConfig

class ExamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exams'
    
    def ready(self):
        """
        Called when the application is ready.
        This is where we ensure departments exist and update student/teacher departments.
        """
        # Import here to avoid circular imports
        from exams.models import Department
        
        # First ensure departments exist
        Department.ensure_departments()
        
        # Then update student and teacher departments
        # We need to import these after departments are created
        from accounts.models import Student, Teacher
        
        # Update existing student and teacher departments
        Student.update_departments_from_username()
        Teacher.update_departments_from_username()

# accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'