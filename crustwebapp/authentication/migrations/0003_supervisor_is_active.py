# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20150415_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='supervisor',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
