from rest_framework import serializers
from .models import *

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'examiner','title', 'code', 'description']

class CourseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseQuestion
        fields = ['id', 'student', 'comprehension', 'question', 'examiner_answer', 'student_answer', 'student_score', 'question_score']

class ExamSerializer(serializers.ModelSerializer):
    questions = CourseQuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'