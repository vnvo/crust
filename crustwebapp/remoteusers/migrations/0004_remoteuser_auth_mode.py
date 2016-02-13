# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteusers', '0003_remoteuser_allow_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='remoteuser',
            name='auth_mode',
            field=models.CharField(default=b'local', max_length=32, null=True, blank=True),
        ),
    ]
