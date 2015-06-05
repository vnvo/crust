from rest_framework import serializers
from servers.serializers import ServerGroupSerializer, ServerSerializer
from servers.serializers import ServerAccountSerializer
from remoteusers.serializers import RemoteUserSerializer
from remoteuseracl.models import RemoteUserACL
from commandgroups.serializers import CommandGroupSerializer

class RemoteUserACLSerializer(serializers.ModelSerializer):
    server_group = ServerGroupSerializer(required=False, read_only=True)
    server = ServerSerializer(required=False, read_only=True)
    server_account = ServerAccountSerializer(required=False, read_only=True)
    command_group = CommandGroupSerializer(required=False, read_only=True)
    remote_user = RemoteUserSerializer(read_only=True, required=False)

    class Meta:
        model = RemoteUserACL
        fields = ('id', 'remote_user', 'server_account', 'server',
                  'server_group', 'command_group', 'acl_action', 'is_active')

        read_only_fields = ('id', 'remote_user', 'server',
                            'server_account', 'server_group'
                            'command_group')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(RemoteUserACLSerializer, self).get_validation_exclusions()
        return exclusions + ['server_group', 'remote_user', 'server',
                             'server_account', 'command_group']

    def create(self, validated_data):
        remoteuser_acl = RemoteUserACL.objects.create(**validated_data)
        return remoteuser_acl
