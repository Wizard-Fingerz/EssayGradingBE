# Generated by Django 4.2.9 on 2024-01-27 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_managers_user_matric_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_lecturer',
        ),
        migrations.AddField(
            model_name='user',
            name='examiner_id',
            field=models.CharField(default=0, max_length=15, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='is_examiner',
            field=models.BooleanField(default=False, verbose_name='Examiner'),
        ),
    ]
