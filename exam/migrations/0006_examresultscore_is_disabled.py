# Generated by Django 5.0.2 on 2024-05-16 16:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exam", "0005_coursequestion_question_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="examresultscore",
            name="is_disabled",
            field=models.BooleanField(default=True),
        ),
    ]
