# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0008_remove_serveraccount_assign_server_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='serveraccount',
            name='password_mode',
            field=models.CharField(default=b'local', max_length=128),
        ),
    ]
