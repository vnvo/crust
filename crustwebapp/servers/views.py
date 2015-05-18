from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response

from servers.models import ServerGroup, Server
from servers.serializers import ServerGroupSerializer, ServerSerializer

from authentication.permissions import IsAdmin

class ServerGroupsViewSet(viewsets.ModelViewSet):
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    #permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(), IsAdmin())

class ServerGroupsCountView(views.APIView):
    def get(self, request):
        servergroup_count = ServerGroup.objects.count()
        return Response({'servergroup_count':servergroup_count})



class ServersViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServersCountView(views.APIView):
    def get(self, request):
        servers_count = Server.objects.count()
        return Response({'server_count':servers_count})
