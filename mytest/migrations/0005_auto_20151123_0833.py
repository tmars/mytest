# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mytest', '0004_task'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='_args',
            new_name='args',
        ),
    ]
