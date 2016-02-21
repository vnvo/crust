import re
import datetime
from collections import OrderedDict
from urwidtrees.decoration import ArrowTree  # for Decoration
from urwidtrees.widgets import TreeBox
from urwidtrees.tree import SimpleTree
from clients.ssh_client import SecureShellClient
import urwid
from urwid.raw_display import Screen
from db_utils import get_acls_by_remote_user
from db_utils import get_server_groups_for_user
from db_utils import get_servers_by_group
from db_utils import get_server_accounts_by_server
from db_utils import close_connection, close_failed_connection, update_connection_state
import pprint
import traceback
from client import send_message, cleanup
from client import handle_connection
import time

class FocusableText(urwid.WidgetWrap):
    """Selectable Text and meta data to hold server info"""
    def __init__(self, txt, metadata=None):
        self.metadata = metadata
        self.text = txt
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def __repr__(self):
        return '%s: %s'%(self.text, self.metadata)

def unhandled_input(k):
    #exit on q
    if k in ['q', 'Q']: raise urwid.ExitMainLoop()

def padding_right(text, pad_len):
    while len(text) < pad_len+2:
        text += ' '
    return text

def create_server_tree_old(user_obj):
    allowed_acl = get_acls_by_remote_user(user_obj)
    Text = FocusableText
    tree = (Text('Crust Shell'), [])

    acl_nodes = []
    i = 0
    ordered_acls = OrderedDict(allowed_acl)
    acl_count = len(ordered_acls)
    for server_account_repr, server_account_obj in ordered_acls.iteritems():
        i += 1
        acl_nodes.append(
            (
                Text('%s%s'%(padding_right(str(i), acl_count),
                             server_account_repr), #representation
                     server_account_obj), #metadata
                None)
        )

    #acl_nodes.sort(key=lambda item:item[0].text.split('@')[-1])

    acl_group = (Text('%s Access List'%user_obj.username), acl_nodes)
    tree[1].append(acl_group)
    return tree

def create_server_group_tree(user_obj):
    user_servergroups = get_server_groups_for_user(user_obj)
    data_count = len(user_servergroups)
    Text = FocusableText
    tree = (Text('Crust Shell'), [])
    sg_nodes = []
    index_map = []
    i = 0
    for sg in user_servergroups:
        i += 1
        index = padding_right(str(i), len(str(data_count)))
        sg_nodes.append( (Text('%s%s'%(index, sg), sg), None) )
        index_map.append('%s'%sg)

    node_group = (Text('Server Groups'), sg_nodes)
    print 'server-group-tree: '
    pprint.pprint( node_group )
    tree[1].append(node_group)
    return tree, index_map

def create_server_tree(user_obj, server_group):
    print 'create server tree'
    user_servers = get_servers_by_group(user_obj, server_group)
    data_count = len(user_servers)
    Text = FocusableText
    tree = (Text('Crust Shell'), [])
    s_nodes = []
    index_map = []
    i = 0
    for s in user_servers:
        i += 1
        s_nodes.append(
            (Text('%s%s'%(padding_right(str(i), len(str(data_count))), s), s), None) )
        index_map.append('%s'%s)

    node_group = (Text('Servers'), s_nodes)
    print 'server-tree: '
    pprint.pprint( node_group )
    tree[1].append(node_group)
    return tree, index_map

def create_server_account_tree(user_obj, server):
    print 'create server account tree'
    user_accounts = get_server_accounts_by_server(user_obj, server)
    data_count = len(user_accounts)
    Text = FocusableText
    tree = (Text('Crust Shell'), [])
    sa_nodes = []
    index_map = []
    i = 0
    for sa in user_accounts:
        i += 1
        sa_nodes.append(
            (Text('%s%s'%(padding_right(str(i), len(str(data_count))), sa), sa), None) )
        index_map.append('%s'%sa.username)

    node_group = (Text('Server Accounts'), sa_nodes)
    print 'server-account-tree'
    pprint.pprint(node_group)
    tree[1].append(node_group)
    return tree, index_map

class ShellScreen(Screen):
    def get_available_raw_input(self):
        return map(ord, self._term_input_file.recv(1024))

    def write(self, data):
        self._term_output_file.send(data)

    def flush(self):
        try:
            self._term_output_file.flush()
        except:
            pass

    def get_cols_rows(self):
        return self._term_input_file.width, self._term_input_file.height

class ShellBoxMenu(object):
    def __init__(self, upstream_chan, sshgw, remote_host, remote_connection, logger):
        self.upstream_chan = upstream_chan
        self.sshgw = sshgw
        self.user_obj = sshgw.user
        self.remote_host = remote_host
        self.remote_connection = remote_connection
        self.logger = logger

        self.palette = [
            ('body', 'black', 'light gray'),
            ('focus', 'light green', 'dark blue', 'standout'),
            ('head', 'yellow', 'dark gray', 'standout'),
            ('foot', 'light gray', 'dark gray'),
            ('key', 'light green', 'dark gray', 'underline'),
            ('title', 'white', 'black', 'bold'),
            ('error', 'dark red', 'black'),
            ('footer_msg', 'yellow', 'dark gray')
        ]
        self.footer_text = [
            ('footer_msg', 'Move:'), ' ',
            ('key', 'Up'), '/', ('key', 'Down'), '   ',
            ('footer_msg', 'Select:'), ' ',
            ('key', 'enter'), '   ', #('key', 'double-click'), ' ',
            ('footer_msg', 'Quit:'), ' ', ('key', 'Ctrl+q'), '        ',
            ('footer_msg', 'Powered By: Crust-Shell v1.0.7')
        ]

        self.quit = False
        self.selected_server_group = None
        self.selected_server = None
        self.selected = None
        self.current_level = 'server-group'
        self.index_map = []
        #####
        new_tree, self.index_map = self._create_level_tree()
        self.root_node = new_tree
        stree = SimpleTree([self.root_node])
        atree = ArrowTree(stree)
        self.treebox = TreeBox(atree)
        self.rootwidget = urwid.AttrMap(self.treebox, 'body')
        ####
        self.ui = None
        self.size = None
        self.header_text = '%s@%s Access List'%(
            self.user_obj.username, self.remote_host
        )
        self.header = urwid.AttrWrap(urwid.Text(self.header_text), 'head')
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text), 'foot')
        self.view = urwid.Frame(self.rootwidget,
                                header=urwid.AttrWrap(self.header, 'head'),
                                footer=self.footer)
        self.logger.info('Shell Menu, ready to serve "%s@%s" ...'%(
            self.user_obj, self.remote_host))

    def _setup_tree(self):
        print '================== Setup Tree ========================='
        new_tree, self.index_map = self._create_level_tree()
        self.root_node = new_tree
        stree = SimpleTree([self.root_node])
        atree = ArrowTree(stree)
        self.treebox = TreeBox(atree)
        self.logger.info('after tree setup ... %s'%str(self.root_node))
        self.rootwidget = urwid.AttrMap(self.treebox, 'body')
        self.view.set_body(self.rootwidget)
        self.view.render(size=self.size)
        self.treebox.refresh()
        self.treebox.focus_parent()
        print 'after treebox refresh'
        print '================ End Setup Tree ======================'

    def _create_level_tree(self):
        self.logger.info('create level tree: %s'%self.current_level)
        if self.current_level == 'server-group':
            self.logger.info('level server-group: %s'%self.user_obj)
            return create_server_group_tree(self.user_obj)
        elif self.current_level == 'server':
            self.logger.info('level server: %s - %s '%(self.user_obj, self.selected_server_group))
            return create_server_tree(self.user_obj, self.selected_server_group)
        else:
            self.logger.info('level server-account: %s - %s'%(self.user_obj, self.selected_server))
            return create_server_account_tree(self.user_obj, self.selected_server)

    def main(self):
        try:
            while not self.quit:
                if self.upstream_chan:
                    self.ui = ShellScreen(input=self.upstream_chan,
                                          output=self.upstream_chan)
                else:
                    self.ui = urwid.raw_display.Screen()

                self.ui.register_palette(self.palette)
                self.ui.run_wrapper(self.run)

            return self.selected
        except Exception as e:
            print e
            self.logger.exception('Shell Box Menu, main:')
            return None

        self.logger.info('Main loop exiting.')

    def run(self):
        try:
            self.ui.tty_signal_keys('undefined', 'undefined', 'undefined',
                                    'undefined', 'undefined')
            self.size = self.ui.get_cols_rows()
            self.logger.info('Shell Menu, run size=%s'%str(self.size))
            while True:
                print '============ In Loop ==========='
                pprint.pprint(self.root_node)
                try:
                    current_focus = self.treebox.get_focus()
                except Exception as e:
                    print 'error ------>  %s'%e
                    self.logger.info(traceback.format_exc())
                    break #continue

                self.logger.info('%s'%str(current_focus))
                self.logger.info(current_focus[0].get_focus().text)
                header_focus_name = ''
                try:
                    selected_sa = current_focus[0].get_focus().metadata
                    header_focus_name = str(selected_sa)#.get_server_account_repr
                except:
                    header_focus_name = 'N/A'

                self.logger.info('Shell Menu, focus: %s'%header_focus_name)
                self.header_text = [
                    ('footer_msg',
                     '%s      Remote User: %s@%s'%(
                         datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                         self.user_obj.username,
                         self.remote_host)
                    ),
                    ' ', ('footer_msg', '--> '), ' ',
                    ('key', str(header_focus_name))
                ]

                self.header.set_text(self.header_text)
                self.logger.info('header is updated')
                self.logger.info('channel: %s'%self.upstream_chan.closed)
                self.logger.info('size: %s'%str(self.size))
                canvas = self.view.render(self.size, focus=1)
                self.logger.info('canvas is updated')
                self.ui.draw_screen(self.size, canvas)
                self.logger.info('redraw screen')
                keys = None
                while not keys:
                    keys = self.ui.get_input()

                for k in keys:
                    self.view.keypress(self.size, k)
                    if k in ['ctrl q', 'ctrl Q']:
                        self.logger.info('user pressed Ctrl+Q')
                        self.quit = True
                        self.stop_ui()
                        return

                    if k == 'enter':
                        selected = current_focus[0].get_focus().metadata
                        if selected:
                            if self.current_level == 'server-account':
                                self.stop_ui()
                                self.selected = selected
                                self.sshgw.ignore_resize = False
                                update_connection_state(self.remote_connection, 'session')
                                handle_connection(
                                    self.selected, self.sshgw, self.remote_host,
                                    self.upstream_chan, self.remote_connection)
                                self.sshgw.ignore_resize = True
                                update_connection_state(self.remote_connection, 'select server')
                                self.start_ui()

                            elif self.current_level == 'server-group':
                                self.current_level = 'server'
                                self.selected_server_group = selected
                                self._setup_tree()

                            elif self.current_level == 'server':
                                self.current_level = 'server-account'
                                self.selected_server = selected
                                self._setup_tree()
                        else:
                            label = current_focus[0].get_focus().text
                            if label == 'Servers':
                                self.current_level = 'server-group'
                                self.selected_server_group = None
                                self.selected_server = None
                            elif label == 'Server Accounts':
                                self.current_level = 'server'
                                self.selected_server = None
                            self._setup_tree()

                    elif re.match('[a-zA-Z]', k) : #seek and set focus
                        for index, item in enumerate(self.index_map):
                            if item.lower().startswith(k.lower()):
                                print 'setting focus on ', k, index
                                self.treebox.set_focus((0,0,index))
                                self.view.render(size=self.size)
                                break
        except Exception as e:
            print e
            self.logger.exception('Shell Menu, run:')

    def start_ui(self):
        self.ui.start()
        self.ui.set_mouse_tracking()
        self.ui.tty_signal_keys('undefined', 'undefined', 'undefined',
                                'undefined', 'undefined')
        self.size = self.ui.get_cols_rows()

    def stop_ui(self):
        self.ui.stop()
