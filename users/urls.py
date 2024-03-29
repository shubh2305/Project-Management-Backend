from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import  (
  LoginAPIView, 
  LogoutAPIView, 
  GoogleSignInView, 
  RegisterAPIView, 
  ProtectedView, 
  TaskCreateView,
  UserProfileView,
  ProjectView,
  IndividualProjectView,
  IndividualTaskView,
  DocumentAPIView,
  IndividualDocumentAPIView
)

urlpatterns = [
  path('get-access-token/', TokenRefreshView.as_view()),
  path('verify-token/', TokenVerifyView.as_view()),
  path('register/', RegisterAPIView.as_view()),
  path('login/', LoginAPIView.as_view()),
  path('logout/', LogoutAPIView.as_view()),
  path('google-sign-in/', GoogleSignInView.as_view()),
  path('', ProtectedView.as_view()),
  path('create-task/', TaskCreateView.as_view()),
  path('<int:pk>/', UserProfileView.as_view()),
  path('project/<int:pk>/', IndividualProjectView.as_view()),
  path('project/', ProjectView.as_view()),
  path('task/<int:pk>/', IndividualTaskView.as_view()),
  path('document/', DocumentAPIView.as_view()),
  path('document/<int:pk>/', IndividualDocumentAPIView.as_view())
]


