from django.db import models

class RemoteUser(models.Model):
    username = models.CharField(max_length=256, unique=True)
    password = models.CharField(max_length=1024)
    auth_mode = models.CharField(max_length=32, blank=True, null=True, default='local')
    sshv2_public_key = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)
    email = models.CharField(max_length=256, blank=True)
    cell_phone = models.CharField(max_length=256, blank=True)
    comment = models.TextField(blank=True, default='')
    allow_ip = models.TextField(blank=True, null=True)
