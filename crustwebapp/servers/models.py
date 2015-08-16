from django.db import models
from authentication.models import Supervisor

class ServerGroup(models.Model):
    '''
    @name ServerGroup
    @desc To group Servers together for better management
    '''
    supervisor = models.ForeignKey(Supervisor, null=True)
    group_name = models.CharField(max_length=256, unique=True)
    comment = models.TextField(blank=True)

    @property
    def get_server_count(self):
        return self.server_set.count()

    @property
    def serveraccounts_count(self):
        sa_count = 0
        for s in self.server_set.all():
            sa_count += s.serveraccount_set.count()

        return sa_count


class Server(models.Model):
    '''
    @name Server
    @desc Represents a reachable element in network
    '''
    #### General Fields
    server_group = models.ForeignKey(ServerGroup)
    server_name = models.CharField(max_length=256, unique=True)
    server_ip = models.CharField(max_length=15)

    #### Connection Info Fields
    timeout = models.IntegerField(blank=True, null=True)
    sshv2_port = models.IntegerField(blank=True, null=True)
    sshv2_private_key = models.TextField(blank=True)
    telnet_port = models.IntegerField(blank=True, null=True)

    comment = models.TextField(blank=True, default='')

    def __unicode__(self):
        return '%s (%s)'%(self.server_name, self.server_ip)

    @property
    def get_serveraccount_count(self):
        return self.serveraccount_set.count()

class ServerAccount(models.Model):
    '''
    @name ServerAccount
    @desc To define a way to connect to specified Server
    '''
    server = models.ForeignKey(Server)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256, blank=True)

    protocol = models.CharField(max_length=64)
    sshv2_private_key = models.TextField(blank=True)

    is_locked = models.BooleanField(default=False)
    comment = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('server', 'username', 'protocol')

    def __unicode__(self):
        return '%s://%s@%s'%(
            self.protocol,
            self.username,
            self.server
        )

    @property
    def get_server_account_repr(self):
        return '%s://%s@%s'%(
            self.protocol,
            self.username,
            self.server.server_name
        )
