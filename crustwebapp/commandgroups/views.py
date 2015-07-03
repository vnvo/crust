from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response

from commandgroups.models import CommandGroup, CommandPattern
from commandgroups.serializers import CommandGroupSerializer
from commandgroups.serializers import CommandPatternSerializer

from authentication.permissions import IsAdmin


class CommandGroupsViewSet(viewsets.ModelViewSet):
    #queryset = CommandGroup.objects.all()
    serializer_class = CommandGroupSerializer

    def get_queryset(self):
        queryset = CommandGroup.objects.all()
        hint = self.request.query_params.get('hint', None)
        if hint:
            queryset = queryset.filter(command_group_name__icontains=hint)

        return queryset

    def get_permissions(self):
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(), IsAdmin())


class CommandPatternsViewSet(viewsets.ModelViewSet):
    queryset = CommandPattern.objects.all()
    serializer_class = CommandPatternSerializer

    def get_permissions(self):
        # @todo: must check the requesters assign server-groups
        #if self.request.method in permissions.SAFE_METHODS:
        #    return (permissions.IsAuthenticated(), )
        return (permissions.IsAuthenticated(), IsAdmin())

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
        return (permissions.IsAuthenticated(), IsAdmin())

    def get(self, request):
        commandgroup_count = CommandGroup.objects.count()
        return Response({'commandgroup_count':commandgroup_count})

class CommandPatternsCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdmin())

    def get(self, request):
        commandpattern_count = CommandPattern.objects.count()
        return Response({'commandpattern_count':commandpattern_count})
