from django.forms.models import model_to_dict
from django.core import serializers

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .models import Document, User, Task, Project
from .serializers import DocumentSerializer, UserSerializer, TaskSerializer, ProjectSerializer, CustomException

# Generate tokens for user
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)

  return {
    'refresh': str(refresh),
    'access': str(refresh.access_token),
  }

# serializing list of model objects into dictionaries 
def serialize(model_list, Serializer, context=None):
  serialized = [Serializer(model, context=context).data for model in model_list]
  return serialized


def update(data, instance, Serializer) -> Response:
  serializer = Serializer(instance, data=data, partial=True)
  if serializer.is_valid(raise_exception=True):
    serializer.save()
    print("save serializer")
    return Response(serializer.data, status=status.HTTP_200_OK)
  return Response(serializer.error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterAPIView(APIView):

  def post(self, request, *args, **kwargs):
    data = request.data
    # user = User.objects.get(id=1)
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
    except Exception as e: 
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProtectedView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request, *args, **kwargs):
    qs = User.objects.all()
    return Response(qs.values('id', 'email', 'first_name', 'last_name', 'date_created'))


class TaskCreateView(APIView):

  def post(self, request, *args, **kwargs):
    data = request.data
    try:
      serializer = TaskSerializer(data=data)

      if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'message': 'Task was created'}, status=status.HTTP_200_OK)

      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except CustomException as ce:
      return Response(ce.__dict__, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IndividualTaskView(APIView):

  def get(self, request, *args, **kwargs):
    id = kwargs.pop('pk', None)
    try:
      project: Project = Project.objects.filter(task__id=id).first()
      task: Task = Task.objects.filter(id=id).first()
      
      response: Response = TaskSerializer(task, context={'project_id': project.id}).data
      response['project'] = ProjectSerializer(project).data
      return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
      print(e)
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def patch(self, request, pk):
    data = request.data
    try:
      task: Task = Task.objects.filter(id=pk).first()
      return update(data, task, TaskSerializer)
    except Exception as e:
      print(e)
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):

  def get(self, request, *args, **kwargs):
    id = kwargs.pop('pk', None)
    try:
      user: User = User.objects.get(id=id)
      projects: list[Project] = Project.objects.filter(members__id=id)

      response: dict = UserSerializer(user).data
      temp: list = []
      for project in projects:
        user_project: list = ProjectSerializer(project).data
        user_tasks = Task.objects.filter(project_id=project, assigned_to=user)
        user_project['tasks'] = serialize(user_tasks, TaskSerializer)
        
        temp.append(user_project)
        
      response['projects'] = temp
      return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
      print(e)
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def patch(self, request, pk):
    data = request.data
    try:
      user: User = User.objects.filter(id=pk).first()
      return update(data, user, UserSerializer)
    except Exception as e:
      print(e)
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProjectView(APIView):

  def get(self, request, *args, **kwargs):
    id = kwargs.pop('pk', None)
    try:
      project = Project.objects.filter(id=id).first()
      response = ProjectSerializer(project).data
      
      manager = project.manager
      members = project.members.all()
      tasks = Task.objects.filter(project_id=project)
      documents = Document.objects.filter(project_id=project)

      members_serialized = serialize(members, UserSerializer)
      tasks_serialized = serialize(tasks, TaskSerializer)
      documents_serialized = serialize(documents, DocumentSerializer)

      response['manager'] = UserSerializer(manager).data
      response['members'] = members_serialized
      response['tasks'] = tasks_serialized
      response['documents'] = documents_serialized

      return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
      print(e)
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class DocumentAPIView(APIView):

  def post(self, request, *args, **kwargs):
    data = request.data
    try:
      serializer = DocumentSerializer(data=data)
      if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response('Document Received')
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except CustomException as ce:
      return Response(ce.__dict__, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IndividualDocumentAPIView(APIView):
  def get(self, request, *args, **kwargs):
    id: int or None = kwargs.get('pk', None)
    try:
      document: Document or None = Document.objects.filter(id=id).first() or None
      print(document.__class__)
      if document is None:
        return Response(f'Document with ID {id} does not exist', status=status.HTTP_400_BAD_REQUEST)
      response: dict = DocumentSerializer(document).data

      project: Project = Project.objects.filter(id=response.pop('project_id')).first()
      project_data = ProjectSerializer(project).data
      response['project'] = project_data

      user: User = User.objects.filter(id=response.pop('created_by')).first()
      user_data = UserSerializer(user).data
      response['created_by'] = user_data

      return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
      print(e)
      return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)