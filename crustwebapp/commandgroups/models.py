from django.db import models
from authentication.models import Supervisor

class CommandGroup(models.Model):
    command_group_name = models.CharField(max_length=256, unique=True)
    default_action = models.CharField(max_length=32)
    comment = models.TextField(blank=True, default='')
    supervisor = models.ForeignKey(Supervisor, null=True, blank=True)

    @property
    def get_pattern_count(self):
        return self.commandpattern_set.count()

class CommandPattern(models.Model):
    command_group = models.ForeignKey(CommandGroup)
    pattern = models.CharField(max_length=256)
    action = models.CharField(max_length=32)
