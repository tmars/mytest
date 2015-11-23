#encoding=utf8
import json
import subprocess
import os

from django.utils import timezone
from django.db import models
from django.conf import settings

class Message(models.Model):
    author = models.CharField(max_length=30)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField()
    session_key = models.CharField(max_length=32, default='')
    task = models.ForeignKey('Task', null=True, blank=True, default=None)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        return super(Message, self).save(*args, **kwargs)

class Info(models.Model):
    session_key = models.CharField(max_length=32, default='')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)    

class Task(models.Model):
    command = models.CharField(max_length=30)
    args = models.CharField(max_length=1000)
    results = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=32, default='')
    is_active = models.BooleanField(default=True)

    def save_results(self, results):
        self.results = json.dumps(results)
        self.save()

    def save_message(self, result):
        m = Message()
        m.author = u'Бот'
        m.content = u'Задача %d завершена, результат: %s' % (self.id, result)
        m.session_key = self.session_key
        m.save()

    @staticmethod
    def create(command, args, session_key):
        t = Task()
        t.command = command
        t.set_args(args) 
        t.session_key = session_key
        t.save()

        m = Message()
        m.content = u'Задача %d поставлена в очередь' % t.id
        m.session_key = session_key
        m.author = 'Бот'
        m.save()

        return t

    # запуск без ожидания результата
    def run(self):
        cmd = ['python', os.path.join(settings.BASE_DIR, 'manage.py'), 'run_task', str(self.id)]
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        o, e = p.communicate()
        print o
        print e
            # stdout=subprocess.PIPE, 
            # stderr=subprocess.STDOUT
        # )

    def set_args(self, args):
        try:
            self.args = json.dumps(args)
        except:
            pass

    def get_args(self):
        try:
            return json.loads(self.args)
        except:
            return {}