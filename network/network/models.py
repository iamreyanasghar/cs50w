from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post")
    content = models.TextField()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="thread")