from .models import *
from exam.models import *
from rest_framework import serializers
from rest_framework import serializers
from .models import User
from exam.models import StudentCourseRegistration

class UserSerializer(serializers.ModelSerializer):
    matric_number = serializers.CharField(max_length=15, required=False)
    examiner_id = serializers.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['matric_number', 'examiner_id', 'password', 'is_student', 'is_examiner']

    def validate_matric_number(self, value):
        # Your custom validation for matric number here, if needed
        return value

    def validate_examiner_id(self, value):
        # Your custom validation for examiner id here, if needed
        return value

    def create(self, validated_data):
<<<<<<< HEAD
        matric_number = validated_data.pop('matric_number', None)
        examiner_id = validated_data.pop('examiner_id', None)

        if matric_number:
            username = matric_number.replace('/', '/')
            existing_user = User.objects.filter(matric_number=matric_number).first()
=======
        matric_number = validated_data.pop('matric_number')
        username = matric_number.replace('/', '/')  # Remove slashes from matric number for the username
        
        # Explicitly set is_student to True
        validated_data['is_student'] = True
>>>>>>> 0cd4ff983fff3670030e6ecb499319cb6d992b47

        elif examiner_id:
            username = examiner_id.replace('/', '/')
            existing_user = User.objects.filter(examiner_id=examiner_id).first()

        if existing_user:
            for key, value in validated_data.items():
                setattr(existing_user, key, value)
            existing_user.save()
            return existing_user
        else:
            user = User.objects.create_user(username=username, **validated_data)
            return user

class StudentCourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseRegistration
        fields = '__all__'

class StudentRegistrationSerializer(serializers.Serializer):
    user = UserSerializer()
    course_id = serializers.IntegerField()

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_student(username=user_data.get('matric_number'), password=user_data.get('password'))

        student = Student.objects.create(user=user)

        course_id = validated_data.pop('course_id')
        course_registration = StudentCourseRegistration.objects.create(student=student, course_id=course_id)

        return student


class ExaminerRegistrationSerializer(serializers.Serializer):
    user = UserSerializer()
    # Add any additional fields related to examiner registration

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_examiner(**user_data)

        # Add any additional logic related to examiner registration

        return user
