# Generated manually for Course.category field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainers', '0016_remove_module_notes_file_module_notes_binary_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
