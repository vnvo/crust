# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remote_connections', '0004_banip'),
    ]

    operations = [
        migrations.AddField(
            model_name='remoteconnection',
            name='pid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='remoteconnection',
            name='temrination_cause',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
    ]
