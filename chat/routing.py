
from django.urls import path

from .consumers import ChatConsumer

websocket_urlpatterns = [
  path('chat/<int:pk>', ChatConsumer.as_asgi()),
]