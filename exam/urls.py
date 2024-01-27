from django.urls import path
from .views import *


urlpatterns = [
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('course-questions/', CourseQuestionCreateView.as_view(), name='course-question-create'),
    path('course-questions/<int:pk>/answer/', CourseQuestionAnswerView.as_view(), name='course-question-answer'),
    path('course-questions/<int:question_id>/', CourseQuestionDetailView.as_view(), name='course-question-detail'),

]
