from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainers', '0010_remove_livesession_course_batch_livesession_batch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='livesession',
            name='batch',
        ),
        migrations.AddField(
            model_name='livesession',
            name='course',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='live_sessions',
                to='trainers.course',
            ),
        ),
    ]
