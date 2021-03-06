"""
This module provides access to django models
"""

import os
import sys
import uuid
import json
from datetime import datetime, timedelta
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
from remote_connections.models import RemoteConnection, BanIP
from auth_lib.auth_helpers import ldap_authenticate_user

def generate_session_id():
    new_session_id = uuid.uuid4()
    return new_session_id

def start_new_cli_sessions(user_obj, serveraccount_obj, client_addr, pid):
    session_id = generate_session_id()
    new_session = CrustCLISession(
        session_id=session_id,
        remoteuser=user_obj.username,
        serveraccount=str(serveraccount_obj),
        server=str(serveraccount_obj.server),
        status=SESSION_ESTAB,
        client_ip = client_addr[0],
        client_port = client_addr[1],
        pid = pid
    )

    new_session.save()
    return new_session


def save_cli_session_event(session_obj, event_time, tty_size, event_content):
    #print event_content
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

################### Remote Connections ##########

def close_failed_connection(connection, reason, termination_cause='failure'):
    connection.successful = False
    connection.fail_reason = reason
    connection.terminated_at = datetime.now()
    connection.termination_cause = termination_cause
    connection.save()
    check_connection_ban_ip(connection)

def close_connection(connection, termination_cause='normal stop'):
    connection.successful = True
    connection.terminated_at = datetime.now()
    connection.termination_cause = termination_cause
    connection.save()

def update_connection_state(connection, state):
    connection.state = state
    connection.save()

def check_connection_ban_ip(connection):
    should_ban = False
    now = datetime.now()
    past_min = now - timedelta(seconds=60)
    past_5min = now - timedelta(seconds=300)
    connection_qs = RemoteConnection.objects.filter(
        source_ip=connection.source_ip
    ).filter(
        username=connection.username
    ).filter(
        fail_reason__in=['Invalid Password', 'Remote User not found'])

    past_min_fails = connection_qs.filter(created_at__gte=past_min).count()
    past_5min_fails = connection_qs.filter(created_at__gte=past_5min).count()

    if past_min_fails >= 3 or past_5min_fails >= 3: # mark for ban
        ban_ip = BanIP(ip=connection.source_ip)
        ban_ip.save()
