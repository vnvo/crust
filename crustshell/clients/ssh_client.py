# -*- coding: utf-8 -*-
import paramiko
import termios
import tty
import os
import select
import socket
import sys
from datetime import datetime



class SecureShellClient(object):
    """
    This class implements basic SSH v2 client with logging capabilities
    """
    def __init__(self, user_session, server_info, size, upstream_chan):
        #server_info = server_info[0]
        print server_info
        self.user_session = user_session
        self.server_data = server_info
        self.host = server_info['ip']
        self.port = server_info['port']
        self.account = server_info['user_account']
        self.size = size
        self.session_start_date = datetime.now()
        self.session_stop_date = None
        self.closed = False
        self.upstream_chan = upstream_chan

        paramiko.util.logging.getLogger().setLevel(30)

    def _prepare_transport(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            self.sock.connect((self.host, self.port))
        except Exception as e:
            except_msg = "E Connect failed: %s to %s"%(
                str(e), self.server_data['name'])
            raise Exception(except_msg)

        #Create the transport
        self.transport = paramiko.Transport(self.sock)
        self.transport.start_client()

        #Handle authentication
        if self.account['account_type'] == "userpass":
            try:
                self.transport.auth_password(
                    self.account['username'],
                    self.account['password'])
            except paramiko.SSHException as e:
                self.transport.close()
                self.sock.close()
                raise Exception(e)

        elif self.account['account_type'] == "userpkey":
            pkey = paramiko.PKey.from_private_key_file(
                self.account['pkey'],
                self.account['key_password'])
            try:
                self.transport.auth_publickey(
                    self.account['username'],
                    pkey)
            except paramiko.SSHException as e:
                self.transport.close()
                self.sock.close()
                raise Exception(e)

        else:
            raise Exception(
                'Auth Type %s not supported'%self.account['account_type'])

    def _prepare_channel(self):
        self.chan = self.transport.open_session()
        cols, rows = self.size
        self.chan.get_pty('xterm', cols, rows)
        self.chan.invoke_shell()

    def start(self):
        self._prepare_logging()
        self.to_log("session started ...\n")
        self._prepare_transport()
        self.to_log("transport is ready.\n")
        self._prepare_channel()
        self.to_log("channel is ready.\n")

        try:
            self.to_log("setup interactive shell ...\n")
            self._intractive_shell()
        except paramiko.SSHException as e:
            except_msg = 'SSH Negotiation Failed to %s'
            self.transport.close()
            self.sock.close()
            raise Exception(except_msg)
        finally:
            self.to_log("end session.\n")
            self._end_logging()

    def _prepare_logging(self):
        log_filename = '/tmp/test.log'
        self.log_buffer = ""
        self.log_file = open(log_filename, 'w+')

    def _end_logging(self):
        self.to_log("\n")
        self.log_file.flush()
        self.log_file.close()

    def to_log(self, msg):
        self.log_buffer += msg
        if not '\n' in self.log_buffer:
            return
        try:
            prep_msg = str(self.log_buffer).decode().replace('\r', '')
        except:
            prep_msg = str(self.log_buffer)

        self.log_buffer = ""

        now = str(datetime.now())
        self.log_file.write(now+": "+prep_msg+"\n")
        self.log_file.flush()
        os.fsync(self.log_file.fileno())

    def _intractive_shell(self):
        #oldtty = termios.tcgetattr(sys.stdin)
        #oldtty = termios.tcgetattr(self.upstream_chan)

        try:
            #tty.setraw(sys.stdin.fileno())
            #tty.setraw(self.upstream_chan.fileno())
            #tty.setcbreak(self.upstream_chan.fileno())
            #tty.setcbreak(sys.stdin.fileno())
            self.chan.settimeout(0.0)

            while True:
                r, w, e = select.select([self.chan, self.upstream_chan], [], [])
                if self.chan in r:
                    try:
                        data = self.chan.recv(1024)
                        if len(data) == 0:
                            break

                        self.upstream_chan.send(data)
                        #sys.stdout.write(data)
                        #sys.stdout.flush()
                        self.to_log(data)

                    except socket.timeout:
                        break

                if self.upstream_chan in r:
                    self.to_log("upstream ready to read ...\n")
                #if sys.stdin in r:
                    #data = os.read(sys.stdin.fileno(), 1)
                    data = self.upstream_chan.recv(1024)
                    #data = os.read(self.upstream_chan.fileno(), 1)
                    if len(data) == 0:
                        break
                    self.chan.send(data)
        except:
            raise
        finally:
            pass
            #termios.tcsetattr(self.upstream_chan, termios.TCSADRAIN, oldtty)
            #termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

if __name__ == '__main__':
    a_server = {"name":"my test server (local)",
              "ip":"127.0.0.1", "port":22, "id":10,
              "user_account":{"account_type":"userpass",
                              "username":"vahid",
                              "password":"vahid"}}

    c = SecureShellClient("vahid", a_server, (50, 50))
    c.start()
