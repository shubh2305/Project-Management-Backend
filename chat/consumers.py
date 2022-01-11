from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import  AsyncWebsocketConsumer
from users.models import Project, User

import time
import asyncio
import json

@database_sync_to_async
def get_project(pk: int) -> Project:
  return Project.objects.filter(id=pk).first()

@database_sync_to_async
def get_user_in_project(email: str, project: Project) -> bool:
  return User.objects.filter(email=email).first() in project.members.all()

class ChatConsumer(AsyncWebsocketConsumer):


  async def connect(self):
    pk: int = self.scope['url_route']['kwargs']['pk']
    params: str = self.scope['query_string'].decode("utf-8")
    email: str = params.split('=')[1]
    project: Project = await get_project(pk)
    user_in_project: bool = await get_user_in_project(email, project)

    if not user_in_project:
      print('Not in project')
      await self.close()  
      await self.send(f'{email} is not allowed to message in {str(project)}')

    self.room_name = project.name
    self.room_group_name = 'chat_%s' % pk

    await self.accept()
    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )


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
  