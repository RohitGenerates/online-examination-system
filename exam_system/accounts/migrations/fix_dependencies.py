from django.db import migrations

class Migration(migrations.Migration):
    """
    This empty migration explicitly depends on exams.Department creation
    to ensure proper migration order.
    """
    dependencies = [
        ('accounts', '0001_initial'),
        ('exams', '0001_initial'),  # Make sure this matches your first exams migration
    ]

    operations = [
        # This is an empty migration that just fixes dependencies
    ]