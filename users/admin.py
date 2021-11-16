from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Task
# Register your models here.

class UserAdmin(admin.ModelAdmin):
  model = User
  list_display = ['id', 'email', 'date_created', 'last_login']

class TaskAdmin(admin.ModelAdmin):
  model = Task
  list_display = ['id', 'title', 'assigned_to', 'done']

admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.unregister(Group)