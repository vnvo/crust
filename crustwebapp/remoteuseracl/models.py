import re
from datetime import datetime
from django.db import models
from django.db.models import Q
from servers.models import ServerAccount, ServerGroup, Server
from servers.models import ServerGroupAccount, ServerAccountMap
from remoteusers.models import RemoteUser
from commandgroups.models import CommandGroup

dow = dict(
    zip(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        range(7)))
dow_nums = {v:k for k,v in dow.iteritems()}

def get_dow_name(day_num):
    return dow_nums.get(int(day_num))

def get_dow_number(day_name):
    return dow.get(day_name)


class RemoteUserACL(models.Model):
    remote_user = models.ForeignKey(RemoteUser)
    server_account = models.ForeignKey(ServerAccount, blank=True, null=True)
    server = models.ForeignKey(Server, blank=True, null=True)
    server_group = models.ForeignKey(ServerGroup, blank=True, null=True)
    command_group = models.ForeignKey(CommandGroup, blank=True, null=True)
    acl_action = models.CharField(max_length=32, default='allow')
    is_active = models.BooleanField(default=True)
    limit_hours_start = models.IntegerField(null=True, blank=True, default=-1)
    limit_hours_end = models.IntegerField(null=True, blank=True, default=-1)
    limit_days = models.CharField(blank=True, null=True, max_length=32, default='')

    def __unicode__(self):
        return 'RU-ACL(%s): %s'%(
            self.id, self.remote_user.username,
        )

    @property
    def get_limit_hours_repr(self):
        if self.limit_hours_start > -1:
            return '%s - %s'%(self.limit_hours_start, self.limit_hours_end)
        return ''
    @property
    def get_limit_days_repr(self):
        if self.limit_days:
            l = [int(item) for item in self.limit_days.split(',')]
            return ','.join(get_dow_name(item) for item in l)
        return ''

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
        now = datetime.now()
        wday = str(now.weekday())
        acl_list = cls.objects.filter(
            remote_user=remote_user
        ).filter(is_active=True).filter(
            Q(Q(limit_hours_start__lte=now.hour)&
              Q(limit_hours_end__gt=now.hour))|
            Q(limit_hours_start=-1)
        ).filter(Q(limit_days__contains=wday)|Q(limit_days=None))
        allow_list = set()
        deny_list = set()

        def add_server_group_from_server(acl, sg):
            """
            Only add to allow list if server is allowed, other case is handled
            automatically when allowing/denying a server group directly
            """
            if acl.acl_action == 'allow':
                allow_list.add(sg)

        def add_server_group(acl, sg):
            if acl.acl_action == 'allow':
                allow_list.add(sg)
            else:
                deny_list.add(sg)

        for acl in acl_list:
            if acl.server_account:
                for sga in acl.server_account.servergroupaccount_set.all():
                    add_server_group_from_server(acl, sga.server_group)

            elif acl.server:
                sg = acl.server.server_group
                add_server_group_from_server(acl, sg)

            else:
                add_server_group(acl, acl.server_group)

        data = list(allow_list - deny_list)
        data.sort(key=lambda x: x.group_name)
        return data

    @classmethod
    def get_filtered_servers_by_group(cls, remote_user, server_group):
        print 'get servers by group: ',remote_user, server_group
        now = datetime.now()
        wday = str(now.weekday())
        acl_list = cls.objects.filter(
            remote_user=remote_user
        ).filter(is_active=True).filter(
            Q(Q(limit_hours_start__lte=now.hour)&
              Q(limit_hours_end__gt=now.hour))|
            Q(limit_hours_start=-1)
        ).filter(Q(limit_days__contains=wday)|Q(limit_days=None)).all()
        allow_list = set()
        deny_list = set()

        def add_server_from_serveraccount(acl, server):
            acl_target = server
            if acl.acl_action == 'allow':
                allow_list.add(acl_target)

        for acl in acl_list:
            if acl.server_account:
                server_group_accounts = ServerGroupAccount.objects.filter(
                    server_account=acl.server_account
                ).filter(server_group=server_group)

                if not server_group_accounts:
                    continue
                for sga in server_group_accounts:
                    for server in sga.server_group.server_set.all():
                        add_server_from_serveraccount(acl, server)#@todo clean this

            elif acl.server:
                if acl.server.server_group != server_group:
                    continue

                if acl.acl_action == 'allow':
                    allow_list.add(acl.server)
                else:
                    deny_list.add(acl.server)

            else:
                print acl
                if acl.server_group != server_group:
                    continue

                if acl.acl_action == 'allow':
                    for server in acl.server_group.server_set.all():
                        allow_list.add(server)

        data = list(allow_list-deny_list)
        data.sort(key=lambda x: x.server_name)
        return data

    @classmethod
    def get_filtered_server_accounts_by_server(cls, remote_user, server):
        now = datetime.now()
        wday = str(now.weekday())
        acl_list = cls.objects.filter(
            remote_user=remote_user
        ).filter(is_active=True).filter(
            Q(Q(limit_hours_start__lte=now.hour)&
              Q(limit_hours_end__gt=now.hour))|
            Q(limit_hours_start=-1)
        ).filter(Q(limit_days__contains=wday)|Q(limit_days=None)).all()
        allow_list = set()
        deny_list = set()

        sa_to_acl = {}

        server_group = server.server_group
        server_group_account = server

        for acl in acl_list:
            if acl.server_account:
                server_account_maps = ServerAccountMap.objects.filter(
                    server=server
                ).filter(server_account=acl.server_account)
                if not server_account_maps:
                    continue

                if acl.acl_action == 'allow':
                    sa = server_account_maps[0].server_account
                    sa.server=server
                    allow_list.add(sa)
                    sa_to_acl[sa.id] = acl
                else:
                    deny_list.add(sa)

            elif acl.server:
                if acl.server != server:
                    continue

                for sam in acl.server.serveraccountmap_set.all():
                    sa = sam.server_account
                    sa.server = server
                    if acl.acl_action == 'allow':
                        allow_list.add(sa)
                        sa_to_acl[sa.id] = acl
            else:
                sg_servers = acl.server_group.server_set.filter(server_ip=server.server_ip)
                print sg_servers
                if sg_servers and acl.acl_action == 'allow':
                    for sam in sg_servers[0].serveraccountmap_set.all():
                        sa = sam.server_account
                        sa.server = server
                        allow_list.add(sa)
                        sa_to_acl[sa.id] = acl

                #add server group account
                print 'checking server group accounts', server
                sga_list = ServerGroupAccount.objects.filter(server_group=server.server_group).all()
                for sga in sga_list:
                    print 'adding sga: ', sga
                    sga.server_account.server = server #dirty and unsafe, fix this.
                    allow_list.add(sga.server_account)
                    sa_to_acl[sga.server_account.id] = acl

        sa_allow_list = list(allow_list-deny_list)
        sa_allow_list_acl = []
        for sa in sa_allow_list:
            #try:
            sa.apply_acl = sa_to_acl[sa.id]
            #except:
            #    sa.apply_acl = None
            #    continue

            sa_allow_list_acl.append(sa)

        print sa_allow_list_acl
        sa_allow_list_acl.sort(key=lambda x:x.username)
        return sa_allow_list_acl

    @classmethod
    def check_direct_access(self, remote_user, proto, server_account_username, server_name_ip):
        print 'check-direct-access: %s, %s, %s, %s'%(
            remote_user, proto, server_account_username, server_name_ip
        )

        server_account = ServerAccount.objects.filter(
            username = server_account_username
        ).filter(protocol=proto)
        if server_account:
            server_account = server_account[0]
        else:
            print 'server_account not found!'
            return None

        if re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", server_name_ip):
            server = Server.objects.filter(server_ip = server_name_ip)
        else:
            server = Server.objects.filter(server_name=server_name_ip)
        if server:
            server = server[0]
        else:
            print 'server not found!'
            return None

        #check server account and server relation
        sam = server_account.serveraccountmap_set.filter(server=server)
        if not sam: # we should check by server group relation
            sga = server_account.servergroupaccount_set.filter(server_group=server.server_group)
            if not sga:
                print 'no relation for server_account and server!'
                return None

        server_account.server = server #@todo: dirty, fix this mechanism
        #check acls
        now = datetime.now()
        wday = str(now.weekday())
        acl_by_remote_user = RemoteUserACL.objects.filter(
            remote_user=remote_user
        ).filter(is_active=True).filter(
            acl_action='allow'
        ).filter(
            Q(Q(limit_hours_start__lte=now.hour)&
              Q(limit_hours_end__gt=now.hour))|
            Q(limit_hours_start=-1)
        ).filter(Q(limit_days__contains=wday)|Q(limit_days=None))

        acl_by_account = acl_by_remote_user.filter(server_account=server_account)
        if acl_by_account:
            server_account.apply_acl = acl_by_account[0]
            return server_account

        acl_by_server = acl_by_remote_user.filter(server=server)
        if acl_by_server:
            server_account.apply_acl = acl_by_server[0]
            return server_account

        acl_by_server_group = acl_by_remote_user.filter(server_group=server.server_group)
        if acl_by_server_group:
            server_account.apply_acl = acl_by_server_group[0]
            return server_account

        return None
