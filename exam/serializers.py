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

class StudentCourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseRegistration
        fields = '__all__'

    
class StudentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Student
        fields = '__all__'

class CreateCourseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseQuestion
        fields = ['comprehension', 'question', 'examiner_answer', 'question_score']

# class CreateExamSerializer(serializers.ModelSerializer):
#     questions = CreateCourseQuestionSerializer(many=True)

#     class Meta:
#         model = Exam
#         fields = ['duration', 'instruction', 'course', 'questions']

#     def create(self, validated_data):
#         questions_data = validated_data.pop('questions')
#         exam = Exam.objects.create(**validated_data)

#         for question_data in questions_data:
#             CourseQuestion.objects.create(exam=exam, **question_data)

#         return exam

class CreateExamSerializer(serializers.ModelSerializer):
    questions = CreateCourseQuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = ['duration', 'instruction', 'course', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        course_questions = questions_data  # Save the questions_data to use it later
        exam = Exam.objects.create(**validated_data)

        # Now associate the questions with the exam
        for question_data in course_questions:
            CourseQuestion.objects.create(exam=exam, **question_data)

        return exam


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = CourseQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'duration', 'instruction', 'course', 'questions']

class ExamWithQuestionsSerializer(serializers.ModelSerializer):
    questions = CreateCourseQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'duration', 'instruction', 'course', 'questions']

# class CreateExamSerializer(serializers.ModelSerializer):
#     questions = CreateCourseQuestionSerializer(many=True)

#     class Meta:
#         model = Exam
#         fields = ['questions', 'duration', 'instruction', 'course']

#     def create(self, validated_data):
#         questions_data = validated_data.pop('questions', [])
#         exam = Exam.objects.create(**validated_data)

#         for question_data in questions_data:
#             CourseQuestion.objects.create(exam=exam, **question_data)

#         return exam
