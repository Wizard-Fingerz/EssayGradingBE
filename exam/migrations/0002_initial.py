# Generated by Django 5.0.2 on 2024-02-18 18:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exam', '0001_initial'),
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='examiner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lecturer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='coursequestion',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='exam.course'),
        ),
        migrations.AddField(
            model_name='exam',
            name='course',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='exam.course'),
        ),
        migrations.AddField(
            model_name='exam',
            name='examiner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='examiner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exam',
            name='questions',
            field=models.ManyToManyField(related_name='questions', to='exam.coursequestion'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.coursequestion'),
        ),
        migrations.AddField(
            model_name='examresultscore',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.course'),
        ),
        migrations.AddField(
            model_name='examresultscore',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.student'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.student'),
        ),
        migrations.CreateModel(
            name='StudentCourseRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.student')),
            ],
            options={
                'unique_together': {('student', 'course')},
            },
        ),
    ]
