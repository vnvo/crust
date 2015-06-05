# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0003_auto_20150418_1558'),
        ('remoteusers', '0002_auto_20150524_1440'),
        ('commandgroups', '0002_commandgroup_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteUserACL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('acl_action', models.CharField(default=b'allow', max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('command_group', models.ForeignKey(blank=True, to='commandgroups.CommandGroup', null=True)),
                ('remote_user', models.ForeignKey(to='remoteusers.RemoteUser')),
                ('server', models.ForeignKey(blank=True, to='servers.Server', null=True)),
                ('server_account', models.ForeignKey(blank=True, to='servers.ServerAccount', null=True)),
                ('server_group', models.ForeignKey(blank=True, to='servers.ServerGroup', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
