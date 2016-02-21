import os
import struct
import select
import paramiko
import telnetlib
import logging
import logging.handlers
import time
import datetime
import re
import redis
import threading
import simplejson as json
from db_utils import start_new_cli_sessions, save_cli_session_event
from db_utils import close_cli_session
from db_utils import RemoteUserACL
from db_utils import RemoteConnection
from db_utils import close_connection, close_failed_connection, update_connection_state
from db_utils import ldap_authenticate_user
from lib.ipaddr import IPNetwork, IPAddress
from lib.terminal import Terminal
from lib.terminal import css_renditions

SESSION_LOG_PATH = '/var/log/shell_box'
logger = logging.getLogger('sshgw')


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



class IgnoreHostKeyPolicy (paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return True

class ChannelClosedException(Exception):
    pass


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


def check_user_command(command_buff, apply_acl):
    print '*******************************************************************************'
    command = command_buff.strip()
    print command
    print apply_acl.id
    print apply_acl.command_group
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
            #client.shutdown(1)
            channel_closed = True

def send_message(channel, message):
    if channel.requested_action == 'interactive':
        channel.send(message + "\r\n\r\n")


def cleanup(userchan, app):
    if userchan:
        usertransport = userchan.get_transport()
        logger.info('User %s disconnected' % (usertransport.get_username()))
        # We explicitly need to close the user's channel before the transport
        # to provide a nice shutdown for the client, otherwise ssh(1) get's confused
        userchan.close()
        time.sleep(0.5)
        usertransport.close()

    if app:
        app.close()


def handle_telnet_connection(server_account, sshgw, remote_host, userchan, remote_connection):
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

    spinner = TerminalThrobber(
        userchan,
        '%s@%s'%(server_account, server_account.server))
    spinner.start()
    update_connection_state(remote_connection, 'connecting')

    tc = telnetlib.Telnet(host=server_host, port=server_port)
    tc.set_option_negotiation_callback(process_telnet_option)

    def handle_auth():
        print 'handle_auth ...'
        index, match_obj, text = tc.expect(
            ['[U|u]sername: ', '[L|l]ogin:', '[L|l]oginname', '[P|p]assword'])
        print index, text
        if index == 3: #asking for password
            pass_word = '%s\n'%password
            tc.write(pass_word.encode('ascii'))
            return 'done'

        else: #asking for username
            user_name = '%s\n'%username.strip()
            tc.write(user_name.encode('ascii'))
            return 'continue'

    def handle_shell():
    	print 'handle_shell ...'
        index, match_obj, text = tc.expect(
            ['%', '$', '#', '[I|i]ncorrect', '[E|e]rror'])
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
                cleanup(None, tc.get_socket())
                return 1
        elif status == 'continue':
            continue

        else:
            send_message(userchan, 'Failed to connect to %s: %s'%(
                server_account, 'Auth Failed'))
            cleanup(None, tc.get_socket())
            return 1

    spinner.stop("... Connected.")
    update_connection_state(remote_connection, 'session')
    ### We have access to shell
    session_logger = InteractiveLogger(
        sshgw, remote_host, server_account, None)
    class TelnetSession:
        def __init__(self, tc):
            self.tc = tc
            self.active = True

        def resize_pty(self, w, h):
            naws_command = struct.pack(
                '!BBBHHBB',
                255, 250, 31, # IAC SB NAWS
                w, h,
                255, 240) # IAC SE
            self.tc.get_socket().send(naws_command)

    userchan.paired_interactive_session = TelnetSession(tc)
    if sshgw.tty_size:
        userchan.paired_interactive_session.resize_pty(*sshgw.tty_size)

    copy_bidirectional_blocking_telnet(
        userchan, tc, session_logger, server_account.apply_acl)
    session_logger.finish_up()
    send_message(userchan, 'Terminating session ...')
    #userchan.send_exit_status(0)
    cleanup(None, tc.get_socket())
    return 0

def process_telnet_option(tsocket, command, option):
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


def handle_ssh_connection(server_account, sshgw, remote_host, userchan, remote_connection):
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
            password = user_pass

        spinner = TerminalThrobber(
            userchan, '%s@%s'%(server_account, server_account.server))
        spinner.start()
        update_connection_state(remote_connection, 'connecting')
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
        cleanup(None, app)
        return 1

    spinner.stop("... Connected.")
    update_connection_state(remote_connection, 'session')
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
    #userchan.send_exit_status(rc)
    cleanup(None, app)
    return 0

def handle_connection(server_account, sshgw, remote_host, userchan, remote_connection):
    if server_account.protocol == 'ssh':
        return handle_ssh_connection(server_account, sshgw, remote_host,
                                     userchan, remote_connection)
    else:
        return handle_telnet_connection(server_account, sshgw, remote_host,
                                        userchan, remote_connection)
