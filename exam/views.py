from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .prediction import *
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions, viewsets, views
from .models import Course, CourseQuestion
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import csv
import textdistance
from reportlab.lib.pagesizes import *
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.db.models import Q


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication,]
    # permission_classes = [permissions.AllowAny,]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        examiner = self.request.user
        serializer.save(examiner=examiner)
        return super().perform_create(serializer)


class CourseQuestionCreateView(generics.CreateAPIView):
    serializer_class = CourseQuestionSerializer
    authentication_classes = [TokenAuthentication,]
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.AllowAny,]

    def perform_create(self, serializer):
        serializer.save(examiner=self.request.user)


class CourseQuestionAnswerView(generics.UpdateAPIView):
    queryset = CourseQuestion.objects.all()
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def perform_update(self, serializer):
        # Assuming 'comprehension', 'question_score', 'student_answer', 'examiner_answer' are fields in your model
        comprehension = serializer.validated_data.get('comprehension')
        question_score = serializer.validated_data.get('question_score')
        student_answer = serializer.validated_data.get('student_answer')
        examiner_answer = serializer.validated_data.get('examiner_answer')

        # Use the PredictionService to predict student score
        # Update with the actual path to your model file
        model_path = './model/rf_model.joblib'
        prediction_service = PredictionService(model_path)
        student_score_prediction = prediction_service.predict(
            comprehension, question_score, student_answer, examiner_answer)

        # Update the 'student_score' field in the serializer
        serializer.validated_data['student_score'] = student_score_prediction

        # Save the updated instance
        serializer.save(student=self.request.user)


class ExaminerQuestionsListView(generics.ListAPIView):
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        # Retrieve the questions created by the authenticated examiner
        return CourseQuestion.objects.filter(course__examiner=self.request.user)


class CourseQuestionDetailView(generics.RetrieveAPIView):
    queryset = CourseQuestion.objects.all()
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.kwargs.get(self.lookup_url_kwarg)
        return queryset.filter(course__id=course_id)


class CourseQuestionListView(generics.ListAPIView):
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        # Get the course ID from the URL query parameters or request body
        course_id = self.request.query_params.get('course_id')

        # Filter course questions based on the provided course ID
        queryset = CourseQuestion.objects.filter(course_id=course_id)
        return queryset


class CreateExamination(generics.CreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        examiner = self.request.user
        serializer.save(examiner=examiner)
        return super().perform_create(serializer)


class CoursesByExaminerView(generics.ListAPIView):
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve the examiner's ID from the request user
        examiner_id = self.request.user.id
        # Fetch courses based on the examiner's ID
        return Course.objects.filter(examiner_id=examiner_id)


class ExaminerStudentCourseRegistrationListView(generics.ListAPIView):
    serializer_class = StudentCourseRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        # Get the current examiner from the request user
        examiner = self.request.user
        # Filter the registrations for courses created by the examiner
        queryset = StudentCourseRegistration.objects.filter(
            course__examiner=examiner)
        return queryset


class StudentCourseRegistrationView(generics.CreateAPIView):
    serializer_class = StudentCourseRegistrationSerializer2
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the courses data from the request
        course_ids = request.data.get('courses', [])

        # Assuming create method returns a single instance, not a list
        registrations = []
        for course_id in course_ids:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                # Handle the case where the course does not exist
                # Log a warning or skip this course registration
                # For now, we'll skip it silently
                continue

            student, _ = Student.objects.get_or_create(user=request.user)
            registration = StudentCourseRegistration.objects.create(
                student=student, course=course)
            registrations.append(registration)

        # Return a 201 response
        return Response({"message": "Registrations created successfully"}, status=status.HTTP_201_CREATED)

# class StudentCourseRegistrationCreateView(generics.CreateAPIView):
#     serializer_class = StudentCourseRegistrationSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         # Associate the student with the registration based on the request user
#         student = self.request.user
#         serializer.save(student=student)


class StudentCourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        # Retrieve the courses registered by the student
        registered_courses = StudentCourseRegistration.objects.filter(
            student=self.request.user.student)
        return [registration.course for registration in registered_courses]


class StudentExamListView(generics.ListAPIView):
    serializer_class = GetExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        # Retrieve the courses registered by the student
        registered_courses = StudentCourseRegistration.objects.filter(
            student=self.request.user.student)

        # Get activated exams for the registered courses
        exams = Exam.objects.filter(
            course__in=registered_courses.values_list('course', flat=True),
            is_activate=True)
        return exams


class ExaminerExamListView(generics.ListAPIView):
    serializer_class = GetExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        exams = Exam.objects.filter(examiner=self.request.user)
        return exams


class ExamCreateView(generics.CreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = CreateExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        print(request.data)
        questions_data = request.data.get('questions', [])
        course = request.data.get('course')
        print(course)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        if serializer.errors:
            print(serializer.errors)
            return Response({'detail': 'Validation Error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data['examiner'] = request.user
        self.perform_create(serializer)

        exam_instance = serializer.instance

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BulkUploadExamQuestions(APIView):
    def post(self, request, format=None):
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        questions_data = []
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                questions_data.append(row)
        except Exception as e:
            return Response({'error': 'Invalid CSV format.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CreateExamSerializer(data={'questions': questions_data})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDetailView(generics.RetrieveAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ExamsWithQuestionsListView(generics.ListAPIView):
    serializer_class = ExamWithQuestionsSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        # Retrieve exams with questions created by the current examiner
        return Exam.objects.filter(examiner=self.request.user)


class ExamResultUpdateView(generics.UpdateAPIView):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def perform_update(self, serializer):
        # Assuming 'comprehension', 'question_score', 'student_answer', 'examiner_answer' are fields in your model
        comprehension = serializer.validated_data.get('comprehension')
        question_score = serializer.validated_data.get('question_score')
        student_answer = serializer.validated_data.get('student_answer')
        examiner_answer = serializer.validated_data.get('examiner_answer')

        # Use the PredictionService to predict student score
        # Update with the actual path to your model file
        model_path = './model/dt_model.joblib'
        prediction_service = PredictionService(model_path)
        student_score_prediction = prediction_service.predict(
            comprehension, question_score, student_answer, examiner_answer)

        # Update the 'student_score' field in the serializer
        serializer.validated_data['student_score'] = student_score_prediction

        # Save the updated instance
        serializer.save(student=self.request.user)


class AnswerSubmissionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return Response("User is not authenticated.", status=status.HTTP_401_UNAUTHORIZED)

        answers_data = request.data
        try:
            for question_id, answer in answers_data.items():
                question = get_object_or_404(CourseQuestion, id=question_id)

                # Initialize PredictionService for each question
                prediction_service = PredictionService()

                # Predict student score
                student_score = prediction_service.predict(
                    question_id=question_id,
                    comprehension=question.comprehension,
                    question=question.question,
                    question_score=question.question_score,
                    examiner_answer=question.examiner_answer,
                    student_answer=answer
                )

                # Create or update ExamResult instance
                exam_result, created = ExamResult.objects.get_or_create(
                    student=user.student,
                    question=question,
                    defaults={
                        'student_answer': answer,
                        'student_score': student_score
                    }
                )

                # Update student answer and score if instance already exists
                if not created:
                    exam_result.student_answer = answer
                    exam_result.student_score = student_score
                    exam_result.save()

                # Plagiarism detection logic
                self.detect_plagiarism(question_id, answer, exam_result)

            return Response("Exam results saved successfully", status=status.HTTP_201_CREATED)
        except Exception as e:
            # Log the exception for debugging
            print(f"An error occurred while saving exam result: {e}")
            return Response(f"An error occurred while saving exam result: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def detect_plagiarism(self, question_id, new_answer, new_exam_result):
    #     # Get all existing answers for the question
    #     existing_results = ExamResult.objects.filter(question_id=question_id).exclude(id=new_exam_result.id)

    #     for result in existing_results:
    #         similarity = textdistance.jaccard(new_answer, result.student_answer)
    #         if similarity >= 0.8:  # Set your threshold here
    #             # Update similarity scores
    #             new_exam_result.similarity_score = similarity
    #             result.similarity_score = similarity
    #             new_exam_result.save()
    #             result.save()
    
    def detect_plagiarism(self, question_id, new_answer, new_exam_result):
    # Get all existing answers for the question
        existing_results = ExamResult.objects.filter(question_id=question_id).exclude(id=new_exam_result.id)

        for result in existing_results:
            similarity = textdistance.jaccard(new_answer, result.student_answer)
            similarity_percentage = f"{similarity * 100:.0f}%"  # Convert to percentage string format
            
            if similarity >= 0.8:  # Set your threshold here
                # Update similarity scores
                new_exam_result.similarity_score = similarity_percentage
                result.similarity_score = similarity_percentage
                new_exam_result.save()
                result.save()



class ExamResultScoreListAPIView(generics.ListAPIView):
    serializer_class = ExamResultScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        # Filter the queryset to retrieve only the exam result scores of the currently logged-in student
        return ExamResultScore.objects.filter(student=self.request.user.student, is_disabled=False)


class ExaminerExamResultScoreListAPIView(generics.ListAPIView):
    serializer_class = ExamResultScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        # Filter the queryset to retrieve only the exam result scores related to courses where the examiner is the currently logged-in user
        courses = Course.objects.filter(examiner=self.request.user)
        return ExamResultScore.objects.filter(course__in=courses)


class ExamStudentAnswersScoreListAPIView(generics.ListAPIView):
    serializer_class = AnswerScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        # Filter the queryset to retrieve only the exam result scores related to courses where the examiner is the currently logged-in user
        courses = Course.objects.filter(examiner=self.request.user)
        course_questions = CourseQuestion.objects.filter(course__in=courses)
        return ExamResult.objects.filter(question__in=course_questions)


class CourseBulkUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.data:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

            file = request.data['file']

            if not file.name.endswith('.csv'):
                return Response({'error': 'Invalid file format. Please upload a CSV file'}, status=status.HTTP_400_BAD_REQUEST)

            courses_created = 0

            # Parse the CSV file
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                if all(field in row for field in ['title', 'code', 'description',]):
                    # Create Course instance
                    course = Course(
                        examiner=request.user,
                        title=row.get('title'),
                        code=row.get('code'),
                        description=row.get('description')
                    )
                    course.save()
                    courses_created += 1
                else:
                    return Response({'error': 'Missing required fields in CSV row'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': f'{courses_created} courses created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = CourseQuestion.objects.all()
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExamDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]


class GenerateExamSlipPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def apply_watermark(self, canvas, watermark):
        width, height = letter
        canvas.saveState()
        canvas.drawImage(watermark, 0, 0, width*0.2, height*0.1)
        canvas.restoreState()

    def get(self, request):
        # Get the currently authenticated student
        student = request.user.student
        user = request.user
        username = user.matric_number
        first_name = user.first_name
        last_name = user.last_name

        # Get the student's course registrations
        course_registrations = StudentCourseRegistration.objects.filter(
            student=student)

        # Create a response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exam_slip.pdf"'

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Create data for the table
        data = [['Course Code', 'Course Title', 'Course Description']]
        for registration in course_registrations:
            data.append([registration.course.code, registration.course.title,
                         registration.course.description])

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
            "Matric/Registration Number: {}".format(username), getSampleStyleSheet()['BodyText'])
        name_paragraph = Paragraph("Name: {} {}".format(
            first_name, last_name), getSampleStyleSheet()['BodyText'])

        # Add padding to the top of the table
        padding_paragraph = Spacer(1, 20)  # Adjust the height as needed
        # Create some paragraphs
        paragraphs = []
        # Add your paragraphs here
        paragraphs.append(Paragraph(
            "*This is an official course registered list by this particular student", getSampleStyleSheet()['BodyText']))
        paragraphs.append(Paragraph(
            "*Contact examiner if any corrections is required", getSampleStyleSheet()['BodyText']))

        # Add the table and paragraphs to the PDF document
        doc.build([username_paragraph, name_paragraph, padding_paragraph, table] + paragraphs,
                  onFirstPage=lambda canvas, _: self.apply_watermark(canvas, './media/logo.png'))

        return response


class GenerateExamsPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def apply_watermark(self, canvas, watermark):
        width, height = letter
        canvas.saveState()
        canvas.drawImage(watermark, 0, 0, width*0.2, height*0.1)
        canvas.restoreState()

    def get(self, request):
        # Get the currently authenticated student
        examiner = request.user.id
        user = request.user
        username = user.examiner_id
        first_name = user.first_name
        last_name = user.last_name

        # Get the examiner exams
        exams = Exam.objects.filter(
            examiner=examiner)

        # Create a response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exam_list.pdf"'

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Create data for the table
        data = [['Course', "Number of Questions",
                 'Duration', 'Instruction', 'Total Mark',]]
        for exam in exams:
            data.append([exam.course, exam.questions.count(), exam.duration,
                         exam.instruction, exam.total_mark, ])

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
        username_paragraph = Paragraph("Examiner ID: {}".format(
            username), getSampleStyleSheet()['BodyText'])
        name_paragraph = Paragraph("Name: {} {}".format(
            first_name, last_name), getSampleStyleSheet()['BodyText'])

        # Add padding to the top of the table
        padding_paragraph = Spacer(1, 20)  # Adjust the height as needed
        # Create some paragraphs
        paragraphs = []
        # Add your paragraphs here
        paragraphs.append(Paragraph(
            "*This is an official exam list by this particular examiner", getSampleStyleSheet()['BodyText']))
        paragraphs.append(Paragraph(
            "*Contact admin if any corrections is required", getSampleStyleSheet()['BodyText']))

        # Add the table and paragraphs to the PDF document
        doc.build([username_paragraph, name_paragraph, padding_paragraph, table] + paragraphs,
                  onFirstPage=lambda canvas, _: self.apply_watermark(canvas, './media/logo.png'))

        return response


class GenerateStudentResultsPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def apply_watermark(self, canvas, watermark):
        width, height = letter
        canvas.saveState()
        canvas.drawImage(watermark, 0, 0, width*0.2, height*0.1)
        canvas.restoreState()

    def get(self, request):
        # Get the currently authenticated student
        examiner = request.user.id
        user = request.user
        username = user.examiner_id
        first_name = user.first_name
        last_name = user.last_name

        # Get the examiner exams
        result = ExamResultScore.objects.filter(
            course__examiner=examiner)

        # Create a response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="student_results.pdf"'

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Create data for the table
        data = [['Course Code', "Course Title",
                 'Matric Number', 'Score','Percentage Score', 'Grade',]]
        for result in result:
            data.append([result.course.code, result.course.title, result.student, result.exam_score,
                         result.percentage_score, result.grade, ])

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
        username_paragraph = Paragraph("Examiner ID: {}".format(
            username), getSampleStyleSheet()['BodyText'])
        name_paragraph = Paragraph("Name: {} {}".format(
            first_name, last_name), getSampleStyleSheet()['BodyText'])

        # Add padding to the top of the table
        padding_paragraph = Spacer(1, 20)  # Adjust the height as needed
        # Create some paragraphs
        paragraphs = []
        # Add your paragraphs here
        paragraphs.append(Paragraph(
            "*This is an official exam list by this particular examiner", getSampleStyleSheet()['BodyText']))
        paragraphs.append(Paragraph(
            "*Contact admin if any corrections is required", getSampleStyleSheet()['BodyText']))

        # Add the table and paragraphs to the PDF document
        doc.build([username_paragraph, name_paragraph, padding_paragraph, table] + paragraphs,
                  onFirstPage=lambda canvas, _: self.apply_watermark(canvas, './media/logo.png'))

        return response



class GenerateExamAnswersResultsPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def apply_watermark(self, canvas, watermark):
        width, height = LEGAL
        canvas.saveState()
        canvas.drawImage(watermark, 0, 0, width*0.2, height*0.1)
        canvas.restoreState()

    def get(self, request):
        # Get the currently authenticated student
        examiner = request.user.id
        user = request.user
        username = user.examiner_id
        first_name = user.first_name
        last_name = user.last_name

        # Get the students' answer results
        exam_answers_results = ExamResult.objects.filter(
            question__course__examiner=examiner)

        # Create a response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exam_answer_score.pdf"'

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=LEGAL)

        # Create data for the table
        data = [['Student', 'Course Code', 'Course Title', 'Question Number', "Question",
                 'Answer', 'Score', 'Question Score']]
        for exam_answers_result in exam_answers_results:
            data.append([
                exam_answers_result.student,
                exam_answers_result.question.course.code,
                exam_answers_result.question.course.title,
                exam_answers_result.question.question_number,
                exam_answers_result.student_answer,
                exam_answers_result.student_score,
                exam_answers_result.question.question_score
            ])

        # Calculate column widths based on the length of the longest text in each column
        column_widths = []
        for col in zip(*data):
            column_widths.append(max([len(str(value))
                                 for value in col]) * 0.25 * inch)

        # Create a table from the data
        table = Table(data, colWidths=column_widths)

        # Apply styles to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), 1),  # Enable text wrapping
        ])

        table.setStyle(style)

        # Create a paragraph for student details
        username_paragraph = Paragraph("Examiner ID: {}".format(
            username), getSampleStyleSheet()['BodyText'])
        name_paragraph = Paragraph("Name: {} {}".format(
            first_name, last_name), getSampleStyleSheet()['BodyText'])

        # Add padding to the top of the table
        padding_paragraph = Spacer(1, 20)  # Adjust the height as needed

        # Create some paragraphs
        paragraphs = [
            Paragraph("*This is an official exam answer list of the students who wrote exams set by this particular examiner",
                      getSampleStyleSheet()['BodyText']),
            Paragraph("*Contact admin if any corrections are required",
                      getSampleStyleSheet()['BodyText'])
        ]

        # Add the table and paragraphs to the PDF document
        doc.build([username_paragraph, name_paragraph, padding_paragraph, table] + paragraphs,
                  onFirstPage=lambda canvas, _: self.apply_watermark(canvas, './media/logo.png'))

        return response


class GenerateCoursesPDF(APIView):
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
        username = user.examiner_id
        first_name = user.first_name
        last_name = user.last_name

        # Get the student's course registrations
        courses = Course.objects.filter(
            examiner=examiner)

        # Create a response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="course_list.pdf"'

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Create data for the table
        data = [['Course Code', 'Course Title', 'Course Description']]
        for course in courses:
            data.append([course.code, course.title,
                         course.description])

        # Create a table from the data
        table = Table(data)

        # Apply styles to the table
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            # Enable text wrapping
                            ('WORDWRAP', (0, 0), (-1, -1), 1),
                            ])

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
            "*This is an official course list by this particular examiner", getSampleStyleSheet()['BodyText']))
        paragraphs.append(Paragraph(
            "*Contact this examiner or admin if any corrections is required", getSampleStyleSheet()['BodyText']))

        # Add the table and paragraphs to the PDF document
        doc.build([username_paragraph, name_paragraph, padding_paragraph, table] + paragraphs,
                  onFirstPage=lambda canvas, _: self.apply_watermark(canvas, './media/logo.png'))

        return response



class GenerateStudentResultPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def apply_watermark(self, canvas, watermark):
        width, height = letter
        canvas.saveState()
        canvas.drawImage(watermark, 0, 0, width*0.2, height*0.1)
        canvas.restoreState()

    def get(self, request):
        # Get the currently authenticated student
        student = request.user.student
        user = request.user
        username = user.matric_number
        first_name = user.first_name
        last_name = user.last_name

        # Get the student's course registrations
        exam_result_scores = ExamResultScore.objects.filter(
            student=student)

        # Create a response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="result.pdf"'

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Create data for the table
        data = [['Course', 'Course Ttile', 'Exam Score', 'Percentage Score', 'Grade']]
        for exam_result_score in exam_result_scores:
            data.append([exam_result_score.course.code,exam_result_score.course.title, exam_result_score.exam_score,
                         exam_result_score.percentage_score, exam_result_score.grade])

        # Create a table from the data
        table = Table(data)

        # Apply styles to the table
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            # Enable text wrapping
                            ('WORDWRAP', (0, 0), (-1, -1), 1),
                            ])

        table.setStyle(style)

        # Create a paragraph for student details# Create paragraphs for student details
        username_paragraph = Paragraph(
            "Matric No/Regstration No: {}".format(username), getSampleStyleSheet()['BodyText'])
        name_paragraph = Paragraph("Name: {} {}".format(
            first_name, last_name), getSampleStyleSheet()['BodyText'])

        # Add padding to the top of the table
        padding_paragraph = Spacer(1, 20)  # Adjust the height as needed
        # Create some paragraphs
        paragraphs = []
        # Add your paragraphs here
        paragraphs.append(Paragraph(
            "*This is an official result of this particular student", getSampleStyleSheet()['BodyText']))
        paragraphs.append(Paragraph(
            "*Contact examiner or admin if any corrections is required", getSampleStyleSheet()['BodyText']))

        # Add the table and paragraphs to the PDF document
        doc.build([username_paragraph, name_paragraph, padding_paragraph, table] + paragraphs,
                  onFirstPage=lambda canvas, _: self.apply_watermark(canvas, './media/logo.png'))

        return response




class ExamActivationView(generics.UpdateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Exam.objects.filter(examiner=self.request.user)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        is_activate = request.data.get('is_activate', None)

        if is_activate is None:
            return Response({"is_activate": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        instance.is_activate = is_activate
        instance.save()

        return Response(self.get_serializer(instance).data)


class DisplayResultActivationView(generics.UpdateAPIView):
    serializer_class = ExamResultScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return ExamResultScore.objects.filter(course__examiner=self.request.user)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        is_disabled = request.data.get('is_disabled', None)

        if is_disabled is None:
            return Response({"is_disabled": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        instance.is_disabled = is_disabled
        instance.save()

        return Response(self.get_serializer(instance).data)
