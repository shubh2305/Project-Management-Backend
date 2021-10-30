from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import  LoginAPIView, LogoutAPIView, GoogleSignInView

urlpatterns = [
  path('get-access-token/', TokenRefreshView.as_view()),
  path('verify-token/', TokenVerifyView.as_view()),
  path('login/', LoginAPIView.as_view()),
  path('logout/', LogoutAPIView.as_view()),
  path('google-sign-in/', GoogleSignInView.as_view())
]
