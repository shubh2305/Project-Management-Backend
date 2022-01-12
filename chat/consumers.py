
from channels.db import database_sync_to_async
from channels.generic.websocket import  AsyncWebsocketConsumer

from chat.models import ChatMessage
from chat.serializers import ChatMessageSerializer
from users.models import Project, User
from users.serializers import ProjectSerializer
from utils.common import serialize, serialize_async

import json

@database_sync_to_async
def get_project(pk: int) -> Project:
  return Project.objects.filter(id=pk).first()

@database_sync_to_async
def get_user_in_project(email: str, project: Project) -> bool:
  return User.objects.filter(email=email).first() in project.members.all()

@database_sync_to_async
def get_messages(project: Project) -> list:
  return ChatMessage.objects.filter(project=project).order_by('-date_sent')

class ChatConsumer(AsyncWebsocketConsumer):

  project = None

  async def connect(self):
    pk: int = self.scope['url_route']['kwargs']['pk']
    params: str = self.scope['query_string'].decode("utf-8")
    email: str = params.split('=')[1]
    self.project: Project = await get_project(pk)
    user_in_project: bool = await get_user_in_project(email, self.project)

    if not user_in_project:
      print('Not in project')
      await self.close()  
      await self.send(f'{email} is not allowed to message in {str(self.project)}')

    self.room_name = self.project.name
    self.room_group_name = 'chat_%s' % pk

    await self.accept()
    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )

    await self.channel_layer.group_send(
      self.room_group_name,
      {
        'type': "send_messages"
      }
    )

  async def send_messages(self, event):
    # project = event['project']
    print(event)
    messages = await get_messages(self.project)
    await self.send(text_data=json.dumps({
      "messages": await serialize_async(messages, ChatMessageSerializer)
    }))

  async def receive(self, text_data=None):
    text_message_json = json.loads(text_data)
    message = text_message_json['message']
    await self.channel_layer.group_send(
      self.room_group_name,
      {
        "type": "chat_message",
        "message": message
      }
    )

  async def chat_message(self, event):
    message = event['message']
    await self.send(text_data=json.dumps({
      'message': message
    }))

  async def disconnect(self, close_code):
    print(close_code)
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )
  