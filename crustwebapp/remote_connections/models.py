from django.db import models

class RemoteConnection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    terminated_at = models.DateTimeField(null=True, blank=True)
    mode = models.CharField(max_length=32, default='normal')
    state = models.CharField(max_length=32, default='new')
    username = models.CharField(max_length=256)
    source_ip = models.CharField(max_length=32)
    source_port = models.IntegerField(default=0)
    successful = models.BooleanField(default=True)
    fail_reason = models.CharField(max_length=512, blank=True, null=True)

    def __unicode__(self):
        return '%s(%s)- %s - %s/%s'%(
            self.username, self.source_ip, self.state,
            self.created_at, self.terminated_at
        )
