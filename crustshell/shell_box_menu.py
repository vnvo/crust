import datetime
from collections import OrderedDict
from urwidtrees.decoration import ArrowTree  # for Decoration
from urwidtrees.widgets import TreeBox
from urwidtrees.tree import SimpleTree
from clients.ssh_client import SecureShellClient
import urwid
from urwid.raw_display import Screen
from db_utils import get_acls_by_remote_user


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

def unhandled_input(k):
    #exit on q
    if k in ['q', 'Q']: raise urwid.ExitMainLoop()

def padding_right(text, pad_len):
    while len(text) < pad_len:
        text += ' '
    return text

def create_server_tree(user_obj):
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
    def __init__(self, upstream_chan, user_obj, remote_host, logger):
        self.upstream_chan = upstream_chan
        self.user_obj = user_obj
        self.remote_host = remote_host
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
            #('footer_msg', 'Expand:'), ' ',
            #('key', 'space'), ',', ('key', 'click'), ' ',
            ('footer_msg', 'Select:'), ' ',
            ('key', 'enter'), '   ', #('key', 'double-click'), ' ',
            ('footer_msg', 'Quit:'), ' ', ('key', 'q'), '        ',
            ('footer_msg', 'Powered By: Crust v0.1')
        ]

        self.quit = False
        self.selected = None
        stree = SimpleTree([create_server_tree(self.user_obj)])
        atree = ArrowTree(stree)
        self.treebox = TreeBox(atree)
        self.rootwidget = urwid.AttrMap(self.treebox, 'body')
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
            self.logger.exception('Shell Box Menu, main:')
            return None


    def run(self):
        try:
            self.ui.tty_signal_keys('undefined', 'undefined', 'undefined',
                                    'undefined', 'undefined')
            self.size = self.ui.get_cols_rows()
            self.logger.info('Shell Menu, run size=%s'%str(self.size))
            while True:
                current_focus = self.treebox.get_focus()
                header_focus_name = ''
                try:
                    selected_sa = current_focus[0].get_focus().metadata
                    header_focus_name = selected_sa.get_server_account_repr
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
                    if k in ['q', 'Q']:
                        self.logger.info('user pressed Q')
                        self.quit = True
                        self.stop_ui()
                        return

                    if k == 'enter':
                        server_data = current_focus[0].get_focus().metadata
                        if server_data:
                            self.quit = True
                            self.stop_ui()
                            self.selected = server_data
                            return
        except:# Exception as e:
            self.logger.exception('Shell Menu, run:')
            #raise

    def start_ui(self):
        self.ui.start()
        self.ui.set_mouse_tracking()
        self.ui.tty_signal_keys('undefined', 'undefined', 'undefined',
                                'undefined', 'undefined')
        self.size = self.ui.get_cols_rows()

    def stop_ui(self):
        self.ui.stop()
