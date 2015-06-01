from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from authentication.permissions import IsAdmin

from remoteusers.models import RemoteUser
from remoteusers.serializers  import RemoteUserSerializer


class RemoteUsersViewSet(viewsets.ModelViewSet):
    #queryset = RemoteUser.objects.all()
    serializer_class = RemoteUserSerializer

    def get_queryset(self):
        queryset = RemoteUser.objects.all()
        hint = self.request.query_params.get('hint', None)
        if hint:
            queryset = queryset.filter(username__icontains=hint)

        return queryset

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(), IsAdmin())

class RemoteUsersCountView(views.APIView):
    def get(self, request):
        remoteuser_count = RemoteUser.objects.count()
        return Response({'remoteuser_count': remoteuser_count})
