from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers
from authentication.models import Supervisor

class SupervisorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    last_login = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = Supervisor
        fields = ('id', 'username', 'email', 'created_at', 'updated_at',
                  'first_name', 'last_name', 'password', 'is_admin',
                  'is_active', 'last_login', 'confirm_password')

        read_only_fields = ('created_at', 'updated_at', 'id')

        def create(self, validated_data):
            return Supervisor.objects.create(**validated_data)

        def update(self, instance, validated_data):
            instance.email = validated_data.get('email', instance.email)

            instance.save()

            password = validated_data.get('password', None)
            confirm_password = validated_data.get('confirm_password', None)

            if password and confirm_password and password == confirm_password:
                instance.set_password(password)
                instance.save()

            update_session_auth_hash(self.context.get('request'), instance)

            return instance
