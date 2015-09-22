# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crustsessions', '0003_auto_20150824_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='crustsessionevent',
            name='tty_size_height',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='crustsessionevent',
            name='tty_size_width',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
