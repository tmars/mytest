# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytest', '0002_auto_20151122_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='session_key',
            field=models.CharField(default=b'', max_length=32),
        ),
    ]
