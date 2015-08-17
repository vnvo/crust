from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from authentication.permissions import IsAdmin
from django.db.models import Q
from remoteusers.models import RemoteUser
from remoteusers.serializers  import RemoteUserSerializer


class RemoteUsersViewSet(viewsets.ModelViewSet):
    #queryset = RemoteUser.objects.all()
    serializer_class = RemoteUserSerializer

    def get_queryset(self):
        queryset = RemoteUser.objects.all().order_by('username')

        hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if hint:
            queryset = queryset.filter(username__icontains=hint)
        if search_filter:
            queryset = queryset.filter(
                Q(username__icontains=search_filter)|
                #Q(supervisor__username__icontains=search_filter)|
                Q(email__icontains=search_filter)|
                Q(cell_phone__icontains=search_filter)|
                Q(comment__icontains=search_filter)
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter']:
                continue

            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(), IsAdmin())

class RemoteUsersCountView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdmin())

    def get(self, request):
        remoteuser_count = RemoteUser.objects.count()
        return Response({'remoteuser_count': remoteuser_count})
