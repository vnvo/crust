from django.contrib import admin
from remote_connections.models import RemoteConnection, BanIP

admin.site.register(RemoteConnection)
admin.site.register(BanIP)
