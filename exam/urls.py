from django.urls import path
from .views import *


urlpatterns = [
    path('student-course-registrations/', StudentCourseRegistrationListView.as_view(),
         name='student-course-registrations'),
    path('register-course/', StudentCourseRegistrationCreateView.as_view(),
         name='register-course'),
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('course-questions/', CourseQuestionCreateView.as_view(),
         name='course-question-create'),
    path('create-exam/', CreateExamination.as_view(),
         name='course-question-create'),
    path('course-questions/<int:pk>/answer/',
         CourseQuestionAnswerView.as_view(), name='course-question-answer'),
    path('course-questions/<int:question_id>/',
         CourseQuestionDetailView.as_view(), name='course-question-detail'),
    path('courses-by-examiner/', CoursesByExaminerView.as_view(),
         name='courses-by-examiner'),


]
