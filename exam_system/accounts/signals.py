from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, Student, Teacher
from django.db import connection
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create Student or Teacher profile after User is created."""
    if not created:
        return

    # Import Department here to avoid circular import issues
    from exams.models import Department

    # Skip if role is not specified or is admin
    if instance.role not in ['student', 'teacher']:
        logger.info(f"Skipped profile creation for user {instance.username} with role {instance.role}")
        return

    # Skip admin users or if username is malformed
    if instance.username.startswith('admin') or len(instance.username) < 7:
        logger.info(f"Skipped profile creation for admin or invalid username: {instance.username}")
        return

    # Extract department code (e.g., cs, is, ml, etc.)
    dept_code = instance.username[5:7].lower()
    
    try:
        # Ensure the department exists
        department, created = Department.objects.get_or_create(
            code=dept_code, 
            defaults={'name': f'{dept_code.upper()} Department'}
        )
        
        if created:
            logger.info(f"Created new department: {department}")

        # Create profile based on role
        if instance.role == 'student':
            semester = int(instance.username[0]) if instance.username[0] in '12345678' else 1
            Student.objects.create(
                user=instance,
                department=department,
                semester=semester
            )
            logger.info(f"Created student profile for {instance.username}")
        
        elif instance.role == 'teacher':
            Teacher.objects.create(
                user=instance,
                department=department
            )
            logger.info(f"Created teacher profile for {instance.username}")
    
    except Exception as e:
        logger.error(f"Error creating profile for {instance.username}: {str(e)}")