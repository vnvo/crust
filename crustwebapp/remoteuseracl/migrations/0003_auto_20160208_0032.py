# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteuseracl', '0002_auto_20160208_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remoteuseracl',
            name='limit_hours_end',
            field=models.IntegerField(default=-1, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='remoteuseracl',
            name='limit_hours_start',
            field=models.IntegerField(default=-1, null=True, blank=True),
        ),
    ]
