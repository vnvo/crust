import os
from datetime import datetime
from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response

from crustsessions.models import CrustCLISession, CrustSessionEvent
from crustsessions.serializers import CrustSessionSerializer
from crustsessions.serializers import CrustSessionEventSerializer

class CrustCLISessionViewSet(viewsets.ModelViewSet):
    serializer_class = CrustSessionSerializer

    def get_queryset(self):
        filter_active = self.request.query_params.get('active', None)

        if self.request.user.is_admin:
            queryset = CrustCLISession.objects.all()
        else:
            queryset = CrustCLISession.objects.all()
        #@todo apply filter based on access (define permissions)

        if filter_active:
            queryset = queryset.exclude(status__icontains='closed')
        else:
            queryset = queryset.exclude(status__icontains='established')

        queryset = queryset.order_by('-created_at')

        return queryset

    def get_permissions(self):
        #add proper permission checkings
        return (permissions.IsAuthenticated(),)


class CrustSessionEventViewSet(viewsets.ModelViewSet):
    serializer_class = CrustSessionEventSerializer
    queryset = CrustSessionEvent.objects.select_related(
        'session'
    ).all().order_by('event_time')

    def list(self, request, crustsession_pk):
        queryset = self.queryset.filter(session__id=crustsession_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CrustSessionCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), )


class CrustKillSessionView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(), )

    def get(self, request):
        session_id = request.query_params.get('session_id', None)
        session_obj = CrustCLISession.objects.get(id=session_id)
        if session_obj:
            pid_to_kill = session_obj.pid
            os.system('sudo kill -9 %s'%pid_to_kill)
            session_obj.termination_cause = 'Kill By %s'%request.user
            session_obj.terminated_at = datetime.now()
            session_obj.status = 'Closed-Killed'
            session_obj.save()

            return Response({'killed':True}, status=status.HTTP_200_OK)
