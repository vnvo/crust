# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteuseracl', '0003_auto_20160208_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remoteuseracl',
            name='limit_days',
            field=models.CharField(default=b'', max_length=32, null=True, blank=True),
        ),
    ]
