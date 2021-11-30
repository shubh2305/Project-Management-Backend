from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import fields
# Create your models here.

class UserManager(BaseUserManager):

  def create_user(self, email, password):
    if not email:
      raise ValueError('Email is required')
    if not password:
      raise ValueError('Password is required')

    user = self.model(email=self.normalize_email(email))

    user.set_password(password)

    user.save(using=self._db)

    return user

  def create_superuser(self, email, password):
    user = self.create_user(email=self.normalize_email(email), password=password)
    
    user.is_admin = True
    user.is_superuser = True
    user.is_staff = True

    user.save(using=self._db)



class User(AbstractBaseUser):
  email = models.EmailField(unique=True, max_length=100)
  password = models.CharField(max_length=300)
  first_name = models.CharField(max_length=100, null=True)
  last_name = models.CharField(max_length=100, null=True)
  date_created = models.DateTimeField(auto_now_add=True)
  last_login = models.DateTimeField(auto_now=True)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  is_superuser = models.BooleanField(default=False)
  is_admin = models.BooleanField(default=False)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = [] # email and password are required by default

  objects = UserManager()

  def __str__(self) -> str:
    return self.email

  def has_perm(self, perm, obj=None) -> bool:
    # Does user has specific permissions ?
    return self.is_admin

  def has_module_perms(self, app_label) -> bool:
    return True


class Task(models.Model):
  assigned_to = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
  title = models.CharField(max_length=500, null=True)
  description = models.TextField(null=True, blank=True)
  done = models.BooleanField(default=False)
  date_created = models.DateTimeField(auto_now_add=True)
  date_finished = models.DateTimeField(null=True, blank=True)

  def __str__(self) -> str:
    return self.title

class Project(models.Model):
  manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
  name = models.CharField(max_length=300, null=True)
  description = models.TextField(null=True, blank=True)
  members = models.ManyToManyField(User, related_name='developers')
  tasks = models.ManyToManyField(Task)
  date_created = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return self.name

class Document(models.Model):
  project_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
  created_by = models.ForeignKey(User, on_delete=models.CASCADE)
  title = models.CharField(max_length=500)
  file = models.FileField(upload_to='documents/')
  uploaded_at = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return self.title

    


  