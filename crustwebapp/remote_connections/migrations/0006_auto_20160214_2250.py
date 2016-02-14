# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remote_connections', '0005_auto_20160214_2205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='remoteconnection',
            old_name='temrination_cause',
            new_name='termination_cause',
        ),
    ]
