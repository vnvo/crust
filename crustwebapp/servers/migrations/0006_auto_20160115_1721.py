# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0005_auto_20160115_1716'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serveraccount',
            name='server_group',
        ),
        migrations.AddField(
            model_name='serveraccount',
            name='assign_server_group',
            field=models.BooleanField(default=False),
        ),
    ]
