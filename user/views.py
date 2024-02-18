from django.shortcuts import render
from .models import *
import csv
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import generics, permissions, viewsets, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
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
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Create a mutable copy of the request data
        mutable_data = request.data.copy()

        # Ensure is_student is set to True
        mutable_data['is_student'] = True

        # Set matric_number equal to the username if 'username' is present in mutable_data
        if 'username' in mutable_data:
            mutable_data['matric_number'] = mutable_data['username']

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'Student user created and registered for the course successfully.'},
                        status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Set is_student to True and matric_number to username before saving
        serializer.validated_data['is_student'] = True
        serializer.validated_data['matric_number'] = serializer.validated_data['username']

        # Encrypt the password using make_password
        raw_password = serializer.validated_data['password']
        encrypted_password = make_password(raw_password)
        serializer.validated_data['password'] = encrypted_password

        serializer.save()

class BulkStudentUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print('hello')
        print(request.data)
        # Check if the request contains a file
        if 'file' not in request.data:
            print('No file uploaded')
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.data['file']

        # Check if the uploaded file is a CSV file
        if not file.name.endswith('.csv'):
            return Response({'error': 'Invalid file format. Please upload a CSV file'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the header row of the CSV file
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            header = next(reader)  # Read the header row
            required_fields = ['first_name', 'last_name', 'matric_number', 'password']  # Define your required fields here
            if not all(field in header for field in required_fields):
                return Response({'error': 'Missing required fields in CSV header'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        students = []

        # Parse the CSV file
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                # Encrypt the password before saving
                row['password'] = make_password(row.get('password'))
                serializer = StudentRegistrationSerializer(data=row)
                if serializer.is_valid():
                    students.append(serializer.validated_data)
                else:
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update student records
        created_students = []
        for student_data in students:
            serializer = StudentRegistrationSerializer(data=student_data)
            if serializer.is_valid():
                serializer.save()
                created_students.append(serializer.data)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': f'{len(created_students)} students created successfully'}, status=status.HTTP_201_CREATED)

class ExaminerRegistrationView(generics.CreateAPIView):
    serializer_class = ExaminerRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'Examiner user created successfully.'}, status=status.HTTP_201_CREATED, headers=headers)


class StudentRegistrationView2(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'Student user created successfully.'}, status=status.HTTP_201_CREATED, headers=headers)


class StudentListView(generics.ListAPIView):
    queryset = User.objects.filter(is_student=True)
    serializer_class = StudentsListSerializer
