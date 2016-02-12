from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from remote_connections.models import RemoteConnection
from remote_connections.serializers import RemoteConnectionSerializer


class RemoteConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = RemoteConnectionSerializer

    def get_queryset(self):
        active = self.request.query_params.get('active', None)
        queryset = RemoteConnection.objects.all()
        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter', 'active']:
                continue
            queryset = queryset.filter(**{key:val})

        if active:
            queryset = queryset.filter(terminated_at=None)

        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering).distinct()

        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), )
