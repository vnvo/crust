# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0007_servergroupaccount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serveraccount',
            name='assign_server_group',
        ),
    ]
