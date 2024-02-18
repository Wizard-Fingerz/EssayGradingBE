from rest_framework import serializers
from .models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'examiner', 'title', 'code', 'description']


class CourseQuestionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(
        source='course.title', read_only=True)
    course_code = serializers.CharField(
        source='course.code', read_only=True)

    class Meta:
        model = CourseQuestion
        fields = ['id', 'course_name', 'course_code',  'comprehension',
                  'question', 'examiner_answer', 'question_score', 'course']


class ExamSerializer(serializers.ModelSerializer):
    questions = CourseQuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = '__all__'


class GetExamSerializer(serializers.ModelSerializer):
    questions = CourseQuestionSerializer(many=True)
    examiner = serializers.CharField(source='examiner.username', read_only=True)
    course_name = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Exam
        fields = ['questions', 'examiner', 'duration', 'instruction', 'course_name', 'total_mark', 'course']


class StudentCourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseRegistration
        fields = ['student', 'course', 'registration_date']
        read_only_fields = ['registration_date']



class StudentCourseRegistrationSerializer2(serializers.ModelSerializer):
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())
    courses = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = StudentCourseRegistration
        fields = ['student', 'courses', 'registration_date']
        read_only_fields = ['registration_date']

    def create(self, validated_data):
        student = validated_data.get('student')
        course_ids = validated_data.get('courses', [])

        registrations = []
        for course_id in course_ids:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                # Handle the case where the course does not exist
                # Log a warning or skip this course registration
                # For now, we'll skip it silently
                continue

            # Check if the student is already registered for this course
            existing_registration = StudentCourseRegistration.objects.filter(student=student, course=course).first()
            if existing_registration:
                # If a registration already exists for this student-course combination, skip it
                continue

            # Create the registration for the current course
            registration = StudentCourseRegistration.objects.create(student=student, course=course)
            registrations.append(registration)

        return registrations

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'


class CreateCourseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseQuestion
        fields = ['comprehension', 'question',
                  'examiner_answer', 'question_score']


class CreateExamSerializer(serializers.ModelSerializer):
    questions = CreateCourseQuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = ['duration', 'instruction', 'course', 'questions', 'total_mark']

    def create(self, validated_data):
        course = validated_data.pop('course')
        questions_data = validated_data.pop('questions')

        # Save the questions_data to use it later
        course_questions = questions_data  

        exam = Exam.objects.create(course=course, **validated_data)

        # Now associate the questions with the exam
        for question_data in course_questions:
            question = CourseQuestion.objects.create(course=course, **question_data)
            exam.questions.add(question)  # Add the question to the many-to-many relationship

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


class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = ['id', 'student', 'question', 'student_answer', 'student_score']


class ExamResultScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResultScore
        fields = ['id', 'course', 'exam_score', 'grade']