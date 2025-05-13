from django.core.management.base import BaseCommand
from accounts.models import User, Student, Teacher
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix missing profile connections for users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Checking for users with missing profiles...'))
        
        # Get all users
        users = User.objects.all()
        fixed_count = 0
        error_count = 0
        
        for user in users:
            role = user.role
            user_id = user.username
            
            # Only process users that have role set but no profile
            if role == 'student' and not hasattr(user, 'student_profile'):
                self.stdout.write(f'Found student {user_id} without profile')
                try:
                    with transaction.atomic():
                        # Extract semester from ID if possible
                        semester = int(user_id[0]) if user_id[0] in '12345678' else 1
                        
                        # Get department if possible
                        try:
                            from exams.models import Department
                            dept_code = user_id[5:7] if len(user_id) > 6 else None
                            department = Department.objects.get(code=dept_code) if dept_code else None
                        except Exception:
                            department = None
                        
                        Student.objects.create(
                            user=user,
                            department=department,
                            semester=semester
                        )
                        fixed_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Created student profile for {user_id}'
                        ))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'Error creating student profile for {user_id}: {str(e)}'
                    ))
            
            elif role == 'teacher' and not hasattr(user, 'teacher_profile'):
                self.stdout.write(f'Found teacher {user_id} without profile')
                try:
                    with transaction.atomic():
                        # Get department if possible
                        try:
                            from exams.models import Department
                            dept_code = user_id[5:7] if len(user_id) > 6 else None
                            department = Department.objects.get(code=dept_code) if dept_code else None
                        except Exception:
                            department = None
                        
                        Teacher.objects.create(
                            user=user,
                            department=department
                        )
                        fixed_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Created teacher profile for {user_id}'
                        ))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'Error creating teacher profile for {user_id}: {str(e)}'
                    ))
        
        self.stdout.write(self.style.SUCCESS(
            f'Profile fix completed. Fixed: {fixed_count}, Errors: {error_count}'
        ))