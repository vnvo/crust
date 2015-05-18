from rest_framework import serializers

from servers.models import ServerGroup
from servers.models import Server
from servers.models import ServerAccount

class ServerGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServerGroup
        fields = ('id', 'group_name', 'server_set')
        read_only_fields = ('id','server_set')

class ServerSerializer(serializers.ModelSerializer):
    server_group = ServerGroupSerializer(read_only=True, required=False)

    class Meta:
        model = Server
        fields = (
            'id', 'server_group', 'server_name',
            'server_ip', 'timeout', 'sshv2_port',
            'sshv2_private_key', 'telnet_port',
            'comment'
        )

        read_only_fields = ('id',)

    def create(self, validated_data):
        server = Server.objects.create(**validated_data)
        return server


    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(ServerSerializer, self).get_validation_exclusions()

        return exclusions + ['server_group']


class ServerAccountSerializer(serializers.ModelSerializer):
    server = ServerSerializer(required=True)

    class Meta:
        model = ServerAccount
        fields = (
            'id', 'server', 'username', 'password',
            'protocol', 'sshv2_private_key', 'comment'
        )

        read_only_fields = ('id',)

    def get_validation_exclusive(self, *args, **kwargs):
        exclusions = super(ServerAccountSerializer, self).get_validation_exclusions()
        return exclusions + ['server']
