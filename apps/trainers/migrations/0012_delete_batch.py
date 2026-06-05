from django.db import migrations


class Migration(migrations.Migration):
    """
    Drops the Batch table after both FK references (livesession.batch and
    enrollment.batch) have been removed by trainers/0011 and students/0004.
    """

    dependencies = [
        ('trainers', '0011_remove_livesession_batch_add_livesession_course'),
        ('students', '0004_remove_enrollment_batch_add_enrollment_course'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Batch',
        ),
    ]
