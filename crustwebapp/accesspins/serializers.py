from rest_framework import serializers
from accesspins.models import AccessPin

class AccessPinSerializer(serializers.ModelSerializer):
    supervisor_id = serializers.IntegerField(
        source='supervisor.id', read_only=True, required=False)
    supervisor_name = serializers.CharField(
        source='supervisor.username', read_only=True, required=False)
    remote_user_id = serializers.IntegerField(
        source='remote_user.id', read_only=True, required=False)
    remote_user_username = serializers.CharField(
        source='remote_user.username', read_only=True, required=False)
    server_id = serializers.IntegerField(
        source='server.id', read_only=True, required=False)
    server_name = serializers.CharField(
        source='server.server_name', read_only=True, required=False)
    server_account_id = serializers.IntegerField(
        source='server_account.id', read_only=True, required=False)
    server_account_username = serializers.CharField(
        source='server_account.username', read_only=True, required=False)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    first_used_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    exp_on_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)


    class Meta:
        model = AccessPin
        fields = ('id', 'supervisor_id', 'supervisor_name',
                  'remote_user_id', 'remote_user_username', 'server_id',
                  'server_name', 'server_account_id', 'server_account_username',
                  'pin', 'created_at', 'first_used_at', 'validation_mode',
                  'exp_after_creation', 'exp_after_creation_formatted',
                  'exp_after_first_login', 'exp_after_first_login_formatted',
                  'exp_on_date')
        read_on_fields = ('id', 'supervisor_id', 'supervisor_name',
                  'remote_user_id', 'remote_user_username', 'server_id',
                  'server_name', 'server_account_id', 'server_account_username',
                  'created_at', 'first_used_at', 'exp_after_creation_formatted',
                  'exp_after_first_login_formatted', 'exp_on_date')

    def create(self, validated_data):
        apin = AccessPin.objects.create(**validated_data)
        return apin
