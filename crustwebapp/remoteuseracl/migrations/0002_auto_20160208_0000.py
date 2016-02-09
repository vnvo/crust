# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteuseracl', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='remoteuseracl',
            name='limit_days',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='remoteuseracl',
            name='limit_hours_end',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='remoteuseracl',
            name='limit_hours_start',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
