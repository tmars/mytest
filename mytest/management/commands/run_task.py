#coding=utf8
from django.core.management.base import BaseCommand, CommandError

from mytest.models import *

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('task_id', type=int)

    def handle(self, *args, **options):
        try:
            t = Task.objects.get(pk=options['task_id'])
        except:
            print u'Task %s not found' % options['task_id']

        if not t.is_active:
            print u'Task %s executed' % t.id
            return 
        
        import mytest.tasks as tasks
        if not hasattr(tasks, t.command):
            print u'Not found command %s for task %s' % (t.command, t.id)
            return

        print u'Start task %s' % t.id
        cmd = getattr(tasks, t.command)
        cmd(t, **t.get_args())
        
        t.is_active = False
        t.save()

        print u'Stop task'
        