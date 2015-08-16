from rest_framework import permissions, viewsets
from rest_framework import views, status, generics
from rest_framework.response import Response
from django.db.models import Q, Count
from servers.models import ServerGroup, Server, ServerAccount
from servers.serializers import ServerGroupSerializer, ServerSerializer
from servers.serializers import ServerAccountSerializer

from authentication.permissions import IsAdmin
from authentication.models import Supervisor

################# ServerGroups
class ServerGroupsViewSet(viewsets.ModelViewSet):
    #queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    #permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        queryset = ServerGroup.objects.annotate(server_count=Count('server'))
        queryset = queryset.annotate(serveraccount_count=Count('server__serveraccount'))

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
            if key in ['page', 'page_size', 'ordering', 'search_filter']:
                continue

            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated())
        return (permissions.IsAuthenticated(), IsAdmin())

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
        return (permissions.IsAuthenticated(), IsAdmin())

    def get(self, request):
        if request.user.is_admin:
            servergroup_count = ServerGroup.objects.count()
        else:
            servergroup_count = ServerGroup.objects.filter(supervisor=request.user).count()

        return Response({'servergroup_count':servergroup_count})


################# Servers
class ServersViewSet(viewsets.ModelViewSet):
    #queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get_queryset(self):
        queryset = Server.objects.annotate(serveraccount_count=Count('serveraccount'))

        if self.request.user.is_admin:
            queryset = queryset.all().order_by('server_name')
        else:
            queryset = ServerGroup.objects.filter(
                server_group__supervisor=self.request.user
            ).order_by('server_name')

        hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if hint:
            queryset = queryset.filter(server_name__icontains=hint)
        if search_filter:
            queryset = queryset.filter(
                Q(server_group__group_name__icontains=search_filter)|
                Q(server_name__icontains=search_filter)|
                Q(server_ip__icontains=search_filter)|
                Q(comment__icontains=search_filter)
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter']:
                continue
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        # @todo: must check the requesters assign server-groups
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated(), IsAdmin() )
        return (permissions.IsAuthenticated(), IsAdmin())

    def create(self, request):
        data = request.data
        server_group = data.pop('server_group')
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
        return (permissions.IsAuthenticated(), IsAdmin())

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
        if self.request.user.is_admin:
            queryset = ServerAccount.objects.all()
        else:
            queryset = ServerAccount.objects.filter(
                server__server_group__supervisor=self.request.user)

        hint = self.request.query_params.get('hint', None)
        if hint: #username@server_name
            hint = hint.split('@')
            if hint[0]: #username
                queryset = queryset.filter(username__icontains=hint[0])
            if len(hint)> 1 and hint[1]:
                queryset = queryset.filter(server__server_name__icontains=hint[1])

        return queryset

    def get_permissions(self):
        # @todo: must check the requesters assign server-groups
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated(), )
        return (permissions.IsAuthenticated(), IsAdmin())

    def create(self, request):
        data = request.data
        server_data = data.pop('server')
        server_obj = Server.objects.get(id=server_data['id'])
        #data['server'] = server_obj
        print data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(server=server_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        serveraccount_obj = ServerAccount.objects.get(id=pk)
        data = request.data
        server_data = data.pop('server')
        server_obj = Server.objects.get(id=server_data['id'])
        serializer = self.serializer_class(serveraccount_obj, data=data)
        if serializer.is_valid():
            serializer.save(server=server_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServerAccountsCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdmin())

    def get(self, request):
        serveraccounts_count = ServerAccount.objects.count()
        return Response({'serveraccount_count':serveraccounts_count})
