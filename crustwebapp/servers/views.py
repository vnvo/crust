from rest_framework import permissions, viewsets
from rest_framework import views, status, generics
from rest_framework.response import Response

from servers.models import ServerGroup, Server, ServerAccount
from servers.serializers import ServerGroupSerializer, ServerSerializer
from servers.serializers import ServerAccountSerializer

from authentication.permissions import IsAdmin


################# ServerGroups
class ServerGroupsViewSet(viewsets.ModelViewSet):
    #queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    #permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        queryset = ServerGroup.objects.all()
        hint = self.request.query_params.get('hint', None)
        if hint:
            queryset = queryset.filter(group_name__icontains=hint)

        return queryset

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(), IsAdmin())

class ServerGroupsCountView(views.APIView):
    def get(self, request):
        servergroup_count = ServerGroup.objects.count()
        return Response({'servergroup_count':servergroup_count})


################# Servers
class ServersViewSet(viewsets.ModelViewSet):
    #queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get_queryset(self):
        queryset = Server.objects.all()
        hint = self.request.query_params.get('hint', None)
        if hint:
            queryset = queryset.filter(server_name__icontains=hint)

        return queryset

    def get_permission(self):
        # @todo: must check the requesters assign server-groups
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated, )
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
    def get(self, request):
        servers_count = Server.objects.count()
        return Response({'server_count':servers_count})


################# ServerAccount
class ServerAccountsViewSet(viewsets.ModelViewSet):
    #queryset = ServerAccount.objects.all()
    serializer_class = ServerAccountSerializer

    def get_queryset(self):
        queryset = ServerAccount.objects.all()
        hint = self.request.query_params.get('hint', None)
        if hint: #username@server_name
            hint = hint.split('@')
            if hint[0]: #username
                queryset = queryset.filter(username__icontains=hint[0])
            if len(hint)> 1 and hint[1]:
                queryset = queryset.filter(server__server_name__icontains=hint[1])

        return queryset

    def get_permission(self):
        # @todo: must check the requesters assign server-groups
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated, )
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
    def get(self, request):
        serveraccounts_count = ServerAccount.objects.count()
        return Response({'serveraccount_count':serveraccounts_count})
