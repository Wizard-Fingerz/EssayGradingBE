from django.db import models
from user.models import *
from django.db.models import Sum


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
    # exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='exam_questions', null = True, blank = True)
    course = models.ForeignKey(Course, on_delete = models.CASCADE, null = True, blank = True)
    comprehension = models.TextField()
    question = models.CharField(max_length=250)
    examiner_answer = models.TextField()
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
    course = models.OneToOneField('Course', on_delete=models.CASCADE, null = True, blank = True)
    total_mark = models.IntegerField()
    is_activate = models.BooleanField(default = False)

    def __str__(self):
        return str(self.course) or ''

class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(CourseQuestion, on_delete=models.CASCADE)
    student_answer = models.TextField(null=True, blank=True)
    student_score = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.user}'s answer to {self.question}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Calculate total exam score for the student for the specific course examination
        exam_score = ExamResult.objects.filter(student=self.student, question__course=self.question.course).aggregate(total_score=Sum('student_score'))['total_score']
        exam_score = exam_score if exam_score is not None else 0
        
        # Update or create ExamResultScore instance for the student
        exam_result_score, _ = ExamResultScore.objects.get_or_create(student=self.student, course=self.question.course)
        exam_result_score.exam_score = exam_score
        exam_result_score.calculate_grade()
        exam_result_score.save()

class ExamResultScore(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    exam_score = models.IntegerField(null=True, blank=True)
    percentage_score = models.FloatField(null=True, blank=True)
    grade = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return f"{self.student}'s exam score for {self.course}"

    def calculate_grade(self):
        total_mark = self.course.exam.total_mark
        percent_score = (self.exam_score / total_mark) * 100
        self.percentage_score = percent_score
        if percent_score >= 70:
            self.grade = 'A'
        elif percent_score >= 60:
            self.grade = 'B'
        elif percent_score >= 50:
            self.grade = 'C'
        elif percent_score >= 40:
            self.grade = 'D'
        elif percent_score >= 30:
            self.grade = 'E'
        else:
            self.grade = 'F'
