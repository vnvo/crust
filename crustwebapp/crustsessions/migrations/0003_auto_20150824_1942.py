# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crustsessions', '0002_auto_20150812_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='crustclisession',
            name='client_ip',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='crustclisession',
            name='client_port',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='crustclisession',
            name='terminated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
