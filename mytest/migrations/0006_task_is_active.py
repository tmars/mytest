# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytest', '0005_auto_20151123_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
