from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response

from servers.models import ServerGroup, Server, ServerAccount
from commandgroups.models import CommandGroup
from remoteusers.models import RemoteUser
from remoteuseracl.models import RemoteUserACL
from remoteuseracl.serializers import RemoteUserACLSerializer

from authentication.permissions import IsAdmin


class RemoteUserACLViewSet(viewsets.ModelViewSet):
    queryset = RemoteUserACL.objects.all()
    serializer_class = RemoteUserACLSerializer

    def get_permission(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated, )
        return (permissions.IsAuthenticated(), IsAdmin())

    def create(self, request):
        data = request.data
        fkey_objects = {
            'server_group':None, 'command_group':None,
            'server':None, 'server_account':None}

        remote_user_data = data.pop('remote_user', None)
        if remote_user_data:
            remote_user_obj = RemoteUser.objects.get(id=remote_user_data['id'])


        command_group_data = data.pop('command_group', None)
        if command_group_data:
            fkey_objects['command_group'] = CommandGroup.objects.get(id=command_group_data['id'])

        server_group_data = data.pop('server_group', None)
        if server_group_data:
            fkey_objects['server_group'] = ServerGroup.objects.get(id=server_group_data['id'])

        server_data = data.pop('server', None)
        if server_data:
            fkey_objects['server'] = Server.objects.get(id=server_data['id'])

        server_account_data = data.pop('server_account', None)
        if server_account_data:
            fkey_objects['server_account'] = ServerAccount.objects.get(id=server_account_data['id'])

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(remote_user=remote_user_obj,
                            **fkey_objects)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        remoteuseracl_obj = RemoteUserACL.objects.get(id=pk)
        data = request.data
        fkey_objects = {
            'server_group':None, 'command_group':None,
            'server':None, 'server_account':None}

        remote_user_data = data.pop('remote_user', None)
        if remote_user_data:
            remote_user_obj = RemoteUser.objects.get(id=remote_user_data['id'])


        command_group_data = data.pop('command_group', None)
        if command_group_data:
            fkey_objects['command_group'] = CommandGroup.objects.get(id=command_group_data['id'])

        server_group_data = data.pop('server_group', None)
        if server_group_data:
            fkey_objects['server_group'] = ServerGroup.objects.get(id=server_group_data['id'])

        server_data = data.pop('server', None)
        if server_data:
            fkey_objects['server'] = Server.objects.get(id=server_data['id'])

        server_account_data = data.pop('server_account', None)
        if server_account_data:
            fkey_objects['server_account'] = ServerAccount.objects.get(id=server_account_data['id'])

        serializer = self.serializer_class(remoteuseracl_obj, data=data)
        if serializer.is_valid():
            serializer.save(remote_user=remote_user_obj,
                            **fkey_objects)
            return Response(
                serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoteUserACLCountView(views.APIView):
    def get(self, request):
        remoteuser_acl_count = RemoteUserACL.objects.count()
        return Response({'remoteuser_acl_count':remoteuser_acl_count})
