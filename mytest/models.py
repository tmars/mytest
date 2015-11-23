#encoding=utf8

from django.utils import timezone
from django.db import models

class Message(models.Model):
    author = models.CharField(max_length=30)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField()
    session_key = models.CharField(max_length=32, default='')

    def save(self, *args, **kwargs):
    	if not self.created_at:
    		self.created_at = timezone.now()
    	return super(Message, self).save(*args, **kwargs)