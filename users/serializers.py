from enum import IntEnum
from django.db.models import fields
from django.utils.encoding import force_text

from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from .models import Document, User, Task, Project, Document

import datetime

class CustomException(APIException):
  status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
  default_detail = 'Server Error'

  def __init__(self, detail, field, status_code):
    if status_code is not None:self.status_code = status_code
    if detail is not None:
      self.detail = {field: force_text(detail)}
    else: self.detail = {'detail': force_text(self.default_detail)}


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` and 'exclude' argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude is not None:
            not_allowed = set(exclude)
            for exclude_name in not_allowed:
                self.fields.pop(exclude_name)

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
  
  def update(self, instance, validated_data):
    instance.email = validated_data.get('email', instance.email)
    instance.first_name = validated_data.get('first_name', instance.first_name)
    instance.last_name = validated_data.get('last_name', instance.last_name)
    instance.save()
    return instance

  def validate_email(self, email):

    if User.objects.filter(email=email).exists():
      raise CustomException(f'User with email {email} already exists', 'email', status.HTTP_400_BAD_REQUEST)

    return email


class ProjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = Project
    fields = ['id', 'name', 'manager', 'description', 'date_created']

  def validate(self, attrs):
    manager = attrs.get('manager', None)
    name = attrs.get('name', None)

    if manager is None:
      raise CustomException(f'Manager is required', 'manager', status.HTTP_400_BAD_REQUEST)

    if name is None:
      raise CustomException(f'Project name is required', 'name', status.HTTP_400_BAD_REQUEST)
    return attrs

  def create(self, validated_data):
    user = validated_data.get('manager')

    project = Project.objects.create(**validated_data)

    project.members.add(user)

    return project

  def update(self, instance, validated_data):
    print(validated_data)
    print(self.members)
    # if validated_data.get('users') and len(validated_data.get('users')) > 0:
    #   users = validated_data.get('users')
    #   users_model_list = [User.objects.filter(email=user) for user in users]
    #   for user in users_model_list:
    #     instance.members.add(user)

    # instance.name = validated_data.get('name', instance.name)
    # instance.description = validated_data.get('description', instance.description)
    # instance.manager = validated_data.get('manager', instance.manager)
    return instance


class ProjectUpdateSerializer(DynamicFieldsModelSerializer):
  class Meta:
    model = Project
    fields = ['id', 'name', 'description', 'date_created', 'manager', 'members']

  def update(self, instance, validated_data):
    
    members = validated_data.get("members", None)
    
    if members is not None:
      for member in members:
        instance.members.add(member)

    instance.name = validated_data.get("name", instance.name)
    instance.description = validated_data.get("description", instance.description)
    instance.manager = validated_data.get("manager", instance.manager)

    instance.save()

    return instance

class TaskSerializer(serializers.ModelSerializer):

  class Meta:
    model = Task
    fields = '__all__'

  def create(self, validated_data):
    return Task.objects.create(**validated_data)

  def validate(self, attrs):
    project: Project = attrs.get('project_id', None)
    if project is None:
      return attrs
    assigned_to: User = attrs.get('assigned_to')
    if not project.members.filter(id=assigned_to.id).exists():
      raise CustomException(f'User {assigned_to} is not a member of {project}', 'project_id', status.HTTP_400_BAD_REQUEST)
    return attrs

  def update(self, instance, validated_data):
    completed = validated_data.pop("done", None)
    if completed:
      instance.date_finished = datetime.datetime.now()
      instance.done = True
    else:
      instance.date_finished = None
      instance.done = False
    
    instance.title = validated_data.get("title", instance.title)
    instance.description = validated_data.get("description", instance.description)
    instance.assigned_to = validated_data.get("assigned_to", instance.assigned_to)
    
    return instance

class DocumentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Document
    fields = '__all__'

  def create(self, validated_data):
    return Document.objects.create(**validated_data)

  def update(self, instance, validated_data):
    instance.title = validated_data.get("title", instance.title)
    instance.file = validated_data.get("file", instance.file)

    instance.save()

    return instance

  def validate(self, attrs):
    project: Project = attrs.get('project_id')
    if project is None:
      return attrs
    created_by: User = attrs.get('created_by')
    if not project.members.filter(id=created_by.id).exists():
      raise CustomException(f'User {created_by} is not a member of {project}', 'project_id', status.HTTP_400_BAD_REQUEST)
    return attrs 

  