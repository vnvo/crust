# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_name', models.CharField(unique=True, max_length=256)),
                ('server_ip', models.CharField(max_length=15)),
                ('timeout', models.IntegerField(blank=True)),
                ('sshv2_port', models.IntegerField(blank=True)),
                ('sshv2_private_key', models.TextField(blank=True)),
                ('telnet_port', models.IntegerField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=256)),
                ('password', models.CharField(max_length=256, blank=True)),
                ('protocol', models.CharField(max_length=64)),
                ('sshv2_private_key', models.TextField(blank=True)),
                ('telnet_port', models.IntegerField(blank=True)),
                ('is_locked', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('server', models.ForeignKey(to='servers.Server')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.CharField(unique=True, max_length=256)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='serveraccount',
            unique_together=set([('server', 'username', 'protocol')]),
        ),
        migrations.AddField(
            model_name='server',
            name='server_group',
            field=models.ForeignKey(to='servers.ServerGroup'),
            preserve_default=True,
        ),
    ]
