from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from django.db.models import Q, Count
from commandgroups.models import CommandGroup, CommandPattern
from commandgroups.serializers import CommandGroupSerializer
from commandgroups.serializers import CommandPatternSerializer

from authentication.models import Supervisor
from commandgroups.permissions import IsAdminOrCGOwner, IsAdminOrCommandPatternOwner

class CommandGroupsViewSet(viewsets.ModelViewSet):
    #queryset = CommandGroup.objects.all()
    serializer_class = CommandGroupSerializer

    def get_queryset(self):
        queryset = CommandGroup.objects.annotate(
            pattern_count=Count('commandpattern')
        )

        if self.request.user.is_admin:
            queryset = queryset.all()
        else:
            queryset = queryset.filter(
                supervisor=self.request.user
            )

        hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if hint:
            queryset = queryset.filter(command_group_name__icontains=hint)
        if search_filter:
            queryset = queryset.filter(
                Q(command_group_name__icontains=search_filter)|
                Q(supervisor__username__icontains=search_filter)|
                Q(comment__icontains=search_filter)
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter']:
                continue
            print key, val
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-id')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrCGOwner())

    def create(self, request):
        data = request.data
        if request.user.is_admin and data.has_key('supervisor'):
            supervisor = Supervisor.objects.get(id=int(data['supervisor']['id']))
        else:
            supervisor = request.user

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(supervisor=supervisor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        cg_obj = CommandGroup.objects.get(id=pk)
        data = request.data
        if request.user.is_admin and data.has_key('supervisor'):
            supervisor = Supervisor.objects.get(id=int(data['supervisor']['id']))
        else:
            supervisor = self.request.user

        serializer = self.serializer_class(cg_obj, data=data)
        if serializer.is_valid():
            serializer.save(supervisor=supervisor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommandPatternsViewSet(viewsets.ModelViewSet):
    queryset = CommandPattern.objects.all()
    serializer_class = CommandPatternSerializer

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrCommandPatternOwner())

    def create(self, request):
        data = request.data
        command_group = data.pop('command_group')
        command_group_obj = CommandGroup.objects.get(id=command_group['id'])
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(command_group=command_group_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        command_pattern_obj = CommandPattern.objects.get(id=pk)
        data = request.data
        command_group = data.pop('command_group')
        command_group_obj = CommandGroup.objects.get(id=command_group['id'])
        serializer = self.serializer_class(command_pattern_obj, data=data)
        if serializer.is_valid():
            serializer.save(command_group=command_group_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommandGroupsCountView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrCGOwner())

    def get(self, request):
        commandgroup_count = CommandGroup.objects.count()
        return Response({'commandgroup_count':commandgroup_count})

class CommandPatternsCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdminOrCommandPatternOwner())

    def get(self, request):
        commandpattern_count = CommandPattern.objects.count()
        return Response({'commandpattern_count':commandpattern_count})
