from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from servers.models import ServerGroup, Server, ServerAccount
from commandgroups.models import CommandGroup
from remoteusers.models import RemoteUser
from remoteuseracl.models import RemoteUserACL
from remoteuseracl.serializers import RemoteUserACLSerializer
from django.db.models import Q, Count
from remoteuseracl.permissions import IsAdminOrRuleOwner
from authentication.permissions import IsAdmin


class RemoteUserACLViewSet(viewsets.ModelViewSet):
    queryset = RemoteUserACL.objects.all()
    serializer_class = RemoteUserACLSerializer

    def get_queryset(self):
        queryset = RemoteUserACL.objects

        if self.request.user.is_admin:
            queryset = queryset.all()
        else:
            queryset = queryset.filter(
                Q(server_group__supervisor=self.request.user)|
                Q(server__server_group__supervisor=self.request.user)|
                Q(server_account__server__server_group__supervisor=self.request.user)
            )

        #hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)

        if search_filter:
            queryset = queryset.filter(
                Q(remote_user__username__icontains=search_filter)|
                Q(server_account__username__icontains=search_filter)|
                Q(server_account__server__server_name__icontains=search_filter)|
                Q(server__server_name__icontains=search_filter)|
                Q(server_group__group_name__icontains=search_filter)|
                Q(command_group__command_group_name__icontains=search_filter)
            )

        for key, val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter']:
                continue
            print key, val
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset


    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrRuleOwner())

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
            fkey_objects['command_group'] = CommandGroup.objects.get(
                id=command_group_data['id'])

        server_group_data = data.pop('server_group', None)
        if server_group_data:
            fkey_objects['server_group'] = ServerGroup.objects.get(
                id=server_group_data['id'])

        server_data = data.pop('server', None)
        if server_data:
            fkey_objects['server'] = Server.objects.get(id=server_data['id'])

        server_account_data = data.pop('server_account', None)
        if server_account_data:
            fkey_objects['server_account'] = ServerAccount.objects.get(
                id=server_account_data['id'])

        #@todo check limit days and hours
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
    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdmin())

    def get(self, request):
        remoteuser_acl_count = RemoteUserACL.objects.count()
        return Response({'remoteuser_acl_count':remoteuser_acl_count})
