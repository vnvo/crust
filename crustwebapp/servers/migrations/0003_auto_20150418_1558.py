# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0002_auto_20150418_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serveraccount',
            name='telnet_port',
        ),
        migrations.AddField(
            model_name='server',
            name='comment',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serveraccount',
            name='comment',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
