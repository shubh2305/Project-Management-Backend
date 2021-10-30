from django.db.models import fields
from django.shortcuts import redirect, render
from django.forms.models import model_to_dict
from django.core.serializers import serialize
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
    
    user = User.objects.filter(email=email)[0]

    if not user.check_password(password):
      return Response({'error': 'Password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    tokens = get_tokens_for_user(user)
    # user_data = serialize('json', [user], fields=('id', 'email'))
    user_data = model_to_dict(user, fields=['id', 'email'])
    tokens['user'] = user_data

    return Response(tokens, status=status.HTTP_200_OK)
    # except:
    #   return Response({'error': f'User with email {email} does not exists!'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
  def post(self, request, *args, **kwargs):
    data = request.data

    refresh = data['refresh']

    token = RefreshToken(refresh)
    token.blacklist()

    return Response({'message': 'Successful Logout'}, status=status.HTTP_200_OK)


class GoogleSignInView(APIView):
  def post(self, request, *args, **kwargs):
    data = request.data

    email = data.get('profileObj').get('email')
    # print(email)
    try:
      user, created = User.objects.get_or_create(email=email)
      
      tokens = get_tokens_for_user(user)

      tokens['user'] = email

      return Response(tokens, status=status.HTTP_200_OK)
    except: 
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)