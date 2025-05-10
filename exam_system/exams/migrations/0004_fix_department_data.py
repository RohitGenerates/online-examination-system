from django.db import migrations, models
import django.db.models.deletion

def create_departments(apps, schema_editor):
    Department = apps.get_model('exams', 'Department')
    
    # Create departments
    dept_mapping = {
        'cg': 'Computer Science Design',
        'cs': 'Computer Science Engineering',
        'is': 'Information Science Engineering',
        'ml': 'Artificial Intelligence & Machine Learning',
        'ds': 'Artificial Intelligence & Data Science'
    }
    
    for code, name in dept_mapping.items():
        Department.objects.get_or_create(
            name=name,
            code=code
        )

def update_student_departments(apps, schema_editor):
    Department = apps.get_model('exams', 'Department')
    Student = apps.get_model('accounts', 'Student')
    
    for student in Student.objects.all():
        dept_code = student.user.username[5:7]
        try:
            department = Department.objects.get(code=dept_code)
            student.department = department
            student.save()
        except Department.DoesNotExist:
            print(f"Department not found for code: {dept_code}")

def update_teacher_departments(apps, schema_editor):
    Department = apps.get_model('exams', 'Department')
    Teacher = apps.get_model('accounts', 'Teacher')
    
    for teacher in Teacher.objects.all():
        dept_code = teacher.user.username[5:7]
        try:
            department = Department.objects.get(code=dept_code)
            teacher.department = department
            teacher.save()
        except Department.DoesNotExist:
            print(f"Department not found for code: {dept_code}")

class Migration(migrations.Migration):
    dependencies = [
        ('exams', '0003_department_remove_exam_updated_at_exam_status_and_more'),
        ('accounts', '0001_initial'),  # Changed to use the initial migration
    ]

    operations = [
        # First create the departments
        migrations.RunPython(create_departments),
        
        # Then update the student departments
        migrations.RunPython(update_student_departments),
        
        # Finally update the teacher departments
        migrations.RunPython(update_teacher_departments),
    ] 