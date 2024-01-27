from rest_framework import serializers
from .models import Course, CourseQuestion

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'code', 'description']

class CourseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseQuestion
        fields = ['id', 'student', 'examiner', 'question_id', 'comprehension', 'question', 'examiner_answer', 'student_answer', 'student_score', 'question_score']
