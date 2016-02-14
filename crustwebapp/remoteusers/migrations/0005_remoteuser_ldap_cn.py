# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteusers', '0004_remoteuser_auth_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='remoteuser',
            name='ldap_cn',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
    ]
