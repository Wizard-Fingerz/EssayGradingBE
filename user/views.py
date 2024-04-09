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
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import *
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


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

# class BulkStudentUploadAPIView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     authentication_classes = [TokenAuthentication,]
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         print('hello')
#         print(request.data)
#         # Check if the request contains a file
#         if 'file' not in request.data:
#             print('No file uploaded')
#             return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

#         file = request.data['file']

#         # Check if the uploaded file is a CSV file
#         if not file.name.endswith('.csv'):
#             return Response({'error': 'Invalid file format. Please upload a CSV file'}, status=status.HTTP_400_BAD_REQUEST)

#         # Validate the header row of the CSV file
#         try:
#             decoded_file = file.read().decode('utf-8').splitlines()
#             reader = csv.reader(decoded_file)
#             header = next(reader)  # Read the header row
#             print(header)
#             required_fields = ['first_name', 'last_name', 'matric_number', 'password']  # Define your required fields here
#             if not all(field in header for field in required_fields):
#                 return Response({'error': 'Missing required fields in CSV header'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 print('hello')
#                 students = []

#                 # Parse the CSV file
#                 print(decoded_file)
#                 reader = csv.DictReader(decoded_file)
#                 for row in reader:
#                     # Validate and process each row
#                     serializer = StudentRegistrationSerializer(data=row)

#                     print('hello  after serializer')
#                     print(serializer)
#                     if serializer.is_valid():
#                         # Encrypt the password before saving
#                         print(serializer.errors)
#                         serializer.validated_data['is_student'] = True
#                         serializer.validated_data['username'] = serializer.validated_data['matric_number']
#                         row['password'] = make_password(row.get('password'))
#                         # Save the student record
#                         student = serializer.save()
#                         students.append(student)
#                     else:
#                         return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
#         # Create or update student records
#         created_students = []
#         for student_data in students:
#             serializer = StudentRegistrationSerializer(data=student_data)
#             if serializer.is_valid():
#                 serializer.save()
#                 created_students.append(serializer.data)
#             else:
#                 return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({'success': f'{len(created_students)} students created successfully'}, status=status.HTTP_201_CREATED)


class BulkStudentUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.data:
                return JsonResponse({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

            file = request.data['file']

            if not file.name.endswith('.csv'):
                return JsonResponse({'error': 'Invalid file format. Please upload a CSV file'}, status=status.HTTP_400_BAD_REQUEST)

            students_created = 0

            # Parse the CSV file
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                # Validate and process each row
                if all(field in row for field in ['first_name', 'last_name', 'matric_number', 'password']):
                    # Create User instance
                    user = User.objects.create_student(
                        username=row['matric_number'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        password=row['password']
                    )
                    # Additional fields if necessary
                    user.is_student = True
                    user.save()
                    students_created += 1
                else:
                    return JsonResponse({'error': 'Missing required fields in CSV row'}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({'success': f'{students_created} students created successfully'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = StudentsListSerializer
    permission_classes = [permissions.IsAuthenticated]




class GenerateStudentListPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def apply_watermark(self, canvas, watermark):
        width, height = letter
        canvas.saveState()
        canvas.drawImage(watermark, 0, 0, width*0.2, height*0.1)
        canvas.restoreState()

    def get(self, request):
        # Get the currently authenticated student
        examiner = request.user
        user = request.user
        username = user.matric_number
        first_name = user.first_name
        last_name = user.last_name

        # Get the student's course registrations
        students = User.objects.filter(
            is_student=True)

        # Create a response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exam_slip.pdf"'

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Create data for the table
        data = [['First Name', 'Last Name', 'Matric Number']]
        for student in students:
            data.append([student.first_name, student.last_name,
                         student.matric_number])

        # Create a table from the data
        table = Table(data)

        # Apply styles to the table
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)

        # Create a paragraph for student details# Create paragraphs for student details
        username_paragraph = Paragraph(
            "Examiner ID: {}".format(username), getSampleStyleSheet()['BodyText'])
        name_paragraph = Paragraph("Name: {} {}".format(
            first_name, last_name), getSampleStyleSheet()['BodyText'])

        # Add padding to the top of the table
        padding_paragraph = Spacer(1, 20)  # Adjust the height as needed
        # Create some paragraphs
        paragraphs = []
        # Add your paragraphs here
        paragraphs.append(Paragraph(
            "*This is an official list of students added by this particular examiner", getSampleStyleSheet()['BodyText']))
        paragraphs.append(Paragraph(
            "*Contact admin if any corrections is required", getSampleStyleSheet()['BodyText']))

        # Add the table and paragraphs to the PDF document
        doc.build([username_paragraph, name_paragraph, padding_paragraph, table] + paragraphs,
                  onFirstPage=lambda canvas, _: self.apply_watermark(canvas, './media/logo.png'))

        return response


