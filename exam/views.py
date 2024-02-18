from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .prediction import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions, viewsets, views
from .models import Course, CourseQuestion
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ObjectDoesNotExist


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
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        # Retrieve the questions created by the authenticated examiner
        return Exam.objects.filter(examiner=self.request.user)


class CourseQuestionDetailView(generics.RetrieveAPIView):
    queryset = CourseQuestion.objects.all()
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
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

    def get_queryset(self):
        # Retrieve the courses registered by the student
        registered_courses = StudentCourseRegistration.objects.filter(
            student=self.request.user.student)
        return [registration.course for registration in registered_courses]


class StudentExamListView(generics.ListAPIView):
    serializer_class = GetExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve the courses registered by the student
        registered_courses = StudentCourseRegistration.objects.filter(
            student=self.request.user.student)

        # Get exams for the registered courses
        exams = Exam.objects.filter(
            course__in=registered_courses.values_list('course', flat=True))
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


class ExamDetailView(generics.RetrieveAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ExamsWithQuestionsListView(generics.ListAPIView):
    serializer_class = ExamWithQuestionsSerializer

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
    def post(self, request, *args, **kwargs):
        print(request.data)
        user = request.user  # Assuming the user is authenticated

        # Check if the user is authenticated
        if not user.is_authenticated:
            return Response("User is not authenticated.", status=status.HTTP_401_UNAUTHORIZED)

        # Assuming the request data contains question IDs mapped to answers
        answers_data = request.data
        try:
            print('Initializing PredictionService...')
            prediction_service = PredictionService()  # Initialize PredictionService
            print('PredictionService initialized successfully.')

            for question_id, answer in answers_data.items():
                question = get_object_or_404(CourseQuestion, id=question_id)

                # Use PredictionService to predict student score
                predicted_student_score = prediction_service.predict(
                    question_id=question.course,
                    comprehension=question.comprehension,
                    question=question.question,
                    question_score=question.question_score,
                    examiner_answer=question.examiner_answer,
                    student_answer=answer
                )

                # Check if predicted score is greater than the question score
                if predicted_student_score > question.question_score:
                    student_score = question.question_score  # Set student_score to question_score
                else:
                    student_score = predicted_student_score

                # Create or update ExamResult instance
                exam_result, created = ExamResult.objects.get_or_create(
                    student=user.student,  # Use user's related Student instance
                    question=question,
                    defaults={
                        'student_answer': answer,
                        'student_score': student_score
                    }
                )

                # Update student answer and score if instance already exists
                if not created:
                    # If the instance already exists, re-run the prediction and update the score
                    predicted_student_score = prediction_service.predict(
                        question_id=question.course,
                        comprehension=question.comprehension,
                        question=question.question,
                        question_score=question.question_score,
                        examiner_answer=question.examiner_answer,
                        student_answer=answer
                    )

                    # Check if predicted score is greater than the question score
                    if predicted_student_score > question.question_score:
                        student_score = question.question_score  # Set student_score to question_score
                    else:
                        student_score = predicted_student_score

                    exam_result.student_answer = answer
                    exam_result.student_score = student_score
                    exam_result.save()

            return Response("Exam results saved successfully", status=status.HTTP_201_CREATED)
        except Exception as e:
            # Log the exception for debugging
            print(f"An error occurred while saving exam result: {e}")
            return Response(f"An error occurred while saving exam result: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExamResultScoreListAPIView(generics.ListAPIView):
    serializer_class = ExamResultScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter the queryset to retrieve only the exam result scores of the currently logged-in student
        return ExamResultScore.objects.filter(student=self.request.user.student)


