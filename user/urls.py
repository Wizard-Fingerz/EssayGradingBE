from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'users'

router = DefaultRouter()
router.register(r'', UserViewSet, basename = 'user')

urlpatterns = [
    path('login/', CustomObtainAuthToken.as_view(), name='obtain_token'),
    path('student/register/', StudentRegistrationView.as_view(), name='student-registration'),
    path('examiner/register/', ExaminerRegistrationView.as_view(), name='examiner-registration'),
]

urlpatterns += router.urls