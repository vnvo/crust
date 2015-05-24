# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remoteusers', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='remoteuser',
            old_name='sshv2_private_key',
            new_name='sshv2_public_key',
        ),
    ]
