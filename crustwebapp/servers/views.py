import operator
from rest_framework import permissions, viewsets
from rest_framework import views, status, generics
from rest_framework.response import Response
from django.db.models import Q, Count
from servers.models import ServerGroup, Server, ServerAccount
from servers.models import ServerGroupAccount, ServerAccountMap
from servers.serializers import ServerGroupSerializer, ServerSerializer
from servers.serializers import ServerAccountSerializer
from servers.serializers import ServerGroupAccountSerializer
from servers.serializers import ServerAccountMapSerializer

from servers.permissions import IsAdminOrGroupOwner
from servers.permissions import IsAdminOrServerOwner
from servers.permissions import IsAdminOrServerAccountOwner
from authentication.models import Supervisor

################# ServerGroups
class ServerGroupsViewSet(viewsets.ModelViewSet):
    #queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    #permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        queryset = ServerGroup.objects.annotate(server_count=Count('server'))
        queryset = queryset.annotate(
            serveraccount_count=Count('server__serveraccountmap')
        )

        if self.request.user.is_admin:
            queryset = queryset.all().order_by('group_name')
        else:
            queryset = ServerGroup.objects.filter(
                supervisor=self.request.user
            ).order_by('group_name')

        hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if hint:
            queryset = queryset.filter(group_name__icontains=hint)
        if search_filter:
            queryset = queryset.filter(
                Q(group_name__icontains=search_filter)|
                Q(supervisor__username__icontains=search_filter)
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter', 'hint']:
                continue

            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated())
        return (permissions.IsAuthenticated(), IsAdminOrGroupOwner())

    def create(self, request):
        data = request.data
        if request.user.is_admin and data.has_key('supervisor'):
            supervisor = Supervisor.objects.get(id=int(data['supervisor']['id']))
        else:
            supervisor = self.request.user

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(supervisor=supervisor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        servergroup_obj = ServerGroup.objects.get(id=pk)
        data = request.data
        if request.user.is_admin and data.has_key('supervisor'):
            supervisor = Supervisor.objects.get(id=int(data['supervisor']['id']))
        else:
            supervisor = self.request.user

        serializer = self.serializer_class(servergroup_obj, data=data)
        if serializer.is_valid():
            serializer.save(supervisor=supervisor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerGroupsCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrGroupOwner())

    def get(self, request):
        if request.user.is_admin:
            servergroup_count = ServerGroup.objects.count()
        else:
            servergroup_count = ServerGroup.objects.filter(supervisor=request.user).count()

        return Response({'servergroup_count':servergroup_count})


class ServerGroupsServerCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrGroupOwner())

    def get(self, request):
        if request.user.is_admin:
            qs = ServerGroup.objects.all()
        else:
            qs = ServerGroup.objects.filter(supervisor=request.user)

        sg_server_count = []
        for item in qs:
            sg_server_count.append( [item.group_name, item.get_server_count] )

        return Response({'server_counts':sg_server_count})


################# Servers
class ServersViewSet(viewsets.ModelViewSet):
    #queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get_queryset(self):
        queryset = Server.objects.annotate(serveraccount_count=Count('serveraccountmap'))

        if self.request.user.is_admin:
            queryset = queryset.all().order_by('server_name')
        else:
            queryset = ServerGroup.objects.filter(
                server_group__supervisor=self.request.user
            ).order_by('server_name')

        hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if hint:
            queryset = queryset.filter(
                Q(server_name__icontains=hint)|
                Q(server_ip__icontains=hint)
            )
        if search_filter:
            queryset = queryset.filter(
                Q(server_group__group_name__icontains=search_filter)|
                Q(server_name__icontains=search_filter)|
                Q(server_ip__icontains=search_filter)|
                Q(comment__icontains=search_filter)
            )

        ############## Filter By Specific Conditions ##############
        qp = self.request.query_params
        if qp.has_key('ip'): # we want to handle ip condition separatly
            ip_list = qp.get('ip').split(',')
            queryset = queryset.filter(
                reduce(operator.or_,
                       (Q(server_ip__startswith=item) for item in ip_list))
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter',
                       'hint', 'ip']:
                continue
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        # @todo: must check the requesters assign server-groups
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated(), IsAdmin() )
        return (permissions.IsAuthenticated(), IsAdminOrServerOwner())

    def create(self, request):
        data = request.data
        print data
        server_group = data.pop('server_group')
        print type(server_group)
        if isinstance(server_group, str) or isinstance(server_group, unicode):
            server_group_obj = ServerGroup.objects.filter(group_name=server_group)
            if server_group_obj:
                server_group_obj = server_group_obj[0]
            else:# create the group
                server_group_obj = ServerGroup(group_name=server_group, supervisor=request.user)
                server_group_obj.save()
                print 'server group created ', server_group_obj
        else:
            server_group_obj = ServerGroup.objects.get(id=server_group['id'])

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(server_group=server_group_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        server_obj = Server.objects.get(id=pk)
        data = request.data
        server_group = data.pop('server_group')
        server_group_obj = ServerGroup.objects.get(id=server_group['id'])
        serializer = self.serializer_class(server_obj, data=data)
        if serializer.is_valid():
            serializer.save(server_group=server_group_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServersCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrServerOwner())

    def get(self, request):
        if request.user.is_admin:
            servers_count = Server.objects.count()
        else:
            servers_count = Server.objects.filter(
                servergroup__supervisor=request.user).count()

        return Response({'server_count':servers_count})


################# ServerAccount
class ServerAccountsViewSet(viewsets.ModelViewSet):
    #queryset = ServerAccount.objects.all()
    serializer_class = ServerAccountSerializer

    def get_queryset(self):
        queryset = ServerAccount.objects

        if self.request.user.is_admin:
            queryset = queryset.all().order_by('username')
        else:
            queryset = queryset.filter(
                server__server_group__supervisor=self.request.user
            ).order_by('username')

        hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if hint:
            hint = hint.split('@')
            if hint[0]:
                queryset = queryset.filter(username__icontains=hint[0])
            if len(hint)>1 and hint[1]:
                queryset = queryset.filter(server__server_name__icontains=hint[1])

        if search_filter:
            queryset = queryset.filter(
                Q(server__server_name__icontains=search_filter)|
                Q(username__icontains=search_filter)|
                Q(comment__icontains=search_filter)|
                Q(protocol__icontains=search_filter)
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter', 'hint']:
                continue
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrServerAccountOwner())

    def create(self, request):
        data = request.data
        servers = []
        server_groups = []
        if data.has_key('servers'):
            servers_data = data.pop('servers')
            servers = [
                Server.objects.get(id=item['id'])
                for item in servers_data
            ]

        if data.has_key('server_groups'):# add server groups
            server_groups = data.pop('server_groups')
            server_groups = [
                ServerGroup.objects.get(id=item['id'])
                for item in server_groups
            ]

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            account_id = serializer.data['id']
            sa = ServerAccount.objects.get(id=account_id)
            # add servers
            for s in servers:
                ServerAccountMap(server_account=sa, server=s).save()
            # add server groups
            for sg in server_groups:
                sga = ServerGroupAccount(server_account=sa, server_group=sg).save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk):
        serveraccount_obj = ServerAccount.objects.get(id=pk)
        data = request.data
        servers = []
        server_groups = []

        if data.has_key('servers'):
            servers_data = data.pop('servers')
            servers = [
                Server.objects.get(id=item['id'])
                for item in servers_data]
        if data.has_key('server_groups'):
            server_groups = data.pop('server_groups')
            server_groups = [
                ServerGroup.objects.get(id=item['id'])
                for item in server_groups]

        serializer = self.serializer_class(serveraccount_obj, data=data)

        if serializer.is_valid():
            serializer.save()
            ServerAccountMap.objects.filter(
                server_account=serveraccount_obj).delete()
            for s in servers:
                ServerAccountMap(
                    server_account = serveraccount_obj,
                    server = s
                ).save()

            ServerGroupAccount.objects.filter(
                server_account=serveraccount_obj).delete()
            for sg in server_groups:
                sga = ServerGroupAccount(
                    server_account=serveraccount_obj,
                    server_group=sg
                ).save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServerAccountsCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrServerAccountOwner())

    def get(self, request):
        serveraccounts_count = ServerAccount.objects.count()
        return Response({'serveraccount_count':serveraccounts_count})

#############################
class ServerGroupAccountsViewSet(viewsets.ModelViewSet):
    serializer_class = ServerGroupAccountSerializer

    def get_queryset(self):
        queryset = ServerGroupAccount.objects
        if self.request.query_params.has_key('server_group_id'):
            sg = ServerGroup.objects.get(
                id=int(self.request.query_params.get('server_group_id'))
            )
            queryset = queryset.filter(server_group=sg)
        elif self.request.query_params.has_key('server_account_id'):
            sa = ServerAccount.objects.get(
                id=int(self.request.query_params.get('server_account_id')))
            queryset = queryset.filter(server_account=sa)

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter', 'hint']:
                continue
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), ) #fix, check access to sg or sa?

    def create(self, request):
        data = request.data
        server_account_data = data.pop('server_account')
        server_account_obj = ServerAccount.objects.get(id=server_account_data['id'])
        server_group_data = data.pop('server_group')
        server_group_obj = ServerGroup.objects.get(id=server_group_data['id'])

        print data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(
                server_account=server_account_obj,
                server_group=server_group_obj
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        sgaccount_obj = ServerGroupAccount.objects.get(id=pk)
        data = request.data

        server_account_data = data.pop('server_account')
        server_account_obj = ServerAccount.objects.get(id=server_account_data['id'])
        server_group_data = data.pop('server_group')
        server_group_obj = ServerGroup.objects.get(id=server_group_data['id'])

        serializer = self.serializer_class(sgaccount_obj, data=data)
        if serializer.is_valid():
            serializer.save(
                server_account=server_account_obj,
                server_group_obj=server_group_obj
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerAccountMapsViewSet(viewsets.ModelViewSet):
    serializer_class = ServerAccountMapSerializer

    def get_queryset(self):
        queryset = ServerAccountMap.objects
        if self.request.query_params.has_key('server_id'):
            server_obj = Server.objects.get(
                id=int(self.request.query_params.get('server_id'))
            )
            queryset = queryset.filter(server=server_obj)

        elif self.request.query_params.has_key('server_account_id'):
            sa = ServerAccount.objects.get(
                id=int(self.request.query_params.get('server_account_id')))
            queryset = queryset.filter(server_account=sa)

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter', 'hint']:
                continue
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), ) #fix, check access to sg or sa?

    def create(self, request):
        data = request.data
        server_account_data = data.pop('server_account')
        server_account_obj = ServerAccount.objects.get(id=server_account_data['id'])
        server_data = data.pop('server')
        server_obj = Server.objects.get(id=server_data['id'])

        print data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(
                server_account=server_account_obj,
                server=server_obj
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        sgaccount_obj = ServerAccountMap.objects.get(id=pk)
        data = request.data

        server_account_data = data.pop('server_account')
        server_account_obj = ServerAccount.objects.get(id=server_account_data['id'])
        server_data = data.pop('server')
        server_obj = Server.objects.get(id=server_data['id'])

        serializer = self.serializer_class(sgaccount_obj, data=data)
        if serializer.is_valid():
            serializer.save(
                server_account=server_account_obj,
                server_obj=server_obj
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

############## All Server Account For a server
class AllServerAccountsViewSet(viewsets.ModelViewSet):
    serializer_class = ServerAccountSerializer
    queryset = ServerAccount.objects

    def list(self, request):
        """
        Return All available Server Accounts for the given server_id either
        by direct mapping (ServerAccountMap) or by ServerGroupAccount
        """
        server = Server.objects.get(id=int(request.query_params.get('server_id')))
        sa_by_server = ServerAccount.serveraccountmap_set.filter(server=server)
        print sa_by_server
        sa_by_servergroup = ServerAccount.servergroupaccount_set.filter(
            server_group=server.server_group)
        print sa_by_servergroup

        serializer = self.serializer_class(queryset, many=True)
        return Response({'events':serializer.data, 'status':session_obj.status})
