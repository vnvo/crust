import os
import redis
import simplejson as json
from datetime import datetime
from rest_framework import permissions, viewsets
from rest_framework import views, status
from rest_framework.response import Response
from django.db.models import Q
from crustsessions.models import CrustCLISession, CrustSessionEvent
from crustsessions.serializers import CrustSessionSerializer
from crustsessions.serializers import CrustSessionEventSerializer

class CrustCLISessionViewSet(viewsets.ModelViewSet):
    serializer_class = CrustSessionSerializer

    def get_queryset(self):
        filter_active = self.request.query_params.get('active', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if self.request.user.is_admin:
            queryset = CrustCLISession.objects.all()
        else:
            queryset = CrustCLISession.objects.all()
        #@todo apply filter based on access (define permissions)

        if search_filter:
            queryset = queryset.filter(
                Q(remoteuser=search_filter) |
                Q(serveraccount__icontains=search_filter) |
                Q(server__icontains=search_filter) |
                Q(client_ip=search_filter)
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'search_filter', 'active']:
                continue

            queryset = queryset.filter(**{key:val})

        if filter_active:
            queryset = queryset.exclude(status__icontains='closed')
        else:
            queryset = queryset.exclude(status__icontains='established')

        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering).distinct()

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
        session_obj = CrustCLISession.objects.get(id=crustsession_pk)
        print session_obj
        print request.query_params
        queryset = self.queryset.filter(session__id=crustsession_pk)
        if request.query_params.has_key('last_event_id'):
            last_id = int(request.query_params.get('last_event_id'))
            print last_id
            queryset = queryset.filter(id__gt=last_id)
        if request.query_params.has_key('seek_end'):
            queryset = queryset.latest('id')

        serializer = self.serializer_class(queryset, many=True)
        terminated_at = None
        if session_obj.terminated_at:
            terminated_at = session_obj.terminated_at.strftime('%Y-%m-%d %H:%M:%S')

        return Response(
            {'events':serializer.data, 'status':session_obj.status,
             'session_created_at':session_obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
             'session_terminated_at':terminated_at
            }
        )


class CrustActiveSessionCountView(views.APIView):

    def get_permissions(self):
        return (permissions.IsAuthenticated(), )

    def get(self, request):
        queryset = CrustCLISession.objects.exclude(status__icontains='closed')
        return Response(
            {'active_count':queryset.count()},
            status=status.HTTP_200_OK
        )

class CrustKillSessionView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(), )

    def get(self, request):
        session_id = request.query_params.get('session_id', None)
        session_obj = CrustCLISession.objects.get(id=session_id)
        if session_obj:
            pid_to_kill = session_obj.pid
            #os.system('sudo kill -9 %s'%pid_to_kill)
            redis_conn = redis.Redis()
            redis_conn.publish(str(pid_to_kill), 'KILL:%s'%request.user.username)
            session_obj.termination_cause = 'Kill By %s'%request.user
            session_obj.terminated_at = datetime.now()
            session_obj.status = 'CLOSED-KILLED'
            session_obj.save()

            return Response({'killed':True}, status=status.HTTP_200_OK)

class CrustSessionSendMsgView(views.APIView):
    def get_permissions(self):
        return (permissions.IsAuthenticated(), )

    def get(self, request):
        session_id = request.query_params.get('session_id', None)
        message = request.query_params.get('message','')
        if '\n' in message:
            message = message.replace('\n', '\r\n')
        session_obj = CrustCLISession.objects.get(id=session_id)
        if session_obj:
            msg_info = {
                'sender':request.user.username,
                'message': message
            }
            redis_conn = redis.Redis()
            redis_conn.publish(
                str(session_obj.pid),
                'MSG:%s'%json.dumps(msg_info))

            return Response({'sent':True}, status=status.HTTP_200_OK)
