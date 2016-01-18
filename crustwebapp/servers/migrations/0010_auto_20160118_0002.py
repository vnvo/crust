# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0009_serveraccount_password_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerAccountMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server', models.ForeignKey(to='servers.Server')),
            ],
        ),
        migrations.RemoveField(
            model_name='serveraccount',
            name='server',
        ),
        migrations.AddField(
            model_name='serveraccountmap',
            name='server_account',
            field=models.ForeignKey(to='servers.ServerAccount'),
        ),
    ]
