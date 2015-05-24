from rest_framework import serializers

from remoteusers.models import RemoteUser

class RemoteUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = RemoteUser
        fields = ('id', 'username', 'is_locked', 'email',
                  'cell_phone', 'password', 'confirm_password',
                  'sshv2_public_key', 'comment')

        read_only_fields = ('id',)
