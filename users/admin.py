from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Task, Project
# Register your models here.

class UserAdmin(admin.ModelAdmin):
  model = User
  list_display = ['id', 'email', 'date_created', 'last_login']

class TaskAdmin(admin.ModelAdmin):
  model = Task
  list_display = ['id', 'title', 'assigned_to', 'done']

class ProjectAdmin(admin.ModelAdmin):
  model = Project
  list_display = ['id', 'manager', 'name', 'date_created']

admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.unregister(Group)