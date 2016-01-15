# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0004_servergroup_supervisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='serveraccount',
            name='server_group',
            field=models.ForeignKey(blank=True, to='servers.ServerGroup', null=True),
        ),
        migrations.AlterField(
            model_name='serveraccount',
            name='server',
            field=models.ForeignKey(blank=True, to='servers.Server', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='serveraccount',
            unique_together=set([]),
        ),
    ]
