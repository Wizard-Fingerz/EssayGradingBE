# Generated by Django 5.0.2 on 2024-02-16 06:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursequestion',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='exam.course'),
        ),
    ]