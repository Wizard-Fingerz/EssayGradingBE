# Generated by Django 4.2.9 on 2024-01-27 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_remove_user_is_lecturer_user_examiner_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='examiner_id',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='matric_number',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
