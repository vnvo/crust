# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=256)),
                ('password', models.CharField(max_length=1024)),
                ('sshv2_private_key', models.TextField(blank=True)),
                ('is_locked', models.BooleanField(default=False)),
                ('email', models.CharField(max_length=256, blank=True)),
                ('cell_phone', models.CharField(max_length=256, blank=True)),
                ('comment', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
