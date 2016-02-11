# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('terminated_at', models.DateTimeField()),
                ('username', models.CharField(max_length=256)),
                ('source_ip', models.CharField(max_length=32)),
                ('successful', models.BooleanField(default=True)),
                ('fail_reason', models.CharField(max_length=512, null=True, blank=True)),
            ],
        ),
    ]
