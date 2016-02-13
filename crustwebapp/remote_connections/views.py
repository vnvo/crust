from django.db.models import Count
from datetime import timedelta, datetime
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


class RemoteConnectionsFailPerUser(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(), )
    def get(self, request):
        now = datetime.now()
        past24 = now - timedelta(seconds=72*3600)
        qs = RemoteConnection.objects.filter(
            created_at__gte=past24
        ).filter(
            successful=False
        ).values_list('username','fail_reason', 'state', 'source_ip').annotate(
            total=Count('fail_reason')
        ).order_by('-total')
        result = [
            {'username':item[0], 'fail_reason':item[1],
             'state':item[2], 'source_ip':item[3], 'total':item[4]}
            for item in qs
        ]
        return Response({'users_fail_counts':result})

class RemoteConnectionsFailCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    def get(self, request):
        now = datetime.now()
        past24 = now - timedelta(seconds=24*3600)
        qs = RemoteConnection.objects.filter(
            created_at__gte=past24
        ).filter(
            successful=False
        ).values('fail_reason').annotate(
            total=Count('fail_reason')
        ).order_by('-total')
        result = [[item['fail_reason'], item['total']] for item in qs]

        return Response({'fail_counts':result})
