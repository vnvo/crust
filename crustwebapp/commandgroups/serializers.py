from rest_framework import serializers
from commandgroups.models import CommandGroup, CommandPattern
from authentication.serializers import SupervisorSerializer

class CommandGroupSerializer(serializers.ModelSerializer):
    pattern_count = serializers.IntegerField(
        source='get_pattern_count', required=False, read_only=True)
    supervisor = SupervisorSerializer(required=False, read_only=True)

    class Meta:
        model = CommandGroup
        fields = ('id', 'command_group_name','supervisor',
                  'default_action', 'comment', 'pattern_count')
        read_only_fields = ('id', 'pattern_count')


class CommandPatternSerializer(serializers.ModelSerializer):
    command_group = CommandGroupSerializer(required=False, read_only=True)

    class Meta:
        model = CommandPattern
        fields = ('id', 'command_group', 'pattern', 'action')
        read_only_fields = ('id', 'command_group')
