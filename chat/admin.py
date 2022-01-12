from django.contrib import admin

from chat.models import ChatMessage

# Register your models here.
class ChatMessageAdmin(admin.ModelAdmin):
  model = ChatMessage
  list_display = ['id', 'project', 'user', 'message', 'date_sent']

admin.site.register(ChatMessage, ChatMessageAdmin)
