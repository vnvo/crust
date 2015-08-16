#!/usr/bin/env python
import os
import socket
import sys
import threading
import traceback
import select
import paramiko
import Crypto.Random
import logging
import logging.handlers
import pwd
import time
import datetime
from optparse import OptionParser
from shell_box_menu import ShellBoxMenu
from db_utils import get_remote_user_by_username, get_acls_by_remote_user
from lib.ipaddr import IPNetwork, IPAddress
from lib.terminal import Terminal

SESSION_LOG_PATH = '/var/log/shell_box'

class IgnoreHostKeyPolicy (paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return True

class ChannelClosedException(Exception):
    pass

class TerminalThrobber(threading.Thread):
    def __init__(self, channel, host):
        threading.Thread.__init__(self)
        self.channel = channel
        self.throb = True
        self.daemon = True
        self.message = ""
        self.host = host
        self.update_interval = 0.05

    def run(self):
        # We only do throbbing for interactive sessions
        if self.channel.requested_action != 'interactive':
            return

        self.channel.send("\r\nConnecting to %s ...  "%self.host)
        throbber = ['|', '/', '-', '\\']
        count = 0
        while self.throb:
            self.channel.send("\b" + throbber[count % len(throbber)])
            time.sleep(self.update_interval)
            count += 1
        self.channel.send("\b%s\r\n\r\n" % self.message)

    def stop(self, message):
        self.message = message
        self.throb = False
        self.join()


class SSHGateway (paramiko.ServerInterface):

    def __init__(self, remote_addr):
        self.event = threading.Event()
        self.remote_credentials = None
        self.remote_addr = IPAddress(remote_addr)
        self.user = None

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            logger.debug('Handled a channel request, allowed a session')
            return paramiko.OPEN_SUCCEEDED
        logger.debug('Handled a channel request, denied: ' + kind)
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        logger.debug('Checking password for user %s' % (username))

        user_obj = get_remote_user_by_username(username)
        if not user_obj:
            logger.info('Username "%s" not found'%username)
            return paramiko.AUTH_FAILED

        self.user = user_obj
        if not user_obj.password == password:
            logger.info('Invalid Password for %s'%username)
            return paramiko.AUTH_FAILED

        if False: #user_obj.allowed_ips:
            allowed_list = [IPNetwork(ip) for ip in\
                            user_obj.allowed_ips.split(',')]
            for iprange in allowed_list:
                if self.remote_addr in iprange:
                    self.remote_credentials = (username, password)
                    return paramiko.AUTH_SUCCESSFUL

            logger.info('Username %s not authorized from %s'%(username,
                                                           self.remote_addr))
        logger.info('Authentication OK for %s@%s'%(self.user.username, self.remote_addr))
        self.remote_credentials = (username, password)
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        auths = 'password'
        logger.debug('Returned allowed auths: ' + auths)
        return auths

    def check_channel_exec_request(self, channel, command):
        channel.user_command = command
        channel.requested_action = 'execute'
        logger.debug('Handled an exec request: ' + command)
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        logger.debug('Handled a shell request')
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        channel.term = term
        channel.width = width
        channel.height = height
        channel.requested_action = 'interactive'
        logger.debug('Handled a PTY request (term=%s w=%s h=%s)'%(term, width,
                                                                  height))
        return True

    def check_channel_subsystem_request(self, channel, name):
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
        if channel.paired_interactive_session and \
           channel.paired_interactive_session.active:
            logger.debug('Handled a resize request, new resolution: %ix%i' % (
                width,
                height))
            channel.paired_interactive_session.resize_pty(width, height)


def create_user_log_dirs(username):
    """
    Create a directory to keep logs of user activity
    """
    dir_path = '%s/%s'%(SESSION_LOG_PATH, username)
    try:
        os.makedirs(dir_path)
    except OSError as e:
        logger.info('error while creating log dir %s: %s'%(dir_path, e))

    return dir_path


class SSHExecuteSCPLogger(object):
    action_type = 'exec_scp'

    def __init__(self, username, remote_host, server_user, server_host, scp_cmd):
        self.remote_username = username
        self.remote_host = remote_host
        self.server_user = server_user
        self.server_host = server_host
        self.scp_cmd = scp_cmd.split(' ')[-1].split('/')[-1]
        self.scp_mode = 't'
        if '-f' in scp_cmd:
            self.scp_mode = 'f'

        self.output_name = None
        self.output = None

        self._setup_output()

    def _setup_output(self):
        log_dir_path = create_user_log_dirs(self.remote_username)
        self.output_name = '%s/%s__%s_%s_%s_%s_%s'%(
            log_dir_path,
            datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'),
            self.remote_username,
            self.remote_host,
            self.server_host,
            ['from','to'][self.scp_mode=='t'],
            self.scp_cmd)

        self.output = open(self.output_name, 'wb')
        logger.info('logger ready for scp mode:%s'%self.scp_mode)

    def log(self, data):
        self.output.write(data)
        self.output.flush()

    def finish_up(self):
        self.output.close()


class InteractiveLogger(object):
    action_type = 'interactive'

    def __init__(self, username, remote_host, server_user, server_host, exec_cmd=None):
        self.remote_username = username
        self.remote_host = remote_host
        self.server_user = server_user
        self.server_host = server_host
        self.exec_cmd = exec_cmd
        self.output_name = None
        self.output = None
        self._setup_output()


    def _setup_output(self):
        log_dir_path = create_user_log_dirs(self.remote_username)
        self.output_name = '%s/%s__%s_%s_%s_interactive.log'%(
            log_dir_path,
            datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'),
            self.remote_username,
            self.remote_host,
            self.server_host)

        self.output = open(self.output_name, 'w')
        self.output.write('============= Session Started ============\n')
        self.output.write('%s\n'%str(datetime.datetime.now()))
        self.output.write('Remote User: %s@%s\n'%(self.remote_username,
                                                  self.remote_host))
        self.output.write('Server User: %s@%s\n'%(self.server_user,
                                                  self.server_host))
        if self.exec_cmd:
            self.output.write('Exec CMD: %s\n'%self.exec_cmd)
        self.output.write('==========================================\n\n\n')

    def log(self, data):
        self.output.write(data)
        self.output.flush()

    def finish_up(self):
        end_time = str(datetime.datetime.now())
        self.output.write('============= End: %s ===============\n'%end_time)
        self.output.close()


def configure_logger():
    print "preparint logging ..."
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


def copy_data(source, drain, copy_stderr, session_logger):
    while source.recv_ready():
        data = source.recv(4096)
        #print ('stdin', 'stdout')[copy_stderr] + ': ' + repr(data)
        if len(data) == 0: raise ChannelClosedException()
        drain.sendall(data)

        if session_logger: # and session_logger.action_type!='interactive':
            session_logger.log(data)

    # We only want to copy stderr when we're collecting data
    # from the app channel
    while copy_stderr and source.recv_stderr_ready():
        data = source.recv_stderr(4096)
        if len(data) == 0: raise ChannelClosedException()
        drain.sendall_stderr(data)


def copy_bidirectional_blocking(client, server, session_logger):
    socklist = (client.fileno(), server.fileno())

    # Copy data between the two SSH channels
    channel_closed = False
    abort = False
    while not abort:
        select.select(socklist, socklist, socklist, 1)

        # Force a final run after an abort condition triggered
        # to make sure that all channels are flushed
        if channel_closed == True:
            abort = True

        # Copy data from user to app
        try:
            if session_logger.action_type=='exec_scp':
                if session_logger.scp_mode=='t':
                    copy_data(client, server, False, session_logger)
                else:
                    copy_data(client, server, False, None)

            elif session_logger.action_type=='interactive':
                copy_data(client, server, False, None)
            else:
                copy_data(client, server, False, session_logger)

        except ChannelClosedException:
            channel_closed = True

        # If we receive an EOF we need to shutdown the sending side of the
        # peer's socket to generate an appropriate EOF.
        # This is necessary for tools like scp to terminate correctly
        if client.closed or client.eof_received:
            server.shutdown(1)
            channel_closed = True

        # Copy data from app to user
        try:
            if session_logger.action_type=='exec_scp':
                if session_logger.scp_mode=='f':
                    copy_data(server, client, True, session_logger)
                else:
                    copy_data(server, client, True, None)
            else:
                copy_data(server, client, True, session_logger)

        except ChannelClosedException:
            channel_closed = True

        if server.closed or server.eof_received:
            client.shutdown(1)
            channel_closed = True


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


def send_message(channel, message):
    if channel.requested_action == 'interactive':
        channel.send(message + "\r\n\r\n")


def cleanup(userchan, app):
    usertransport = userchan.get_transport()
    logger.info('User %s disconnected' % (usertransport.get_username()))

    # We explicitly need to close the user's channel before the transport
    # to provide a nice shutdown for the client, otherwise ssh(1) get's confused

    userchan.close()
    time.sleep(0.5)
    usertransport.close()
    if app:
        app.close()

def run_session(client, client_addr):
    user = paramiko.Transport(client)
    add_host_keys(user)
    remote_host = client_addr[0]
    sshgw = SSHGateway(remote_host)

    # We initialized a transport and now start SSH negotiation
    try:
        user.start_server(server=sshgw)
    except (paramiko.SSHException, EOFError) as e:
        logger.info('SSH negotiation failed: ' + str(e))
        sys.exit(1)

    # Waiting for client to authenticate and initiate a session
    # FIXME: We only support a single channel per Transport
    userchan = user.accept(60)
    if userchan is None:
        logger.warn('Client failed to open a channel')
        sys.exit(1)

    # Waiting for client to request something
    # This event is triggered from one of the handlers
    sshgw.event.wait(60)
    if not sshgw.event.isSet():
        logger.warn('Client never asked for a shell or sftp.')
        sys.exit(1)

    target_server_account = ShellBoxMenu(userchan, sshgw.user, remote_host, logger).main()
    logger.info('Selected: %s'%target_server_account)
    if not target_server_account:
        send_message(userchan, 'No Target Selected,Exit ...')
        cleanup(userchan, None)
        return 1

    spinner = TerminalThrobber(userchan, target_server_account)
    spinner.start()

    # Connect to the app
    app = paramiko.SSHClient()
    app.set_missing_host_key_policy(IgnoreHostKeyPolicy())

    try:
        target_server = target_server_account.server
        server_host = target_server.server_ip
        server_port = target_server.sshv2_port or 22
        username = target_server_account.username
        password = target_server_account.password
        app.connect(
            hostname=server_host, port=server_port,
            username=username, password=password, timeout=10,
            allow_agent=False, look_for_keys=False)
    except Exception as e:
        spinner.stop("error!")
        logger.error('Failed to connect to %s: %s' %  (server_host, str(e)))
        send_message(userchan, 'Failed to connect to %s: %s'%(
            target_server_account, e))
        time.sleep(3)
        cleanup(userchan, app)
        return 1

    spinner.stop("... And We Are Connected.")
    appchan = None

    if userchan.requested_action == 'sftp':
        appchan = app.get_transport().open_session()
        appchan.invoke_subsystem('sftp')

    elif userchan.requested_action == 'interactive':
        appchan = app.invoke_shell(userchan.term,
                                   userchan.width,
                                   userchan.height)
        userchan.paired_interactive_session = appchan
        remote_username = sshgw.remote_credentials[0]
        session_logger = InteractiveLogger(remote_username, remote_host,
                                           username, server_host)

    elif userchan.requested_action == 'execute':
        appchan = app.get_transport().open_session()
        appchan.exec_command(userchan.user_command)
        remote_username = sshgw.remote_credentials[0]
        if 'scp' in userchan.user_command:
            session_logger = SSHExecuteSCPLogger(remote_username, remote_host,
                                                 username, server_host,
                                                 userchan.user_command)
        else:
            session_logger = InteractiveLogger(remote_username, remote_host,
                                               username, server_host,
                                               userchan.user_command)
    else:
        logger.warn('Unknown or unset action for userchannel: %s, aborting'%userchan.requested_action)
        cleanup(userchan, app)
        return 1

    copy_bidirectional_blocking(userchan, appchan, session_logger)
    session_logger.finish_up()

    send_message(userchan, 'Terminating session ...')

    # This could block indefinitely if the app never sends a return code
    # and doesn't tear down the connection... ignore for now
    rc = appchan.recv_exit_status()

    logger.debug('Shutting down session with exit code %d' % rc)
    userchan.send_exit_status(rc)

    cleanup(userchan, app)
    return 0

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

    parser.add_option('-l', '--listen-address', action='store', dest='bind-address', default='0.0.0.0',
        help="Bind to this interface [default: %default]")
    parser.add_option('-p', '--port', action='store', type=int, dest='listen-port', default=2200,
        help="Listen on this port [default: %default]")
    parser.add_option('--host-rsa-key', action='store', dest='host-rsa-key', default='/etc/hs/sshgateway/ssh_host_rsa_key',
        help="Use this file as RSA host key [default: %default]")
    parser.add_option('--host-dsa-key', action='store', dest='host-dsa-key', default='/etc/hs/sshgateway/ssh_host_dsa_key',
        help="Use this file as DSA host key [default: %default]")
    parser.add_option('--log-target', action='store', dest='log-target', default='syslog',
        help="Send log output to this target. Can be either 'syslog', 'stdout' or a path to a file. [default: %default]")
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
        help="Log more information during the sesion. Only one -v is supported")
    parser.add_option('-g', '--gateway-agent', action='store', dest='gateway-agent', default='127.0.0.1',
        help="Address or hostname for the Gateway agent. [default: %default]")
    parser.add_option('-u', '--user', action='store', dest='daemon-user', default='nobody',
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