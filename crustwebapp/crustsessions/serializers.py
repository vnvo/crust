from rest_framework import serializers
from crustsessions.models import CrustCLISession, CrustSessionEvent
from servers.serializers import ServerAccountSerializer
from servers.serializers import ServerSerializer
from remoteusers.serializers import RemoteUserSerializer

class CrustSessionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    terminated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = CrustCLISession
        fields = ('id', 'created_at', 'remoteuser', 'server',
                  'serveraccount', 'status', 'terminated_at',
                  'termination_cause', 'session_id', 'client_ip')

        read_only_fields = fields


class CrustSessionEventSerializer(serializers.ModelSerializer):
    session_seq_id = serializers.IntegerField(
        source='session.id', read_only=True, required=False)
    session_id = serializers.CharField(
        source='session.session_id', read_only=True, required=False
    )

    class Meta:
        model = CrustSessionEvent
        fields = ('id', 'session_seq_id', 'session_id', 'event_time', 'content')
        read_only_fields = fields
