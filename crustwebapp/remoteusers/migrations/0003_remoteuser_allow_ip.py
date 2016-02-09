# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteusers', '0002_auto_20150524_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='remoteuser',
            name='allow_ip',
            field=models.TextField(null=True, blank=True),
        ),
    ]
