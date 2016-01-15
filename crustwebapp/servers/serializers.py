from rest_framework import serializers
from authentication.serializers import SupervisorSerializer
from servers.models import ServerGroup
from servers.models import Server
from servers.models import ServerAccount
from servers.models import ServerGroupAccount


class ServerGroupSerializer(serializers.ModelSerializer):
    server_count = serializers.IntegerField(
        source='get_server_count',
        required=False, read_only=True)

    serveraccount_count = serializers.IntegerField(
        source='serveraccounts_count',
        required=False, read_only=True)

    supervisor = SupervisorSerializer(read_only=True, required=False)

    class Meta:
        model = ServerGroup
        fields = ('id', 'group_name', 'server_count',
                  'supervisor', 'serveraccount_count')
        read_only_fields = ('id', 'server_count', 'supervisor')

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
    assigned_server_groups = serializers.CharField(
        source='get_assigned_server_groups', read_only=True, required=False)

    server = ServerSerializer(read_only=True, required=False)
    server_account_repr = serializers.CharField(
        source='get_server_account_repr', required=False, read_only=True)

    class Meta:
        model = ServerAccount
        fields = (
            'id', 'server', 'username', 'password', 'password_mode',
            'protocol', 'sshv2_private_key', 'comment',
            'is_locked', 'server_account_repr', 'assigned_server_groups'
        )

        read_only_fields = ('id', 'server_account_repr', 'server',
                            'assigned_server_groups')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(ServerAccountSerializer, self).get_validation_exclusions()
        print "checking exclusions ..."
        return exclusions + ['server']

    def create(self, validated_data):
        serveraccount = ServerAccount.objects.create(**validated_data)
        return serveraccount

class ServerGroupAccountSerializer(serializers.ModelSerializer):
    server_account = ServerAccountSerializer(read_only=True, required=False)
    server_group = ServerGroupSerializer(read_only=True, required=False)

    class Meta:
        model = ServerGroupAccount
        fields = ('server_account', 'server_group')

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(ServerGroupAccountSerializer, self).get_validation_exclusions()
        print "checking exclusions ..."
        return exclusions + ['server_group', 'server_account']

    def create(self, validated_data):
        sgaccount = ServerGroupAccount.objects.create(**validated_data)
        return sgaccount
