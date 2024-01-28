from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'

# serializers.py

from rest_framework import serializers
from .models import User

class StudentRegistrationSerializer(serializers.ModelSerializer):
    matric_number = serializers.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('matric_number', 'password', 'is_student')

    def validate_matric_number(self, value):
        # Your custom validation for matric number here, if needed
        return value

    def create(self, validated_data):
        matric_number = validated_data.pop('matric_number')
        username = matric_number.replace('/', '/')  # Remove slashes from matric number for the username
        
        # Explicitly set is_student to True
        validated_data['is_student'] = True

        # Try to get an existing user with the same matric_number
        existing_user = User.objects.filter(matric_number=matric_number).first()

        if existing_user:
            # Update the existing user instead of creating a new one
            for key, value in validated_data.items():
                setattr(existing_user, key, value)
            existing_user.save()
            return existing_user
        else:
            # Create a new user if no existing user with the same matric_number is found
            user = User.objects.create_student(username=username, matric_number=matric_number, **validated_data)
            return user



class ExaminerRegistrationSerializer(serializers.ModelSerializer):
    examiner_id = serializers.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('examiner_id', 'password', 'is_examiner')

    def validate_examiner_id(self, value):
        # Your custom validation for matric number here, if needed
        return value

    def create(self, validated_data):
        examiner_id = validated_data.pop('examiner_id')
        username = examiner_id.replace('/', '/')  # Remove slashes from matric number for the username

        # Try to get an existing user with the same matric_number
        existing_user = User.objects.filter(examiner_id=examiner_id).first()

        if existing_user:
            # Update the existing user instead of creating a new one
            for key, value in validated_data.items():
                setattr(existing_user, key, value)
            existing_user.save()
            return existing_user
        else:
            # Create a new user if no existing user with the same matric_number is found
            user = User.objects.create_examiner(username=username, examiner_id=examiner_id, **validated_data)
            return user
