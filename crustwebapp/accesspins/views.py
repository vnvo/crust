from uuid import uuid4
from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from django.db.models import Q
from remoteusers.models import RemoteUser
from servers.models import Server, ServerAccount
from accesspins.models import AccessPin
from accesspins.serializers import AccessPinSerializer
from accesspins.permissions import IsAdminOrPINOwner

class AccessPinViewSet(viewsets.ModelViewSet):
    serializer_class = AccessPinSerializer

    def get_queryset(self):
        if self.request.user.is_admin:
            queryset = AccessPin.objects.all()
        else:
            queryset = AccessPin.objects.filter(supervisor=self.request.user)

        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrPINOwner())

    def create(self, request):
        data = request.data
        remote_user_data = data.pop('remote_user')
        remote_user = RemoteUser.objects.get(id=remote_user_data['id'])
        server_data = data.pop('server')
        server = Server.objects.get(id=server_data['id'])
        server_account_data = data.pop('server_account')
        server_account = ServerAccount.objects.get(id=server_account_data['id'])

        pin = str(uuid4().int)[8:18]
        data['pin'] = pin

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(
                supervisor=request.user, remote_user=remote_user,
                server=server, server_account=server_account)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        pin_obj = AccessPin.objects.get(id=pk)
        data = request.data
        remote_user_data = data.pop('remote_user')
        remote_user = RemoteUser.objects.get(id=remote_user_data['id'])
        server_data = data.pop('server')
        server = Server.objects.get(id=server_data['id'])
        server_account_data = data.pop('server_account')
        server_account = ServerAccount.objects.get(id=server_account_data['id'])

        serializer = self.serializer_class(pin_obj, data=data)
        if serializer.is_valid():
            serializer.save(
                supervisor=request.user, remote_user=remote_user,
                server=server, server_account=server_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
