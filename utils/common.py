from channels.db import database_sync_to_async
from rest_framework.response import Response
from rest_framework import status 
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserSerializer


# Generate tokens for user


def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)

  return {
    'refresh': str(refresh),
    'access': str(refresh.access_token),
  }

# serializing list of model objects into dictionaries 
def serialize(model_list, Serializer):
  serialized = [Serializer(model).data for model in model_list]
  return serialized

@database_sync_to_async
def serialize_async(model_list, Serializer):
  serialized = [Serializer(model).data for model in model_list]
  for message in serialized:
    user = User.objects.filter(id=message['user']).first()
    message['user'] = UserSerializer(user).data
  return serialized

def update(data, instance, Serializer) -> Response:
  print(data)
  serializer = Serializer(instance, data=data, partial=True)

  print(data)
  if serializer.is_valid(raise_exception=True):
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
  return Response(serializer.error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)