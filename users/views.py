from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)

  return {
    'refresh': str(refresh),
    'access': str(refresh.access_token),
  }


class LoginAPIView(APIView):
  def post(self, request, *args, **kwargs):
    data = request.data

    email = data.get('email')
    password = data.get('password')

    if not email: 
      return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not password: 
      return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
    try: 
      user = User.objects.get(email=email)

      if not user.check_password(password):
        return Response({'error': 'Password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

      tokens = get_tokens_for_user(user)
      tokens['user'] = email

      return Response(tokens, status=status.HTTP_200_OK)
    except:
      return Response({'error': f'User with email {email} does not exists!'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
  def post(self, request, *args, **kwargs):
    data = request.data

    refresh = data['refresh']

    token = RefreshToken(refresh)
    token.blacklist()

    return Response({'message': 'Successful Logout'}, status=status.HTTP_200_OK)