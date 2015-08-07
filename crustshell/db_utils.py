"""
This module provides access to django models
"""

import os
import sys

sys.path.append(os.getcwd()+'/../crustwebapp/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "crustwebapp.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from remoteusers.models import RemoteUser
from remoteuseracl.models import RemoteUserACL
from servers.models import ServerGroup, Server, ServerAccount



def get_remote_user_by_username(username):
    user_obj = RemoteUser.objects.get(username=str(username))
    if user_obj:
        return user_obj

    return None

def get_acls_by_remote_user(user_obj):
    return RemoteUserACL.get_cooked_acls(user_obj)

def get_server_by_addr(host_addr):
    server_obj = Server.objects.find(server_ip=str(host_addr))
    return server_obj

def get_server_by_name(host_name):
    server_obj = Server.objects.filter(server_name=str(host_name))
    return server_obj
