# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remote_connections', '0003_remoteconnection_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='BanIP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ip', models.CharField(max_length=32)),
            ],
        ),
    ]
