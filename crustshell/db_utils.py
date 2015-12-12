"""
This module provides access to django models
"""

import os
import sys
import uuid
import json
from datetime import datetime
sys.path.append(os.getcwd()+'/../crustwebapp/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "crustwebapp.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from remoteusers.models import RemoteUser
from remoteuseracl.models import RemoteUserACL
from servers.models import ServerGroup, Server, ServerAccount
from crustsessions.models import CrustCLISession
from crustsessions.models import CrustSessionEvent
from crustsessions.models import SESSION_ESTAB, SESSION_RUN
from crustsessions.models import SESSION_CLOSED_NORMAL, SESSION_CLOSED_LOST



def generate_session_id():
    new_session_id = uuid.uuid4()
    return new_session_id

def start_new_cli_sessions(user_obj, serveraccount_obj, client_addr):
    session_id = generate_session_id()
    new_session = CrustCLISession(
        session_id=session_id,
        remoteuser=user_obj.username,
        serveraccount=str(serveraccount_obj),
        server=str(serveraccount_obj.server),
        status=SESSION_ESTAB,
        client_ip = client_addr[0],
        client_port = client_addr[1]
    )

    new_session.save()
    return new_session


def save_cli_session_event(session_obj, event_time, tty_size, event_content):
    print event_content
    new_event = CrustSessionEvent(
        session=session_obj,
        tty_size_width = tty_size[0],
        tty_size_height = tty_size[1],
        event_time=event_time,
        content='\n'.join(event_content[1])
    )
    new_event.save()

def close_cli_session(session_obj, term_cause):
    session_obj.termination_cause = term_cause
    session_obj.status = SESSION_CLOSED_NORMAL
    session_obj.terminated_at = datetime.now()
    session_obj.save()


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


def get_server_groups_for_user(user_obj):
    return RemoteUserACL.get_filtered_server_groups(user_obj)

def get_servers_by_group(user_obj, server_group):
    return RemoteUserACL.get_filtered_servers_by_group(user_obj, server_group)

def get_server_accounts_by_server(user_obj, server_obj):
    return RemoteUserACL.get_filtered_server_accounts_by_server(
        user_obj,
        server_obj)
