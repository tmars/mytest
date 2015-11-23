# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytest', '0006_task_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='results',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
    ]
