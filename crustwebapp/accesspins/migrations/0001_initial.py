# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0010_auto_20160118_0002'),
        ('remoteusers', '0002_auto_20150524_1440'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessPin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pin', models.CharField(unique=True, max_length=64)),
                ('validation_mode', models.CharField(default=b'one-time', max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('first_used_at', models.DateTimeField(null=True, blank=True)),
                ('exp_after_creation', models.IntegerField(null=True, blank=True)),
                ('exp_after_first_login', models.IntegerField(null=True, blank=True)),
                ('exp_on_date', models.DateTimeField(null=True, blank=True)),
                ('remote_user', models.ForeignKey(to='remoteusers.RemoteUser')),
                ('server', models.ForeignKey(to='servers.Server')),
                ('server_account', models.ForeignKey(to='servers.ServerAccount')),
                ('supervisor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
