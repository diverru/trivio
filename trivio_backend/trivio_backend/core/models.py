from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]
    location = models.CharField(max_length=100, null=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(null=False, auto_now=True, editable=False)
    title = models.CharField(max_length=256)
    content = models.TextField(max_length=32768)
    likes = models.ManyToManyField(User, related_name="likes")

    class Meta:
        pass
