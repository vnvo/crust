from django.db import models
from remoteusers.models import RemoteUser
from servers.models import Server, ServerAccount


SESSION_ESTAB = 'ESTABLISHED'
SESSION_RUN = 'RUNNING'
SESSION_CLOSED_NORMAL = 'CLOSED-NORMAL'
SESSION_CLOSED_LOST = 'CLOSED-LOST'

# Session for command line interface
class CrustCLISession(models.Model):
    session_id = models.CharField(max_length=128, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remoteuser = models.CharField(max_length=128, null=True)
    serveraccount = models.CharField(max_length=128, blank=True, null=True)
    server = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=64, default='new')
    terminated_at = models.DateTimeField(null=True, blank=True)
    termination_cause = models.CharField(max_length=256, blank=True, null=True)
    client_ip = models.CharField(max_length=32, null=True, blank=True)
    client_port = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s: %s@%s -> %s'%(
            self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            self.remoteuser, self.client_ip,
            self.serveraccount
        )


class CrustSessionEvent(models.Model):
    session = models.ForeignKey(CrustCLISession)
    #event_time: time in seconds since start of session
    tty_size_width = models.IntegerField(blank=True, null=True)
    tty_size_height = models.IntegerField(blank=True, null=True)
    event_time = models.IntegerField()
    #the screen user sees at that moment
    content = models.TextField()
