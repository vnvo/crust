from datetime import timedelta
from django.db import models
from remoteusers.models import RemoteUser
from authentication.models import Supervisor
from servers.models import Server, ServerAccount

class AccessPin(models.Model):
    supervisor = models.ForeignKey(Supervisor)
    remote_user = models.ForeignKey(RemoteUser)
    server = models.ForeignKey(Server)
    server_account = models.ForeignKey(ServerAccount)

    pin = models.CharField(max_length=64, unique=True)
    validation_mode = models.CharField(max_length=64, default='one-time')
    created_at = models.DateTimeField(auto_now_add=True)
    first_used_at = models.DateTimeField(null=True, blank=True) #first successful login

    exp_after_creation = models.IntegerField(blank=True, null=True) #seconds
    exp_after_first_login = models.IntegerField(blank=True, null=True) #seconds
    exp_on_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.pin

    @property
    def exp_after_creation_formatted(self):
        if self.exp_after_creation:
            td = timedelta(seconds=self.exp_after_creation)
            return '%d days %02d:%02d:%02d'%(
                td.days, td.seconds/3600,(td.seconds/60)%60, td.seconds%60)
        return None

    @property
    def exp_after_first_login_formatted(self):
        if self.exp_after_first_login:
            td = timedelta(seconds=self.exp_after_first_login)
            return '%d days %02d:%02d:%02d'%(
                td.days, td.seconds/3600,(td.seconds/60)%60, td.seconds%60)
        return None
