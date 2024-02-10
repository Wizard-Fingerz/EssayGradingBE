from django.shortcuts import render
from .prediction import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from .models import Course, CourseQuestion
from .serializers import *
from rest_framework.authentication import TokenAuthentication


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication,]
    # permission_classes = [permissions.AllowAny,]
    permission_classes = [permissions.IsAuthenticated]

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
        model_path = './model/dt_model.joblib'  # Update with the actual path to your model file
        prediction_service = PredictionService(model_path)
        student_score_prediction = prediction_service.predict(comprehension, question_score, student_answer, examiner_answer)

        # Update the 'student_score' field in the serializer
        serializer.validated_data['student_score'] = student_score_prediction

        # Save the updated instance
        serializer.save(student=self.request.user)


class CourseQuestionDetailView(generics.RetrieveAPIView):
    queryset = CourseQuestion.objects.all()
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def retrieve(self, request, *args, **kwargs):
        # Retrieve the question_id from the URL parameters
        question_id = self.kwargs.get('question_id')

        # Query the database to get the specific course question
        course_questions = CourseQuestion.objects.filter(question_id=question_id)

        if not course_questions.exists():
            return Response({"detail": "Course questions not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(course_questions, many=True)
        return Response(serializer.data)
