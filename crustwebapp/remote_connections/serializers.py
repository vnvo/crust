from rest_framework import serializers
from remote_connections.models import RemoteConnection

class RemoteConnectionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    terminated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = RemoteConnection
        fields = ('id', 'created_at', 'terminated_at', 'username',
                  'termination_cause', 'pid', 'source_ip', 'successful',
                  'fail_reason', 'state')

        read_only_fields = fields
