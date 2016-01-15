# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0006_auto_20160115_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerGroupAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_account', models.ForeignKey(to='servers.ServerAccount')),
                ('server_group', models.ForeignKey(to='servers.ServerGroup')),
            ],
        ),
    ]
