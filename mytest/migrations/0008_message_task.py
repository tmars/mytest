# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytest', '0007_task_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='task',
            field=models.ForeignKey(default=None, blank=True, to='mytest.Task', null=True),
        ),
    ]
