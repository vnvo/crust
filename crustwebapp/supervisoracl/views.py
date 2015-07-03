from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response

from servers.models import ServerGroup, Server, ServerAccount
from commandgroups.models import CommandGroup
from remoteusers.models import RemoteUser
from authentication.models import Supervisor
from supervisoracl.models import SupervisorACL
from supervisoracl.serializers import SupervisorACLSerializer
from authentication.permissions import IsAdmin


class SupervisorACLViewSet(viewsets.ModelViewSet):
    queryset = SupervisorACL.objects.all()
    serializer_class = SupervisorACLSerializer

    def get_permissions(self):
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated, )
        return (permissions.IsAuthenticated(), IsAdmin())

    def create(self, request):
        data = request.data
        fkey_objects = {
            'server_group':None, 'command_group':None,
            'server':None, 'remote_user':None}

        supervisor_data = data.pop('supervisor', None)
        if supervisor_data:
            supervisor_obj = Supervisor.objects.get(id=supervisor_data['id'])


        remote_user_data = data.pop('remote_user', None)
        if remote_user_data:
            fkey_objects['remote_user'] = RemoteUser.objects.get(id=remote_user_data['id'])

        command_group_data = data.pop('command_group', None)
        if command_group_data:
            fkey_objects['command_group'] = CommandGroup.objects.get(id=command_group_data['id'])

        server_group_data = data.pop('server_group', None)
        if server_group_data:
            fkey_objects['server_group'] = ServerGroup.objects.get(id=server_group_data['id'])

        server_data = data.pop('server', None)
        if server_data:
            fkey_objects['server'] = Server.objects.get(id=server_data['id'])

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(supervisor=supervisor_obj,
                            **fkey_objects)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        supervisoracl_obj = SupervisorACL.objects.get(id=pk)
        data = request.data
        fkey_objects = {
            'server_group':None, 'command_group':None,
            'server':None, 'remote_user':None}

        supervisor_data = data.pop('supervisor', None)
        if supervisor_data:
            supervisor_obj = Supervisor.objects.get(id=supervisor_data['id'])


        remote_user_data = data.pop('remote_user', None)
        if remote_user_data:
            fkey_objects['remote_user'] = RemoteUser.objects.get(id=remote_user_data['id'])

        command_group_data = data.pop('command_group', None)
        if command_group_data:
            fkey_objects['command_group'] = CommandGroup.objects.get(id=command_group_data['id'])

        server_group_data = data.pop('server_group', None)
        if server_group_data:
            fkey_objects['server_group'] = ServerGroup.objects.get(id=server_group_data['id'])

        server_data = data.pop('server', None)
        if server_data:
            fkey_objects['server'] = Server.objects.get(id=server_data['id'])

        serializer = self.serializer_class(supervisoracl_obj, data=data)
        if serializer.is_valid():
            serializer.save(supervisor=supervisor_obj,
                            **fkey_objects)
            return Response(
                serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupervisorACLCountView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdmin())

    def get(self, request):
        remoteuser_acl_count = SupervisorACL.objects.count()
        return Response({'supervisor_acl_count':remoteuser_acl_count})
