from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('exams', '0004_fix_department_data'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.department'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.department'),
        ),
    ] 