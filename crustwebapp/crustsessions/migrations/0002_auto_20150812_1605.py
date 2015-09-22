# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crustsessions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crustclisession',
            name='server',
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crustclisession',
            name='serveraccount',
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crustclisession',
            name='session_id',
            field=models.CharField(max_length=128, unique=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crustclisession',
            name='termination_cause',
            field=models.CharField(max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='crustclisession',
            name='remoteuser',
            field=models.CharField(max_length=128, null=True),
            preserve_default=True,
        ),
    ]
