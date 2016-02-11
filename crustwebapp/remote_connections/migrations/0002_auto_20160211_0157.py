# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remote_connections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='remoteconnection',
            name='source_port',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='remoteconnection',
            name='state',
            field=models.CharField(default=b'new', max_length=32),
        ),
        migrations.AlterField(
            model_name='remoteconnection',
            name='terminated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
