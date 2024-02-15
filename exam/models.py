from django.db import models
from user.models import *

# Create your models here.


class Course(models.Model):
    examiner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lecturer', null=True, blank=True)
    title = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    description = models.CharField(max_length=250)

    def __str__(self):
        return str(self.title) or ''


class CourseQuestion(models.Model):
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='exam_questions', null = True, blank = True)
    student = models.ForeignKey(
        'Student', on_delete=models.CASCADE, related_name='student', null=True, blank=True)
    # question_id = models.ForeignKey(Course, on_delete = models.CASCADE)
    comprehension = models.TextField()
    question = models.CharField(max_length=250)
    examiner_answer = models.TextField()
    student_answer = models.TextField(null=True, blank=True)
    student_score = models.IntegerField(null=True, blank=True)
    question_score = models.IntegerField()

    def __str__(self):
        return str(self.question) or ''


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    # Add other student-related fields as needed

    def __str__(self):
        return str(self.user.username) or ''


class StudentCourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Enforce unique constraint on student and course combination
        unique_together = ['student', 'course']

    def __str__(self):
        return str(self.student.user.username) or ''


class Exam(models.Model):
    examiner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='examiner', null=True, blank=True)
    questions = models.ManyToManyField(
        'CourseQuestion', related_name='questions')
    duration = models.DurationField()
    instruction = models.CharField(max_length=250)
    course = models.OneToOneField('Course', on_delete=models.CASCADE)
    total_mark = models.IntegerField()

    def __str__(self):
        return str(self.course) or ''
