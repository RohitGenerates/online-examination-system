from django.core.management.base import BaseCommand
from exams.models import Subject

class Command(BaseCommand):
    help = 'Populate subjects in the database'

    def handle(self, *args, **kwargs):
        subjects = [
            "Mathematics 1",
            "Mathematics 2",
            "Mathematics 3",
            "Physics",
            "Chemistry",
            "Python",
            "C",
            "Digital Design and Computer Organization",
            "Operating System",
            "Data Structure and Algorithms",
            "Analysis and Design of Algorithms",
            "Database Management System",
            "Data Science",
            "Java",
            "English",
            "Computer Graphics",
            "Artificial Intelligence",
            "Machine Learning",
            "Cyber Security",
            "Internet of Things"
        ]

        for subject_name in subjects:
            Subject.objects.get_or_create(name=subject_name)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated subjects'))