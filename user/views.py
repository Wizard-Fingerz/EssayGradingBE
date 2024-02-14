from django.shortcuts import render
from .models import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Determine the type of user (admin, student, examiner)
        user_type = None

        if user.is_admin:
            user_type = 'admin'
        elif user.is_student:
            user_type = 'student'
            
        elif user.is_examiner:
            user_type = 'examiner'

        return Response({
            'token': token.key,
            'user_type': user_type,

        })

class StudentRegistrationView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Retrieve the user instance created during registration
        user = serializer.instance.user

        # Assuming the course_id is provided in the request data
        course_id = request.data.get('course_id')

        # Create a StudentCourseRegistration entry
        StudentCourseRegistration.objects.create(student=user.student, course_id=course_id)

        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'Student user created and registered for the course successfully.'},
                        status=status.HTTP_201_CREATED, headers=headers)

class ExaminerRegistrationView(generics.CreateAPIView):
    serializer_class = ExaminerRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'Examiner user created successfully.'}, status=status.HTTP_201_CREATED, headers=headers)
