from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_remove_enrollment_course_enrollment_batch_and_more'),
        ('trainers', '0011_remove_livesession_batch_add_livesession_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollment',
            name='batch',
        ),
        migrations.AddField(
            model_name='enrollment',
            name='course',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='enrollments',
                to='trainers.course',
            ),
        ),
    ]
