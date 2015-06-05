from django.db import models
from servers.models import ServerAccount, ServerGroup, Server
from remoteusers.models import RemoteUser
from commandgroups.models import CommandGroup

class RemoteUserACL(models.Model):
    remote_user = models.ForeignKey(RemoteUser)
    server_account = models.ForeignKey(ServerAccount, blank=True, null=True)
    server = models.ForeignKey(Server, blank=True, null=True)
    server_group = models.ForeignKey(ServerGroup, blank=True, null=True)
    command_group = models.ForeignKey(CommandGroup, blank=True, null=True)
    acl_action = models.CharField(max_length=32, default='allow')
    is_active = models.BooleanField(default=True)
