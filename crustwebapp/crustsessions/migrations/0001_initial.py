# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteusers', '0002_auto_20150524_1440'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrustCLISession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'new', max_length=64)),
                ('terminated_at', models.DateTimeField()),
                ('remoteuser', models.ForeignKey(to='remoteusers.RemoteUser', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrustSessionEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_time', models.IntegerField()),
                ('content', models.TextField()),
                ('session', models.ForeignKey(to='crustsessions.CrustCLISession')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
