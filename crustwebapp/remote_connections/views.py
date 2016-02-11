from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from remote_connections.models import RemoteConnection
from remote_connections.serializers import RemoteConnectionSerializer


class RemoteConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = RemoteConnectionSerializer

    def get_queryset(self):
        queryset = RemoteConnection.objects.all()
        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), )
