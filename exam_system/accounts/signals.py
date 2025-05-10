from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, Student, Teacher
from django.db import connection


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create Student or Teacher profile after User is created."""
    if not created or instance.role not in ['student', 'teacher']:
        return

    # Skip admin users or if username is malformed
    if instance.username.startswith('admin') or len(instance.username) < 7:
        return

    dept_code = instance.username[5:7]  # Extract department code (e.g., cs, is, ml, etc.)

    # Import Department here to avoid circular import issues
    from exams.models import Department

    # Check if 'exams_department' table exists (avoid issues during initial migrations)
    try:
        tables = connection.introspection.table_names()
        if 'exams_department' not in tables:
            print(f"[SKIPPED] Department table not found. User: {instance.username}")
            return
    except Exception as e:
        print(f"[ERROR] Checking department table failed: {e}")
        return

    try:
        department = Department.objects.get(code=dept_code)

        if instance.role == 'student':
            semester = int(instance.username[0])  # Assume semester is first character
            Student.objects.create(
                user=instance,
                department=department,
                semester=semester
            )
        elif instance.role == 'teacher':
            Teacher.objects.create(
                user=instance,
                department=department
            )
    except Department.DoesNotExist:
        print(f"[ERROR] Department not found for code: {dept_code}, user: {instance.username}")
    except Exception as e:
        print(f"[ERROR] Could not create profile for {instance.username}: {e}")
