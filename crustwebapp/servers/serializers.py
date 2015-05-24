from rest_framework import serializers

from servers.models import ServerGroup
from servers.models import Server
from servers.models import ServerAccount

class ServerGroupSerializer(serializers.ModelSerializer):
    server_count = serializers.IntegerField(
        source='get_server_count',
        required=False, read_only=True)

    class Meta:
        model = ServerGroup
        fields = ('id', 'group_name', 'server_set', 'server_count')
        read_only_fields = ('id','server_set', 'server_count')

class ServerSerializer(serializers.ModelSerializer):
    server_group = ServerGroupSerializer(read_only=True, required=False)
    serveraccount_count = serializers.IntegerField(
        source='get_serveraccount_count',
        required=False, read_only=True)

    class Meta:
        model = Server
        fields = (
            'id', 'server_group', 'server_name',
            'server_ip', 'timeout', 'sshv2_port',
            'sshv2_private_key', 'telnet_port',
            'comment', 'serveraccount_set',
            'serveraccount_count'
        )

        read_only_fields = ('id', 'serveraccount_set', 'serveraccount_count')

    def create(self, validated_data):
        server = Server.objects.create(**validated_data)
        return server

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(ServerSerializer, self).get_validation_exclusions()
        print "server validation exclu ... "
        return exclusions + ['server_group']


class ServerAccountSerializer(serializers.ModelSerializer):
    """
    @todo: fix the default value to something meaningfull and reliable
    """
    server = ServerSerializer(read_only=True, default=Server.objects.get(id=1))

    class Meta:
        model = ServerAccount
        fields = (
            'id', 'server', 'username', 'password',
            'protocol', 'sshv2_private_key', 'comment',
            'is_locked'
        )

        read_only_fields = ('id',)

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(ServerAccountSerializer, self).get_validation_exclusions()
        print "checking exclusions ..."
        return exclusions + ['server']

    def create(self, validated_data):
        serveraccount = ServerAccount.objects.create(**validated_data)
        return serveraccount
