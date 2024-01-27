# Generated by Django 4.2.9 on 2024-01-27 14:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exam', '0004_coursequestion_student_delete_studentscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursequestion',
            name='examiner',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='examiner', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coursequestion',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL),
        ),
    ]
