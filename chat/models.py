from django.db import models

from users.models import Project, User

# Create your models here.
class ChatMessage(models.Model):
  project: Project = models.ForeignKey(Project, on_delete=models.CASCADE)
  user: User = models.ForeignKey(User, on_delete=models.CASCADE)
  message = models.TextField()
  date_sent = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return self.message