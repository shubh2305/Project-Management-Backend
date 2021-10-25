from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
  model = User
  list_display = ['id', 'email', 'date_created', 'last_login']

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)