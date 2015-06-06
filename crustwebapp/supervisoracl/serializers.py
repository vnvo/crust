from rest_framework import serializers
from servers.serializers import ServerGroupSerializer, ServerSerializer
from remoteusers.serializers import RemoteUserSerializer
from supervisoracl.models import SupervisorACL
from authentication.serializers import SupervisorSerializer
from commandgroups.serializers import CommandGroupSerializer

class SupervisorACLSerializer(serializers.ModelSerializer):
    server_group = ServerGroupSerializer(required=False, read_only=True)
    server = ServerSerializer(required=False, read_only=True)
    command_group = CommandGroupSerializer(required=False, read_only=True)
    remote_user = RemoteUserSerializer(read_only=True, required=False)
    supervisor = SupervisorSerializer(read_only=True, required=False)

    class Meta:
        model = SupervisorACL
        fields = ('id', 'supervisor', 'remote_user', 'server',
                  'server_group', 'command_group', 'acl_action',
                  'is_active')

        read_only_fields = ('id', 'supervisor', 'remote_user', 'server',
                            'server_group', 'command_group')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(SupervisorACLSerializer, self).get_validation_exclusions()
        return exclusions + ['server_group', 'remote_user',
                             'supervisor','server', 'command_group']

    def create(self, validated_data):
        supervisor_acl = SupervisorACL.objects.create(**validated_data)
        return supervisor_acl
