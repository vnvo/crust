# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crustsessions', '0004_auto_20150921_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='crustclisession',
            name='pid',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
