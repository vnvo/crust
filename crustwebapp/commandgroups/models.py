from django.db import models

class CommandGroup(models.Model):
    command_group_name = models.CharField(max_length=256, unique=True)
    default_action = models.CharField(max_length=32)
    comment = models.TextField(blank=True, default='')

    @property
    def pattern_count(self):
        return self.commandpattern_set.count()

class CommandPattern(models.Model):
    command_group = models.ForeignKey(CommandGroup)
    pattern = models.CharField(max_length=256)
    action = models.CharField(max_length=32)
