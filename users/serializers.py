from django.utils.encoding import force_text

from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from .models import Document, User, Task, Project, Document

class CustomException(APIException):
  status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
  default_detail = 'Server Error'

  def __init__(self, detail, field, status_code):
    if status_code is not None:self.status_code = status_code
    if detail is not None:
      self.detail = {field: force_text(detail)}
    else: self.detail = {'detail': force_text(self.default_detail)}


class UserSerializer(serializers.ModelSerializer):
  email = serializers.CharField()
  class Meta:
    model = User
    fields = ['id', 'email', 'first_name', 'last_name']

  def create(self, validated_data):
    user = User(
      email=validated_data['email'],
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name']
    )
    user.set_password(validated_data['password'])
    user.save()
    return user

  def validate_email(self, email):

    if User.objects.filter(email=email).exists():
      raise CustomException(f'User with email {email} already exists', 'email', status.HTTP_400_BAD_REQUEST)

    return email


class ProjectSerializer(serializers.ModelSerializer):

  class Meta:
    model = Project
    fields = ['id', 'name', 'manager',  'description', 'date_created']

  def validate(self, attrs):
    manager = attrs.get('manager')

    if manager is None:
      raise CustomException(f'User does not exists', 'manager', status.HTTP_400_BAD_REQUEST)

    name = attrs.get('name')
    if name is None:
      raise CustomException(f'Name is required', 'name', status.HTTP_400_BAD_REQUEST)

    return attrs

  def create(self, validated_data):
    user = validated_data.get('manager')

    project = Project.objects.create(**validated_data)

    project.members.add(user)

    return project


class TaskSerializer(serializers.ModelSerializer):

  class Meta:
    model = Task
    fields = '__all__'

  def create(self, validated_data):
    return Task.objects.create(**validated_data)

  def validate(self, attrs):
    project: Project = attrs.get('project_id')
    assigned_to: User = attrs.get('assigned_to')
    if not project.members.filter(id=assigned_to.id).exists():
      raise CustomException(f'User {assigned_to} is not a member of {project}', 'project_id', status.HTTP_400_BAD_REQUEST)
    return attrs


class DocumentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Document
    fields = '__all__'

  def create(self, validated_data):
    return Document.objects.create(**validated_data)

  def validate(self, attrs):
    project: Project = attrs.get('project_id')
    created_by: User = attrs.get('created_by')
    if not project.members.filter(id=created_by.id).exists():
      raise CustomException(f'User {created_by} is not a member of {project}', 'project_id', status.HTTP_400_BAD_REQUEST)
    return attrs 
  