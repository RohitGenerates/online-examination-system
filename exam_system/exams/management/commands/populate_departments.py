from django.core.management.base import BaseCommand
from exams.models import Department

class Command(BaseCommand):
    help = 'Populate departments in the database'

    def handle(self, *args, **kwargs):
        dept_mapping = {
            'cg': 'Computer Science Design',
            'cs': 'Computer Science Engineering',
            'is': 'Information Science Engineering',
            'ml': 'Artificial Intelligence & Machine Learning',
            'ds': 'Artificial Intelligence & Data Science'
        }
        
        for code, name in dept_mapping.items():
            Department.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated departments'))