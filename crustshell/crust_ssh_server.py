import os
import sys
import traceback
import socket
import paramiko
import threading
import time
import pwd
import Crypto.Random
import logging
import logging.handlers
from optparse import OptionParser
from lib.ipaddr import IPNetwork, IPAddress


class IgnoreHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return True

class ChannelClosedException(Exception):
    pass

class TerminalThrobber(threading.Thread):
    """
    Throbber to keep remote user entertained when connecting
    him/her to server.
    """
    def __init__(self, channel, host):
        threading.Thread.__init__(self)
        self.channel = channel
        self.throb = True
        self.daemon = True
        self.message = ""
        self.host = host

    def run(self):
        # We only do throbbing for interactive sessions
        if self.channel.requested_action != 'interactive':
            return

        self.channel.send("\r\nConnecting to %s ...  "%self.host)
        throbber = ['|', '/', '-', '\\']
        count = 0
        while self.throb:
            self.channel.send("\b" + throbber[count % len(throbber)])
            time.sleep(0.5)
            count += 1
        self.channel.send("\b%s\r\n\r\n" % self.message)

    def stop(self, message):
        self.message = message
        self.throb = False
        self.join()


class CrustSSHGateway(paramiko.ServerInterface):
    """
    This is the actual handler of incoming SSH connections.
    All cabilities regarding Remote-User and Crust is here.
    """

    def __init__(self, remote_addr):
        # Event to synchronise with throbber
        self.event = threading.Event()

        #Credentials we have receive from user
        self.remote_user_credentials = None
        self.remote_add = IPAddress(remote_addr)

        # Crust.RemoteUser instance
        self.remote_user = None

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            logger.debug('Handled a channel request, allowed a session')
            return paramiko.OPEN_SUCCEEDED
        logger.debug('Handled a channel request, denied: ' + kind)
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED


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

    parser.add_option(
        '-l', '--listen-address', action='store',
        dest='bind-address', default='0.0.0.0',
        help="Bind to this interface [default: %default]")
    parser.add_option(
        '-p', '--port', action='store', type=int,
        dest='listen-port', default=2200,
        help="Listen on this port [default: %default]")
    parser.add_option(
        '--host-rsa-key', action='store', dest='host-rsa-key',
        default='/etc/hs/sshgateway/ssh_host_rsa_key',
        help="Use this file as RSA host key [default: %default]")
    parser.add_option(
        '--host-dsa-key', action='store', dest='host-dsa-key',
        default='/etc/hs/sshgateway/ssh_host_dsa_key',
        help="Use this file as DSA host key [default: %default]")
    parser.add_option(
        '--log-target', action='store', dest='log-target', default='syslog',
        help="Send log output to this target. Can be either 'syslog', 'stdout' or a path to a file. [default: %default]")
    parser.add_option(
        '-v', '--verbose', action='store_true', dest='verbose', default=False,
        help="Log more information during the sesion. Only one -v is supported")
    parser.add_option(
        '-g', '--gateway-agent', action='store', dest='gateway-agent', default='127.0.0.1',
        help="Address or hostname for the Gateway agent. [default: %default]")
    parser.add_option(
        '-u', '--user', action='store', dest='daemon-user', default='nobody',
        help="When run as root, use this username after reading the host keys and binding to the listen-socket. [default: %default]")

    if print_help:
        parser.print_help()
        return

    (options, args) = parser.parse_args()

    return options.__dict__

def run_crust_server():
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

if __name__ == '__main__':
    run_crust_server();
