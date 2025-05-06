from django.core.management.base import BaseCommand
from accounts.models import User, Student, Teacher

class Command(BaseCommand):
    help = 'Deletes all users except superusers'

    def handle(self, *args, **options):
        # Delete all students and teachers first
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        
        # Delete all non-superuser users
        non_superusers = User.objects.filter(is_superuser=False)
        count = non_superusers.count()
        non_superusers.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} non-superuser users')) 