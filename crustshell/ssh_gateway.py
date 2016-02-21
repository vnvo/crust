#!/usr/bin/env python
import os
import socket
import sys
import threading
import traceback
import paramiko
import Crypto.Random
import logging
import logging.handlers
import pwd
import time
import datetime
import re
import redis
import simplejson as json
from optparse import OptionParser
from shell_box_menu import ShellBoxMenu
from db_utils import get_remote_user_by_username, get_acls_by_remote_user
from db_utils import RemoteUserACL
from db_utils import RemoteConnection
from db_utils import close_connection, close_failed_connection, update_connection_state
from db_utils import ldap_authenticate_user
from lib.ipaddr import IPNetwork, IPAddress
from client import send_message, cleanup, SESSION_LOG_PATH
from client import handle_connection

class ChannelMan(threading.Thread):
    def __init__(self, channel, pid, remote_connection):
        threading.Thread.__init__(self)
        self.channel = channel
        self.remote_connection = remote_connection
        self.pid_str = str(pid)
        self.redis_conn = None
        self.pubsub = None
        self._setup()

    def _setup(self):
        """
        Register to messaging backend
        """
        self.redis_conn = redis.Redis()
        self.pubsub = self.redis_conn.pubsub()
        self.pubsub.subscribe(self.pid_str)

    def run(self):
        for msg in self.pubsub.listen():
            print msg
            try:
                if msg['type'] != 'message':
                    continue

                if msg['data'].startswith('KILL'):
                    command, admin = msg['data'].split(':')
                    close_connection(self.remote_connection, 'Killed by %s'%admin)
                    self.channel.send('\r\nSession Killed by %s\r\n'%admin)
                    time.sleep(1)
                    os.system('sudo kill -9 %s'%self.pid_str)

                elif msg['data'].startswith('MSG'):
                    data = re.findall('MSG:(.*)', msg['data'])
                    msg_info = json.loads(data[0])
                    self.channel.send(
                        '\r\n\r\n%s: %s\r\n'%(msg_info['sender'],
                                              msg_info['message']))
            except Exception as e:
                print e
                continue

    def stop(self):
        self.pubsub.unsubscribe()
        self.join()


class SSHGateway (paramiko.ServerInterface):

    def __init__(self, remote_addr, remote_connection=None):
        self.remote_connection = remote_connection
        self.event = threading.Event()
        self.remote_credentials = None
        self.remote_addr = IPAddress(remote_addr)
        self.direct_request = None
        self.username = None
        self.user = None
        self.tty_size = None
        self.ignore_resize = True

    def check_channel_request(self, kind, chanid):
        print 'check_channel_request'
        if kind == 'session':
            logger.debug('Handled a channel request, allowed a session')
            return paramiko.OPEN_SUCCEEDED
        logger.debug('Handled a channel request, denied: ' + kind)
        close_failed_connection(self.remote_connection,
                                'Channel kind %s not allowed'%kind)
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_direct_connection(self, username):
        print 'check_direct_connection'
        """
        In direct connection mode, client would specify the username
        as proto#server-account-username#server-name#actual-remote-username .
        In this mode, crust will try to connect the remote-user directly to
        target server without presenting the menu.
        """
        conn_info = re.findall(
            '(.*)#(.*)#(.*)#(.*)', username
        )
        if conn_info and len(conn_info[0])==4: #direct connection requested
            logger.info('Direct Mode Connection Detected ==> %s'%str(conn_info))
            username = conn_info[0][-1]
            self.direct_request = {
                'proto':conn_info[0][0],
                'server_account_username':conn_info[0][1],
                'server_name_ip':conn_info[0][2]}
            self.remote_connection.mode = 'direct'

        self.remote_connection.username = username
        self.remote_connection.save()
        print 'direct_connection check done ...'
        return username

    def check_auth_password(self, username, password):
        print 'check_auth_password'
        update_connection_state(self.remote_connection, 'auth')
        logger.debug('Checking password for user %s' % (username))
        username = self.check_direct_connection(username)
        print username
        try:
            user_obj = get_remote_user_by_username(username)
        except Exception as e:
            print e
            close_failed_connection(self.remote_connection, 'Remote User not found')

        if not user_obj:
            logger.info('Username "%s" not found'%username)
            close_failed_connection(self.remote_connection, 'Remote User not found')
            return paramiko.AUTH_FAILED

        self.user = user_obj
        print self.user
        if self.user.auth_mode == 'ldap':
            if self.user.ldap_cn:
                result = ldap_authenticate_user(
                    self.user.username, self.user.ldap_cn, password)
                if not result:
                    close_failed_connection(self.remote_connection,
                                            'Invalid Password(LDAP)')
                    return paramiko.AUTH_FAILED
            else:
                close_failed_connection(self.remote_connection,
                                        'LDAP CN Not Set')
                return paramiko.AUTH_FAILED

        elif not user_obj.password == password: #local mode
            logger.info('Invalid Password for %s'%username)
            close_failed_connection(self.remote_connection, 'Invalid Password')
            return paramiko.AUTH_FAILED

        if user_obj.allow_ip:
            allowed_list = [IPNetwork(ip) for ip in\
                            user_obj.allow_ip.split(',')]
            for iprange in allowed_list:
                if self.remote_addr in iprange:
                    self.remote_credentials = (username, password)
                    return paramiko.AUTH_SUCCESSFUL

            logger.info('Username %s not authorized from %s'%(username,
                                                           self.remote_addr))
            close_failed_connection(self.remote_connection, 'Reject Source IP')
            return paramiko.AUTH_FAILED

        logger.info('Authentication OK for %s@%s'%(self.user.username, self.remote_addr))
        self.remote_credentials = (username, password)
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        print 'get_allowed_auths'
        auths = 'password'
        logger.debug('Returned allowed auths: ' + auths)
        return auths

    def check_channel_exec_request(self, channel, command):
        print 'check_channel_exec_request'
        channel.user_command = command
        channel.requested_action = 'execute'
        logger.debug('Handled an exec request: ' + command)
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        print 'check_channel_shell_request'
        logger.debug('Handled a shell request')
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        print 'check_channel_pty_request'
        channel.term = term
        channel.width = width
        channel.height = height
        channel.requested_action = 'interactive'
        logger.debug('Handled a PTY request (term=%s w=%s h=%s)'%(term, width,
                                                                  height))
        self.tty_size = (width, height)
        return True

    def check_channel_subsystem_request(self, channel, name):
        print 'check_channel_subsystem_request'
        if name == 'sftp':
            logger.debug('Handled a subsystem request, allowed sftp')
            # FIXME: Probably better done via subsystem handlers
            channel.requested_action = 'sftp'
            self.event.set()
            return True

        logger.debug('Handled a subsystem request, denied: ' + name)
        return False

    def check_channel_window_change_request(self, channel, width,
                                            height, pixelwidth, pixelheight):
        print '=== window change request ====='
        if self.ignore_resize:
            return
        try:

            if channel.paired_interactive_session and \
               channel.paired_interactive_session.active:
                logger.debug('Handled a resize request, new resolution: %ix%i' % (
                    width,
                    height))
                channel.paired_interactive_session.resize_pty(width, height)
                self.tty_size = (width, height)
        except:
            logger.exception('window resize: ')


def configure_logger():
    logtemp = logging.getLogger('sshgw')

    if config['verbose']:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logtemp.setLevel(level)
    lh = None
    lf = None

    logtarget = config['log-target']

    log_format = '%(asctime)s [%(process)s] %(levelname)s: %(message)s'

    if logtarget == 'syslog':
        lh = logging.handlers.SysLogHandler(
            address='/var/log',
            facility=logging.handlers.SysLogHandler.LOG_DAEMON)

        # Push messages of severity CRITICAL also to stdout since they prevent
        # the ssh-gateway from running
        stdout = logging.StreamHandler()
        stdout.setLevel(logging.CRITICAL)
        stdout.setFormatter(logging.Formatter(log_format))
        logtemp.addHandler(stdout)

    elif logtarget == 'stdout':
        lh = logging.StreamHandler()
        log_format = '%(asctime)s '+ log_format
    else:
        lh = logging.handlers.RotatingFileHandler(
            '%s/shell_box.log'%SESSION_LOG_PATH,
            maxBytes=1024*1024*1024,
            backupCount=5)

    lf = logging.Formatter(log_format)
    lh.setFormatter(lf)
    logtemp.addHandler(lh)

    # Hackaround-disable paramiko's builtin logger since we handle
    # all exceptions ourselves nicely
    logging.getLogger('paramiko.transport').addHandler(
        logging.FileHandler('/dev/null'))

    return logtemp



def read_host_keys():
    rsakey = config['host-rsa-key']
    if rsakey:
        try:
            config['loaded-host-rsa-key'] = paramiko.RSAKey(filename=rsakey)
        except Exception as e:
            logger.critical('Failed to load RSA host key: ' + str(e))

    dsakey = config['host-dsa-key']
    if dsakey:
        try:
            config['loaded-host-dsa-key'] = paramiko.DSSKey(filename=dsakey)
        except Exception as e:
            logger.critical('Failed to load DSA host key: ' + str(e))

    if not ('loaded-host-rsa-key' in config or 'loaded-host-dsa-key' in config):
        logger.critical('Failed to load any host key')
        sys.exit(1)


def add_host_keys(transport):
    if 'loaded-host-rsa-key' in config:
        transport.add_server_key(config['loaded-host-rsa-key'])

    if 'loaded-host-dsa-key' in config:
        transport.add_server_key(config['loaded-host-dsa-key'])

    # Optional, requires /etc/ssh/moduli
    transport.load_server_moduli()



def run_session(client, client_addr):
    paramiko.Transport._CLIENT_ID = 'Crust_1.0.1'
    user = paramiko.Transport(client)
    add_host_keys(user)
    remote_host = client_addr[0]
    remote_connection = RemoteConnection(
        source_ip=remote_host, username='-',
        source_port=client_addr[1], pid=os.getpid())
    remote_connection.save()
    sshgw = SSHGateway(remote_host, remote_connection)

    # We initialized a transport and now start SSH negotiation
    try:
        user.start_server(server=sshgw)
    except (paramiko.SSHException, EOFError) as e:
        logger.info('SSH negotiation failed: ' + str(e))
        close_failed_connection(remote_connection, str(e))
        sys.exit(1)

    # Waiting for client to authenticate and initiate a session
    # FIXME: We only support a single channel per Transport
    userchan = user.accept(60)
    if userchan is None:
        logger.warn('Client failed to open a channel')
        remote_connection.terminated_at = datetime.datetime.now()
        remote_connection.save()
        sys.exit(1)

    # Waiting for client to request something
    # This event is triggered from one of the handlers
    sshgw.event.wait(60)
    if not sshgw.event.isSet():
        logger.warn('Client never asked for a shell or sftp.')
        close_failed_connection(remote_connection, 'Did not ask for shell or copy')
        sys.exit(1)

    channel_man = ChannelMan(userchan, os.getpid(), remote_connection)
    channel_man.start()
    update_connection_state(remote_connection, 'select server')
    if sshgw.direct_request:
        update_connection_state(remote_connection, 'select server')
        info = sshgw.direct_request
        target_server_account = RemoteUserACL.check_direct_access(
            sshgw.user, info['proto'], info['server_account_username'], info['server_name_ip'])
        print target_server_account
        if not target_server_account:
            send_message(userchan, 'Invalid Direct Connection Info, Exit.')
            close_failed_connection(
                remote_connection, 'Invalid Direct:%s#%s#%s'%(
                    info['proto'], info['server_account_username'], info['server_name_ip']))
            cleanup(userchan, None)
            return 1
        handle_connection(target_server_account, sshgw,
                          remote_host, userchan, remote_connection)
    else:
        try:
            sshgw.ignore_resize = True
            target_server_account = ShellBoxMenu(
                userchan, sshgw, remote_host, remote_connection, logger
            ).main()
        except Exception as e:
            close_failed_connection(remote_connection, str(e))
            channel_man.stop()
            cleanup(userchan, None)
            print e
            raise

    sshgw.ignore_resize = False

    #logger.info('Selected: %s'%target_server_account)
    #if not target_server_account:
    #    send_message(userchan, 'No Target Selected, Exit')
    close_connection(remote_connection)
    channel_man.stop()
    cleanup(userchan, None)
    return 1

    update_connection_state(remote_connection, 'session')

    #ssh or telnet
    #if target_server_account.protocol == 'ssh':
    #    ret = handle_ssh_connection(
    #        target_server_account, sshgw, remote_host, userchan, spinner)
    #    close_connection(remote_connection)
    #    channel_man.stop()
    #    return ret
    #elif target_server_account.protocol == 'ssh and telnet':
    #    pass
    #else: #telnet
    #    print '============== handle telnet connection ==============='
    #    ret = handle_telnet_connection(
    #        target_server_account, sshgw, remote_host, userchan, spinner)
    #    close_connection(remote_connection)
    #    channel_man.stop()
    #    return ret

def drop_privileges():

    # Nothing to do, not running as root
    if os.getuid() != 0:
        return

    username = config['daemon-user']
    uid = pwd.getpwnam(username)[2]

    if not uid:
        raise "User %s doesn't exist" % (username)

    os.setuid(uid)

    if os.getuid() != uid or os.geteuid() != uid:
        raise "Failed to change user to " + username
        sys.exit(1)


def parse_options(print_help=False):
    parser = OptionParser()

    parser.add_option('-l', '--listen-address', action='store',
                      dest='bind-address', default='0.0.0.0',
                      help="Bind to this interface [default: %default]")
    parser.add_option('-p', '--port', action='store', type=int,
                      dest='listen-port', default=2200,
                      help="Listen on this port [default: %default]")
    parser.add_option('--host-rsa-key', action='store', dest='host-rsa-key',
                      default='/etc/hs/sshgateway/ssh_host_rsa_key',
                      help="Use this file as RSA host key [default: %default]")
    parser.add_option('--host-dsa-key', action='store', dest='host-dsa-key',
                      default='/etc/hs/sshgateway/ssh_host_dsa_key',
                      help="Use this file as DSA host key [default: %default]")
    parser.add_option(
        '--log-target', action='store', dest='log-target',
        default='syslog',
        help="Send log to this target. Can be either 'syslog', 'stdout' or a file path. [default: %default]")
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',default=False,
                      help="Log more information during the sesion. Only one -v is supported")
    parser.add_option('-g', '--gateway-agent', action='store', dest='gateway-agent',
                      default='127.0.0.1',
                      help="Address or hostname for the Gateway agent. [default: %default]")
    parser.add_option('-u', '--user', action='store', dest='daemon-user',
                      default='nobody',
                      help="When run as root, use this username after reading the host keys and binding to the listen-socket. [default: %default]")

    if print_help:
        parser.print_help()
        return

    (options, args) = parser.parse_args()
    return options.__dict__


def main():
    global config, logger

    config = parse_options()
    logger = configure_logger()

    read_host_keys()

    # Bind to the socket
    try:
        logger.info('Listening for connections on %s:%i'%(
            config['bind-address'],
            config['listen-port']))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((config['bind-address'], config['listen-port']))

        # Set a timeout so that the accept loop doesn't block too long in low-traffic environments
        sock.settimeout(5)
    except Exception as e:
        logger.critical('Bind failed: ' + str(e))
        sys.exit(1)

    # If we're run as root, drop the privileges after binding to the port.
    #try:
    #    drop_privileges()
    #except Exception as e:
    #    logger.critical('Failed to change user to %s: %s' %  (username, str(e)))
    #    sys.exit(1)

    # Listen for connections
    try:
        sock.listen(100)
    except Exception as e:
        logger.critical('Listen failed: ' + str(e))
        sys.exit(1)

    print 'Crust SSH-GW is ready ...'
    # Accept loop
    try:
        while True:
            client = None

            # Wait for a connection or timeout
            try:
                client, addr = sock.accept()
            except socket.timeout:
                pass

            # Try to reap any leftover childs
            try:
                while os.wait3(os.WNOHANG)[1] != 0:
                    continue
            except OSError:
                pass

            # There was no client connected, try again
            if not client:
                continue

            # We've got a connection, fork!
            logger.info('Client connected from ' + ':'.join(map(str, addr)))
            pid = os.fork()

            if pid == 0:
                # We are a child, run a session and then exit
                Crypto.Random.atfork()
                sock.close()
                run_session(client, addr)
                # When run_sesion returns everything is cleaned up, we can disconnect
                sys.exit(0)
            else:
                # We are the parent, we need to release the client socket
                client.close()


    except Exception as e:
        logger.critical('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__': main()
