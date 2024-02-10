from django.db import models
from user.models import *

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length = 250)
    code = models.CharField(max_length = 250)
    description = models.CharField(max_length = 250)


class CourseQuestion(models.Model):
<<<<<<< HEAD
    student = models.ForeignKey('Student', on_delete= models.CASCADE, related_name = 'student', null = True, blank = True)
=======
    student = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'student', null = True, blank = True)
>>>>>>> 0cd4ff983fff3670030e6ecb499319cb6d992b47
    examiner = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'examiner', null = True, blank = True)
    question_id = models.ForeignKey(Course, on_delete = models.CASCADE)
    comprehension = models.TextField()
    question = models.CharField(max_length = 250)
    examiner_answer = models.TextField()
    student_answer = models.TextField(null = True, blank = True)
    student_score = models.IntegerField(null = True, blank = True)
    question_score = models.IntegerField()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Add other student-related fields as needed

class StudentCourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
