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

    @classmethod
    def get_cooked_acls(cls, remote_user):
        """
        Return all resulting mappings of RemoteUsers to ServerAccounts
        for this RemoteUserACL (allowed list)
        """
        allow_dict = {}
        deny_list = []
        acl_list = cls.objects.filter(remote_user=remote_user).all()

        def add_server_account(acl, sa):
            acl_target = sa.get_server_account_repr
            if acl.acl_action == 'allow':
                allow_dict[acl_target] = sa
            else:
                deny_list.append(acl_target)

        for acl in acl_list:
            if acl.server_account:
                add_server_account(acl, acl.server_account)
            elif acl.server:
                for server_account in acl.server.serveraccount_set.all():
                    add_server_account(acl, server_account)
            else:
                for server in acl.server_group.server_set.all():
                    for server_account in server.serveraccount_set.all():
                        add_server_account(acl, server_account)

        #filter out deny list:
        for acl_target in deny_list:
            if acl_target in allow_dict:
                del allow_dict[acl_target]

        return allow_dict
