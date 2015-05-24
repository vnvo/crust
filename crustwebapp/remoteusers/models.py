from django.db import models

class RemoteUser(models.Model):
    username = models.CharField(max_length=256, unique=True)
    password = models.CharField(max_length=1024)
    sshv2_public_key = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)
    email = models.CharField(max_length=256, blank=True)
    cell_phone = models.CharField(max_length=256, blank=True)
    comment = models.TextField(blank=True, default='')
