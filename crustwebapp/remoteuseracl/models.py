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

    @classmethod
    def get_filtered_server_groups(cls, remote_user):
        acl_list = cls.objects.filter(remote_user=remote_user).all()
        allow_list = set()
        deny_list = set()

        def add_server_group_from_server(acl, sg):
            """
            Only add to allow list if server is allowed, other case is handled
            automatically when allowing/denying a server group directly
            """
            acl_target = sg
            if acl.acl_action == 'allow':
                allow_list.add(acl_target)

        def add_server_group(acl, sg):
            acl_target = sg
            if acl.acl_action == 'allow':
                allow_list.add(acl_target)
            else:
                deny_list.add(acl_target)

        for acl in acl_list:
            if acl.server_account:
                sg = acl.server_account.server.server_group
                add_server_group_from_server(acl, sg)

            elif acl.server:
                sg = acl.server.server_group
                add_server_group_from_server(acl, sg)

            else:
                add_server_group(acl, acl.server_group)

        return list(allow_list - deny_list)

    @classmethod
    def get_filtered_servers_by_group(cls, remote_user, server_group):
        acl_list = cls.objects.filter(remote_user=remote_user).all()
        allow_list = set()
        deny_list = set()

        def add_server_from_serveraccount(acl, server):
            acl_target = server
            if acl.acl_action == 'allow':
                allow_list.add(acl_target)

        for acl in acl_list:
            if acl.server_account:
                if acl.server_account.server.server_group != server_group:
                    continue
                add_server_from_serveraccount(acl, acl.server_account.server)

            elif acl.server:
                if acl.server.server_group != server_group:
                    continue

                if acl.acl_action == 'allow':
                    allow_list.add(acl.server)
                else:
                    deny_list.add(acl.server)

            else:
                if acl.server_group != server_group:
                    continue

                if acl.acl_action == 'allow':
                    for server in acl.server_group.server_set.all():
                        allow_list.add(server)

        return list(allow_list-deny_list)

    @classmethod
    def get_filtered_server_accounts_by_server(cls, remote_user, server):
        acl_list = cls.objects.filter(remote_user=remote_user).all()
        allow_list = set()
        deny_list = set()

        sa_to_acl = {}

        for acl in acl_list:
            if acl.server_account:
                if acl.server_account.server != server:
                    continue
                if acl.acl_action == 'allow':
                    allow_list.add(acl.server_account)
                    sa_to_acl[acl.server_account.id] = acl
                else:
                    deny_list.add(acl.server_account)

            elif acl.server:
                if acl.server != server:
                    continue

                for server_account in acl.server.serveraccount_set.all():
                    if acl.acl_action == 'allow':
                        allow_list.add(server_account)
                        sa_to_acl[server_account.id] = acl
            else:
                sg_servers = acl.server_group.server_set.filter(server=server)
                if sg_servers and acl.acl_action == 'allow':
                    for server_account in sg_servers[0].serveraccount_set.all():
                        allow_list.add(server_account)

        sa_allow_list = list(allow_list-deny_list)
        sa_allow_list_acl = []
        for sa in sa_allow_list:
            sa.apply_acl = sa_to_acl[sa.id]
            sa_allow_list_acl.append(sa)

        return sa_allow_list_acl
