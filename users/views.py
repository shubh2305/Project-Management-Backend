from django.forms.models import model_to_dict
from django.core import serializers

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, Task, Project
from .serializers import UserSerializer, TaskSerializer, ProjectSerializer

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)

  return {
    'refresh': str(refresh),
    'access': str(refresh.access_token),
  }

def serialize(model_list, Serializer):
  serialized = [Serializer(model).data for model in model_list]
  return serialized

class RegisterAPIView(APIView):

  def post(self, request, *args, **kwargs):
    data = request.data

    serializer = UserSerializer(data=data)

    if serializer.is_valid(raise_exception=True):
      serializer.save()
      return Response({'message': 'User was created'}, status=status.HTTP_200_OK)

    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

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

      user_data = model_to_dict(user, fields=['id', 'email'])

      tokens['user'] = user_data

      return Response(tokens, status=status.HTTP_200_OK)
    except: 
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProtectedView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request, *args, **kwargs):
    qs = User.objects.all()
    return Response(qs.values('id', 'email', 'first_name', 'last_name', 'date_created'))

class TaskCreateView(APIView):

  def get(self, request, *args, **kwargs):
    tasks = list(Task.objects.values())
    try:
      for task in tasks:
        user_id = task.pop('assigned_to_id', None)
        user = User.objects.get(id=user_id)
        task['user'] = UserSerializer(user).data
      return Response(tasks, status=status.HTTP_200_OK)
    except Exception: 
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


  def post(self, request, *args, **kwargs):
    data = request.data

    serializer = TaskSerializer(data=data)

    if serializer.is_valid(raise_exception=True):
      serializer.save()
      return Response({'message': 'Task was created'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class IndividualTaskView(APIView):

  def get(self, request, *args, **kwargs):
    id = kwargs.pop('pk', None)
    try:
      projects = Project.objects.filter(tasks__id=id)
      print(projects)
      return Response(status=status.HTTP_200_OK)
    except Exception as e:
      print(e)
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):

  def get(self, request, *args, **kwargs):
    id = kwargs.pop('pk', None)
    try:
      user = User.objects.get(id=id)
      tasks = Task.objects.filter(assigned_to=id)
      projects = Project.objects.filter(members__id=id)
      response = UserSerializer(user).data

      response['tasks'] = serialize(tasks, TaskSerializer)
      response['projects'] = serialize(projects, ProjectSerializer)
      return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
      print(e)
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProjectView(APIView):

  def get(self, request, *args, **kwargs):
    id = kwargs.pop('pk', None)
    try:
      project = Project.objects.filter(id=id).first()
      response = ProjectSerializer(project).data
      
      manager = project.manager
      members = project.members.all()
      tasks = project.tasks.all()

      members_serialized = serialize(members, UserSerializer)
      tasks_serialized = serialize(tasks, TaskSerializer)
      print(response)

      response['manager'] = UserSerializer(manager).data
      response['members'] = members_serialized
      response['tasks'] = tasks_serialized

      return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
      print(e)
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def post(self, request, *args, **kwargs):
    data = request.data

    try:
      serializer = ProjectSerializer(data=data)
      if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'message': 'Project was created'}, status=status.HTTP_200_OK)

      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
      print('[This is line 186,  views.py]', e)
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)