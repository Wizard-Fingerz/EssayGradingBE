from django.urls import path
from .views import *


urlpatterns = [
    path('examiner-student-course-registrations/', ExaminerStudentCourseRegistrationListView.as_view(),
         name='student-course-registrations'),
    #     path('register-course/', StudentCourseRegistrationCreateView.as_view(),
    #          name='register-course'),
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('upload/courses/', CourseBulkUploadAPIView.as_view(),
         name='bulk-course-list-create'),
    path('course-questions/', CourseQuestionCreateView.as_view(),
         name='course-question-create'),
    path('create-exam/', CreateExamination.as_view(),
         name='course-question-create'),
    path('course-questions/<int:pk>/answer/',
         CourseQuestionAnswerView.as_view(), name='course-question-answer'),
    path('course-questions/<int:course_id>/',
         CourseQuestionDetailView.as_view(), name='course-question-detail'),
    path('courses-by-examiner/', CoursesByExaminerView.as_view(),
         name='courses-by-examiner'),
    path('exam-create/', ExamCreateView.as_view(), name='create-exam'),
    path('upload/questions/', BulkUploadExamQuestions.as_view(),
         name='bulk-create-exam'),
    path('exam-detail/<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    path('exams-with-questions/', ExamsWithQuestionsListView.as_view(),
         name='exams-with-questions'),
    path('examiner-questions/', ExaminerQuestionsListView.as_view(),
         name='examiner-questions-list'),
    path('student-course-registration/', StudentCourseRegistrationView.as_view(),
         name='student-course-registration'),
    path('student-courses/', StudentCourseListView.as_view(),
         name='student-courses-list'),
    path('student-exams/', StudentExamListView.as_view(),
         name='student-exams-list'),
    path('examiner-exams/', ExaminerExamListView.as_view(),
         name='examiner-exams-list'),
    path('get-course-questions/', CourseQuestionListView.as_view(),
         name='get-course-question-list'),
    path('exam-results/<int:pk>/', ExamResultUpdateView.as_view(),
         name='exam-result-update'),
    path('submit-answer/<int:pk>/',
         AnswerSubmissionView.as_view(), name='submit-answer'),
    path('exam-results/', ExamResultScoreListAPIView.as_view(), name='exam-results'),
    path('examiner-exam-results/', ExaminerExamResultScoreListAPIView.as_view(),
         name='examiner-exam-results'),
    path('examiner-exam-answers-score/', ExamStudentAnswersScoreListAPIView.as_view(),
         name='examiner-exam-results'),
    path('delete-course/<int:pk>/',
         CourseDetailView.as_view(), name='delete-course'),
    path('delete-exam/<int:pk>/', ExamDetailView.as_view(), name='delete-exam'),
    path('delete-course-question/<int:pk>/',
         QuestionDetailView.as_view(), name='delete-course-question'),
    path('generate-exam-slip-pdf/', GenerateExamSlipPDF.as_view(),
         name='generate-exam-slip-pdf'),
    path('generate-exam-pdf/', GenerateExamsPDF.as_view(),
         name='generate-exam-pdf'),
    path('generate-exam-answers-pdf/', GenerateExamAnswersResultsPDF.as_view(),
         name='generate-exam-answers-pdf'),
    path('generate-courses-pdf/', GenerateCoursesPDF.as_view(),
         name='generate-courses-pdf'),
    path('generate-student-result-pdf/', GenerateStudentResultPDF.as_view(),
         name='generate-student-result-pdf'),
    path('start-end-exam/<int:pk>/', ExamActivationView.as_view(), name = 'exam-activation'),

]
