
from inspect import _void
from channels.generic.websocket import  AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from chat.serializers import ChatMessageSerializer
from users.models import Project
from users.serializers import UserSerializer
from utils.common import (
  get_messages, 
  get_project,
  get_user, 
  get_user_in_project, 
  serialize_async
)
from channels.db import database_sync_to_async
from .models import ChatMessage

import json

class ChatConsumer(AsyncWebsocketConsumer):

  project = None
  user = None

  async def connect(self):
    try:
      pk: int = self.scope['url_route']['kwargs']['pk']
      params: str = self.scope['query_string'].decode("utf-8")
      email: str = params.split('=')[1]
      await self.accept()
      self.project = await self.get_project(pk)
      user_in_project: bool = await get_user_in_project(email, self.project)
      self.user = await get_user(email)
      if not user_in_project:
        print('Not in project')
        await self.disconnect()  
        await self.send(f'{email} is not allowed to message in {str(self.project)}')

      self.room_name = "Room name!"
      self.room_group_name = 'chat_%s' % pk

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
    except Exception as e:
      print(e)

  async def send_messages(self, event):
    # project = event['project']
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
    await self.create_message(message)
    await self.send(text_data=json.dumps({
      'message': message,
    }))

  async def disconnect(self, close_code):
    print(close_code)
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )

  @database_sync_to_async
  def get_project(self, pk: int) -> Project:
    try:
      return Project.objects.filter(id=pk).first()
    except Exception as e:
      print(e)

  @database_sync_to_async
  def create_message(self, text_message):
    try:
      message = ChatMessage(project=self.project, user=self.user, message=text_message)
      message.save()
    except Exception as e:
      print(e)
  