from django.db import models
from authentication.models import Supervisor
from servers.models import ServerAccount, ServerGroup, Server
from remoteusers.models import RemoteUser
from commandgroups.models import CommandGroup

class SupervisorACL(models.Model):
    supervisor = models.ForeignKey(Supervisor)
    remote_user = models.ForeignKey(RemoteUser, blank=True, null=True)
    server = models.ForeignKey(Server, blank=True, null=True)
    server_group = models.ForeignKey(ServerGroup, blank=True, null=True)
    command_group = models.ForeignKey(CommandGroup, blank=True, null=True)
    acl_action = models.CharField(max_length=32, default='allow')
    is_active = models.BooleanField(default=True)
