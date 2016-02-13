#!/usr/bin/env python
import os
import socket
import struct
import sys
import threading
import traceback
import select
import paramiko
import telnetlib
import Crypto.Random
import logging
import logging.handlers
import pwd
import time
import datetime
import re
from optparse import OptionParser
from shell_box_menu import ShellBoxMenu
from db_utils import get_remote_user_by_username, get_acls_by_remote_user
from db_utils import start_new_cli_sessions, save_cli_session_event
from db_utils import close_cli_session
from db_utils import RemoteUserACL
from db_utils import RemoteConnection
from db_utils import close_connection, close_failed_connection, update_connection_state
from lib.ipaddr import IPNetwork, IPAddress
from lib.terminal import Terminal
from lib.terminal import css_renditions
#from shell_menu import startCrustShellMenu

SESSION_LOG_PATH = '/var/log/shell_box'

class IgnoreHostKeyPolicy (paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return True

class ChannelClosedException(Exception):
    pass

class TerminalThrobber(threading.Thread):
    def __init__(self, channel, connection):
        threading.Thread.__init__(self)
        self.channel = channel
        self.throb = True
        self.daemon = True
        self.message = ""
        self.connection = connection
        self.update_interval = 0.05

    def run(self):
        # We only do throbbing for interactive sessions
        if self.channel.requested_action != 'interactive':
            return

        self.channel.send('\r\n====================================================================\r\n')
        self.channel.send("\r\nConnecting to %s ...  "%self.connection)
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
        if kind == 'session':
            logger.debug('Handled a channel request, allowed a session')
            return paramiko.OPEN_SUCCEEDED
        logger.debug('Handled a channel request, denied: ' + kind)
        close_failed_connection(self.remote_connection,
                                'Channel kind %s not allowed'%kind)
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_direct_connection(self, username):
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
        return username

    def check_auth_password(self, username, password):
        update_connection_state(self.remote_connection, 'auth')
        logger.debug('Checking password for user %s' % (username))
        username = self.check_direct_connection(username)
        try:
            user_obj = get_remote_user_by_username(username)
        except Exception as e:
            close_failed_connection(self.remote_connection, 'Remote User not found')

        if not user_obj:
            logger.info('Username "%s" not found'%username)
            close_failed_connection(self.remote_connection, 'Remote User not found')
            return paramiko.AUTH_FAILED

        self.user = user_obj
        if self.user.auth_mode == 'ldap':
            pass

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
        self.tty_size = (width, height)
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

    def __init__(self, sshgw, remote_host, serveraccount_obj, exec_cmd=None):
        self.remoteuser_obj = sshgw.user
        self.serveraccount_obj = serveraccount_obj
        self.sshgw = sshgw
        self.tty_size = sshgw.tty_size
        self.remote_username = self.remoteuser_obj.username
        self.remote_host = remote_host
        self.server_user = serveraccount_obj.username
        self.server_host = serveraccount_obj.server.server_ip
        self.exec_cmd = exec_cmd
        self.output_name = None
        self.output = None
        self.terminal = Terminal(self.tty_size[1], self.tty_size[0])#rows(height), cols(width)
        self.debug_out = open('/tmp/tt.log', 'w')
        self.debug_out.write(css_renditions()+'\n\n\n')
        self.session = None
        self._setup_output()
        self._setup_session(self.remoteuser_obj, serveraccount_obj, remote_host)

    def _setup_session(self, remoteuser_obj, serveraccount_obj, remote_host):
        self.session = start_new_cli_sessions(
            remoteuser_obj, serveraccount_obj, (remote_host, 0), os.getpid()
        )

    def _write_session_event(self, content):
        if self.tty_size != self.sshgw.tty_size:
            self.tty_size = self.sshgw.tty_size
            self.terminal.resize(self.tty_size[1], self.tty_size[0])

        if self.tty_size is None:
            self.tty_size(80,60)

        save_cli_session_event(self.session, time.time(),
                               self.sshgw.tty_size, content)

    def _close_session(self, term_cause):
        close_cli_session(self.session, term_cause)

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

    def log(self, data, debug=False):
        self.output.write(data)
        self.output.flush()
        if debug:
            self.terminal.write(data)
            #cur_pos = self.terminal.get_cursor_position()
            self._write_session_event(self.terminal.dump_html())

    def finish_up(self):
        end_time = str(datetime.datetime.now())
        self.output.write('============= End: %s ===============\n'%end_time)
        self.output.close()
        self.debug_out.close()
        self._close_session('CLOSED-NORMAL')

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


def check_user_command(command_buff, apply_acl):
    print '*******************************************************************************'
    command = command_buff.strip()
    print command
    print apply_acl.id
    print apply_acl.command_group
    #acl = server_account.apply_acl
    #print acl.command_group

    if apply_acl and apply_acl.command_group:
        if apply_acl.command_group.check_command(command) == 'allow':
            return True
        else:
            return False

    return True

def copy_data_from_client(source, drain, copy_stderr, session_logger,
                          command_buff=None, apply_acl=None):

    while source.recv_ready():
        data = source.recv(4096)
        #print ('stdin', 'stdout')[copy_stderr] + ': ' + repr(data)
        if len(data) == 0: raise ChannelClosedException()
        print 'command_buff=',command_buff
        x = '\b' in data
        print x
        print 'data=', data, [ord(i) for i in data]
        if command_buff is not None:
            for ch in data:
                if ord(ch) in [8, 127]: #del or backspace
                    command_buff = command_buff[:-1]
                else:
                    command_buff += ch

        if command_buff is not None and '\r' in data: #user has hit the enter
            #command_buff += data
            if not check_user_command(command_buff, apply_acl):
                source.sendall('\r\n** You can not run this command! **\r\n')
                drain.sendall('\b'*len(command_buff))
            else:
                drain.sendall(data)
            command_buff = ''

        else:
            drain.sendall(data)

        if session_logger: # and session_logger.action_type!='interactive':
            session_logger.log(data)

    # We only want to copy stderr when we're collecting data
    # from the app channel
    while copy_stderr and source.recv_stderr_ready():
        data = source.recv_stderr(4096)
        if len(data) == 0: raise ChannelClosedException()
        drain.sendall_stderr(data)

    return command_buff

def copy_data_from_server(source, drain, copy_stderr, session_logger):
    while source.recv_ready():
        data = source.recv(4096)
        #print ('stdin', 'stdout')[copy_stderr] + ': ' + repr(data)
        if len(data) == 0: raise ChannelClosedException()
        drain.sendall(data)

        if session_logger: # and session_logger.action_type!='interactive':
            session_logger.log(data, True)

    # We only want to copy stderr when we're collecting data
    # from the app channel
    while copy_stderr and source.recv_stderr_ready():
        data = source.recv_stderr(4096)
        if len(data) == 0: raise ChannelClosedException()
        drain.sendall_stderr(data)


def copy_bidirectional_blocking(client, server, session_logger, apply_acl=None):
    socklist = (client.fileno(), server.fileno())

    # Copy data between the two SSH channels
    channel_closed = False
    abort = False
    command_buff = None
    if session_logger.action_type == 'interactive':
        command_buff = ''

    print command_buff

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
                    copy_data_from_client(client, server, False, session_logger, apply_acl=apply_acl)
                else:
                    copy_data_from_client(client, server, False, None, apply_acl=apply_acl)

            elif session_logger.action_type!='interactive':
                copy_data_from_client(client, server, False, None, apply_acl=apply_acl)
            else:
                command_buff = copy_data_from_client(
                    client, server, False, session_logger, command_buff, apply_acl=apply_acl)

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
                    copy_data_from_server(server, client, True, session_logger)
                else:
                    copy_data_from_server(server, client, True, None)
            else:
                copy_data_from_server(server, client, True, session_logger)

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
    paramiko.Transport._CLIENT_ID = 'Crust_1.0.1'
    user = paramiko.Transport(client)
    add_host_keys(user)
    remote_host = client_addr[0]
    remote_connection = RemoteConnection(source_ip=remote_host, username='-', source_port=client_addr[1])
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

    update_connection_state(remote_connection, 'select server')
    if sshgw.direct_request:
        info = sshgw.direct_request
        target_server_account = RemoteUserACL.check_direct_access(
            sshgw.user, info['proto'],
            info['server_account_username'], info['server_name_ip'])
        print target_server_account
        if not target_server_account:
            send_message(userchan, 'Invalid Direct Connection Info, Exit.')
            close_failed_connection(
                remote_connection,
                'Invalid Direct:%s#%s#%s'%(info['proto'],
                                           info['server_account_username'],
                                           info['server_name_ip']))
            cleanup(userchan, None)
            return 1
    else:
        try:
            sshgw.ignore_resize = True
            target_server_account = ShellBoxMenu(
                userchan, sshgw.user, remote_host, logger
            ).main()
        except Exception as e:
            print e
            raise

    sshgw.ignore_resize = False

    logger.info('Selected: %s'%target_server_account)
    if not target_server_account:
        send_message(userchan, 'No Target Selected, Exit')
        close_connection(remote_connection)
        cleanup(userchan, None)
        return 1

    update_connection_state(remote_connection, 'session')
    spinner = TerminalThrobber(
        userchan,
        '%s@%s'%(target_server_account,
                 target_server_account.server)
    )

    #ssh or telnet
    if target_server_account.protocol == 'ssh':
        ret = handle_ssh_connection(
            target_server_account, sshgw, remote_host, userchan, spinner)
        close_connection(remote_connection)
        return ret
    #elif target_server_account.protocol == 'ssh and telnet':
    #    pass
    else: #telnet
        print '============== handle telnet connection ==============='
        ret = handle_telnet_connection(
            target_server_account, sshgw, remote_host, userchan, spinner)
        close_connection(remote_connection)
        return ret


def handle_telnet_connection(server_account, sshgw, remote_host, userchan, spinner):
    target_server = server_account.server
    server_host = target_server.server_ip
    server_port = target_server.telnet_port or 23
    username = server_account.username
    password = server_account.password

    print 'account pass mode: ', server_account.password_mode
    if server_account.password_mode=='ask user':
        print 'asking for pass'
        user_pass = ask_for_pass(userchan, username, server_host)
        print 'asked for pass'
        password = user_pass

    spinner.start()
    tc = telnetlib.Telnet(host=server_host, port=server_port)
    tc.set_option_negotiation_callback(process_option)

    def handle_auth():
        print 'handle_auth ...'
        index, match_obj, text = tc.expect(
            ['[U|u]sername: ', '[L|l]ogin:', '[L|l]oginname', '[P|p]assword'])
        print '======================================'
        print index, text
        print '======================================'
        if index == 3: #asking for password
            pass_word = '%s\n'%password
            tc.write(pass_word.encode('ascii'))
            return 'done'

        else: #asking for username
            print 'asking for username'
            user_name = '%s\n'%username.strip()
            tc.write(user_name.encode('ascii'))
            print 'username sent ...'
            return 'continue'

    def handle_shell():
    	print 'handle_shell ...'
        index, match_obj, text = tc.expect(
            ['%', '$', '#', '[I|i]ncorrect', '[E|e]rror']
        )
        print index, text
        if index >= 3:
            return 'failed'

        return 'done'

    while True:
        status = handle_auth()
        if status == 'done':
            status = handle_shell()
            if status == 'done':
                break
            else:
                send_message(userchan, 'Failed to connect to %s: %s'%(
                    server_account, 'Auth Failed'))
                cleanup(userchan, tc.get_socket())
                return 1
        elif status == 'continue':
            continue

        else:
            send_message(userchan, 'Failed to connect to %s: %s'%(
                server_account, 'Auth Failed'))
            cleanup(userchan, tc.get_socket())
            return 1

    spinner.stop("... And We Are Connected.")
    print 'connected, spinner stopped ...'
    ### We have access to shell
    session_logger = InteractiveLogger(sshgw, remote_host,
                                       server_account,
                                       None)
    class TelnetSession:
        def __init__(self, tc):
            self.tc = tc
            self.active = True

        def resize_pty(self, w, h):
            print 'telnet session resize: ', w, h
            naws_command = struct.pack(
                '!BBBHHBB',
                255, 250, 31, # IAC SB NAWS
                w, h,
                255, 240) # IAC SE
            self.tc.get_socket().send(naws_command)

    userchan.paired_interactive_session = TelnetSession(tc)
    if sshgw.tty_size:
        userchan.paired_interactive_session.resize_pty(*sshgw.tty_size)

    copy_bidirectional_blocking_telnet(userchan, tc,
                                       session_logger,
                                       server_account.apply_acl)
    session_logger.finish_up()
    send_message(userchan, 'Terminating session ...')
    #logger.debug('Shutting down session with exit code %d' % rc)
    userchan.send_exit_status(0)
    cleanup(userchan, tc.get_socket())

    return 0

def process_option(tsocket, command, option):
    print 'process options called', command, option

    from telnetlib import IAC, DO, DONT, WILL, WONT, SB, SE, TTYPE, NAWS
    if command == DO and option == TTYPE:
        tsocket.sendall(IAC + WILL + TTYPE)
        print 'Sending terminal type "xterm"'
        tsocket.sendall(IAC + SB + TTYPE + '\0' + 'xterm' + IAC + SE)
    elif command == DO and option == NAWS:
        print 'WILL NAWS', ord(option)
        tsocket.sendall(IAC + WILL + option)
    elif command in (DO, DONT):
        print 'Will not', ord(option)
        tsocket.sendall(IAC + WONT + option)
    elif command in (WILL, WONT):
        print 'Do not', ord(option)
        tsocket.sendall(IAC + DONT + option)


def copy_bidirectional_blocking_telnet(client, server, session_logger=None, apply_acl=None):
    socklist = (client.fileno(), server.get_socket().fileno())

    channel_closed = False
    abort = False
    command_buff = None
    if session_logger.action_type == 'interactive':
        command_buff = ''

    print command_buff

    while not abort and not channel_closed:
        rlist, wlist, elist = select.select([client.fileno()], [], [], 0.03)
        if channel_closed == True:
            abort = True
        try:
            if rlist:
                client_data = client.recv(1024)
                #print 'recv client data: "%s"'%client_data, len(client_data)
                print 'command_buff=',command_buff
                print 'data=', client_data, [ord(i) for i in client_data]
                if command_buff is not None:
                    for ch in client_data:
                        if ord(ch) in [8, 127]: #del or backspace
                            command_buff = command_buff[:-1]
                        else:
                            command_buff += ch

                if command_buff is not None and '\r' in client_data: #user has hit the enter
                    if not check_user_command(command_buff, apply_acl):
                        print 'deny command: %s'%command_buff
                        client.sendall('\r\n** You nan not run this command! **\r\n\r\n')
                        server.write('\b'*len(command_buff))
                    else:
                        server.write(client_data)
                    command_buff=''

                else:
                    server.write(client_data)
                session_logger.log(client_data)

            srlist, swlist, selist = select.select([server.get_socket().fileno()], [], [], 0.03)
            if srlist:
                try:
                    server_data = server.read_very_eager()
                except:
                    logger.exception('telnet:')
                    print 'server is closed ...'
                    server.close()
                    abort = True
                else:
                    if server_data:
                        print 'recv server data: len=%s'%len(server_data)
                        client.sendall(server_data)
                        session_logger.log(server_data, True)

        except ChannelClosedException:
            channel_closed = True
        except Exception as e:
            print e
            abort = True

def ask_for_pass(userchan, username, server_host):
    userchan.send('\r\n Please, Enter Your Pass (%s@%s):'%(username, server_host))
    user_pass = ''
    while '\n' not in user_pass and '\r' not in user_pass:
        user_pass += userchan.recv(1024)
        #print user_pass

    return user_pass.strip()


def handle_ssh_connection(server_account, sshgw, remote_host, userchan, spinner):
    # Connect to the app
    app = paramiko.SSHClient()
    app.set_missing_host_key_policy(IgnoreHostKeyPolicy())

    try:
        target_server = server_account.server
        server_host = target_server.server_ip
        server_port = target_server.sshv2_port or 22
        username = server_account.username
        password = server_account.password
        print 'account pass mode: ', server_account.password_mode
        if server_account.password_mode=='ask user':
            print 'asking for pass'
            user_pass = ask_for_pass(userchan, username, server_host)
            print 'asked for pass: ', user_pass
            password = user_pass

        spinner.start()

        app.connect(
            hostname=server_host, port=server_port,
            username=username, password=password, timeout=10,
            allow_agent=False, look_for_keys=False)
    except Exception as e:
        logger.exception(str(server_account))
        spinner.stop("error!")
        logger.error('Failed to connect to %s: %s' %  (server_host, str(e)))
        send_message(userchan, 'Failed to connect to %s: %s'%(
            server_account, e))
        time.sleep(3)
        cleanup(userchan, app)
        return 1

    spinner.stop("... And We Are Connected.")
    appchan = None
    app.get_transport().set_keepalive(60)

    if userchan.requested_action == 'sftp':
        appchan = app.get_transport().open_session()
        appchan.invoke_subsystem('sftp')

    elif userchan.requested_action == 'interactive':
        appchan = app.invoke_shell(userchan.term,
                                   userchan.width,
                                   userchan.height)
        userchan.paired_interactive_session = appchan
        remote_username = sshgw.remote_credentials[0]
        session_logger = InteractiveLogger(sshgw, remote_host,
                                           server_account)

    elif userchan.requested_action == 'execute':
        appchan = app.get_transport().open_session()
        appchan.exec_command(userchan.user_command)
        remote_username = sshgw.remote_credentials[0]
        if 'scp' in userchan.user_command:
            session_logger = SSHExecuteSCPLogger(remote_username, remote_host,
                                                 username, server_host,
                                                 userchan.user_command)
        else:
            session_logger = InteractiveLogger(sshgw, remote_host,
                                               server_account,
                                               userchan.user_command)
    else:
        action = userchan.requested_action
        logger.warn(
            'Unknown or unset action for userchannel: %s, aborting'%action)
        cleanup(userchan, app)
        return 1

    copy_bidirectional_blocking(userchan, appchan, session_logger,
                                server_account.apply_acl)
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
