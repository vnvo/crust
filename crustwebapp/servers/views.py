from rest_framework import permissions, viewsets
from rest_framework.response import Response

from servers.models import ServerGroup
from servers.serializers import ServerGroupSerializer

from authentication.permissions import IsAdmin

class ServerGroupsViewSet(viewsets.ModelViewSet):
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    #permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(), IsAdmin())
