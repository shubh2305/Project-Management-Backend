from django.utils.encoding import force_text

from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from .models import User, Task, Project

import json

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
  project_id = serializers.SerializerMethodField('get_project_id')

  class Meta:
    model = Task
    fields = '__all__'

  def get_project_id(self, obj):
    project_id = self.context.get('project_id')
    if project_id:
      return project_id if Project.objects.filter(id=project_id).exists() else None

  def create(self, validated_data):
    print('[This is line 82, serializers.py]', validated_data)
    # email, title = validated_data.get('email'), validated_data.get('title')

    # user = User.objects.get(email=email)

    # task = Task(
    #   title=title,
    #   description=validated_data.get('description'),
    #   assigned_to=user,
    # )
    # task.save()

    # return task

  def validate(self, data):
    self.project_id = data.get('project_id')
    title = data.get('title')
    assigned_to = data.get('assigned_to')
    print(assigned_to)
    print('[This is line 99, serializers.py]', data)
    project = Project.objects.filter(id=self.project_id).first()
    print(project)
    # email = data.get('email')
    # if email is None: 
    #   raise CustomException(f'Email is required', 'assigned_to', status.HTTP_400_BAD_REQUEST)

    # if User.objects.filter(email=email).exists():
    #   raise CustomException(f'User with {email} does not exists', 'assigned_to', status.HTTP_400_BAD_REQUEST)

    # title = data.get('title')
    # if title is None:
    #   raise CustomException('Title is required', 'title', status.HTTP_400_BAD_REQUEST)

    return data