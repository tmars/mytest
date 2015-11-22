from django.db import models

class Message(models.Model):
    author = models.CharField(max_length=30)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)