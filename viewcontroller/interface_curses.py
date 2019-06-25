import copy
import time
import curses
import traceback

from utils import log, gpu


from utils import interface_funcs, display_process
from viewcontroller.curses_view_controller import Window, SubWindow, SubWindowAndPad


LOG = log.get_module_log(__name__)

KEY_TAB = 9


def start_interface(dopq):
    try:
        LOG.info('In start_interface file.')
        curses.wrapper(main, dopq)
    except:
        LOG.error(traceback.format_exc())
    finally:
        gpu.GPU.stop_hardware_monitor()


def main(screen, dopq):
    # custom definition of color pairs
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)

    screen.idcok(False)
    screen.idlok(False)

    interface = InterfaceCurses(dopq, screen, offset=4, indent=2)
    interface()


def reload_config(screen, dopq):

    # create function for updates
    def update_report_fn(msg):
        screen.erase()
        screen.addstr(msg, curses.A_BOLD)
        screen.refresh()

    # let dop-q do the reload of the configuration
    dopq.reload_config(update_report_fn)

    # wait
    time.sleep(2)


class InterfaceCurses(Window):
    def __init__(self, dopq, screen, offset, indent, v_ratio=0.25, h_ratio=0.5, interval=1):
        """
        interface to the docker priority queue object
        :param dopq_ref: instance of DopQ
        :param screen: curses window to use as display
        :param offset: number of blank lines to keep at the top of the window
        :param indent: number of whitespaces to keep at the left side of every line
        :param v_ratio: ratio of top subwindow height to total window height
        :param h_ratio: ratio of left subwindow width to total window width
        :param interval: update interval in seconds
        """

        super(InterfaceCurses, self).__init__(screen, offset, indent)
        self.header_attr = self.CYAN
        self.dopq = dopq
        self.v_ratio = v_ratio
        self.h_ratio = h_ratio
        self.functions = interface_funcs.FUNCTIONS
        self.interval = interval

        self.screen.nodelay(True)
        curses.curs_set(0)
        self.erase()

        self.subwindows = self.split_screen()

        self.scrollable = [self.subwindows['userstats'], self.subwindows['enqueued'], self.subwindows['history']]
        self.focus = -1

        # draw all borders and headers
        self.redraw()

    def __call__(self, *args, **kwargs):
        """
        infinite loop that displays information and watches for input
        :param args: not used
        :param kwargs: not used
        :return: None
        """

        while True:

            # display information in the subwindows
            self.print_information()

            # loop that catches user interactions with ~0.1 cycle time
            for _ in range(int(self.interval/0.1)):
                # get user input char
                key = self.getch()
                curses.flushinp()

                # run the specified function
                if key in list(self.functions.keys()):
                    self.execute_function(self.functions[key])

                if key == KEY_TAB:

                    # unset focus for current subwindow
                    if self.focus != -1:
                        self.scrollable[self.focus].window.box()
                        self.scrollable[self.focus].print_header()

                    # cycle subwindow focus
                    self.focus += 1 if self.focus < len(self.scrollable) - 1 else -3
                    if self.focus != -1:
                        self.scrollable[self.focus].set_focus()

                if key == ord('+') and self.focus > -1:
                    subwindow = self.scrollable[self.focus]
                    subwindow.scroll_up()

                if key == ord('#') and self.focus > -1:
                    subwindow = self.scrollable[self.focus]
                    subwindow.scroll_down()

                self.refresh()

                time.sleep(0.1)

    def subwin(self, pad=False, *args, **kwargs):
        """
        wrapper for Subwindow.__init__() with self as parent
        :param pad: if True return a SubWindowAndPad instead of SubWindow
        :param args: positional arguments passed to Subwindow()
        :param kwargs: keyword arguments passed to Subwindow()
        :return: instance of Subwindow
        """
        if pad:
            return SubWindowAndPad(parent=self, *args, **kwargs)
        else:
            return SubWindow(parent=self, *args, **kwargs)

    def split_screen(self):
        """
        setup the 5 subwindows that are needed for the interface
        :return: dict of Subwindow instances
        """

        # get size of the window adjusted for borders
        win_height, win_width = self.size
        win_height, win_width = win_height - 1.5 * self.offset, win_width - 2 * self.indent
        horizontal_gap, vertical_gap = self.indent // 2, self.offset // 6

        # calculate subwindow sizes
        sub_height_upper = int(self.v_ratio * win_height - vertical_gap // 2)
        sub_height_lower = int((1 - self.v_ratio) * win_height - vertical_gap // 2)
        sub_width_left = int(self.h_ratio * win_width - horizontal_gap // 2)
        sub_width_right = int((1 - self.h_ratio) * win_width - horizontal_gap // 2)

        # create subwindows
        subwindows = {
            'status': self.subwin(height=sub_height_upper,
                                  width=sub_width_left,
                                  y=self.offset,
                                  x=self.indent,
                                  header='~~Status~~',
                                  func=display_process.Status,
                                  indent=self.indent*4),
            'containers': self.subwin(height=sub_height_lower,
                                      width=sub_width_left,
                                      y=self.offset + sub_height_upper + vertical_gap,
                                      x=self.indent,
                                      header='~~Running Containers~~',
                                      func=display_process.Containers,
                                      offset=2),
            'userstats': self.subwin(pad=True,
                                     height=sub_height_upper,
                                     width=sub_width_right,
                                     y=self.offset,
                                     x=self.indent + sub_width_left + horizontal_gap,
                                     offset=1,
                                     indent=4,
                                     header='~~User Stats~~',
                                     func=display_process.UserStats),
            'enqueued': self.subwin(pad=True,
                                    height=sub_height_lower // 2,
                                    width=sub_width_right,
                                    y=self.offset + sub_height_upper + vertical_gap,
                                    x=self.indent + sub_width_left + horizontal_gap,
                                    offset=1,
                                    indent=4,
                                    pad_height_factor=10,
                                    header='~~Enqueued Containers~~',
                                    func=display_process.ContainerList,
                                    mode='enqueued'),
            'history': self.subwin(pad=True,
                                   height=(sub_height_lower // 2) + 1, #+ vertical_gap // 2,
                                   width=sub_width_right,
                                   y=self.offset + sub_height_upper + sub_height_lower // 2 + vertical_gap,
                                   x=self.indent + sub_width_left + horizontal_gap,
                                   offset=1,
                                   indent=4,
                                   pad_height_factor=10,
                                   header='~~History~~',
                                   func=display_process.ContainerList,
                                   mode='history')
                    }

        return subwindows

    def print_information(self):
        """
        wrapper for calling all subwindow functions
        :return:
        """

        for sub in list(self.subwindows.values()):
            sub()

    def redraw(self):
        """
        print window header and redraw all subwindows
        :return: None
        """

        self.print_header(self) # print header is a static method

        for sub in list(self.subwindows.values()):
            sub.redraw()

    def refresh(self):
        """
        call refresh on self and all subwindows
        :return: None
        """

        self.screen.refresh()
        for sub in list(self.subwindows.values()):
            sub.refresh()

    @staticmethod # static because i wanted to use this method with instances of Window as well
    def print_header(self):
        """
        customised print_header to write interface header followed by a vertical line
        static, so that it can be called for other windows as well
        :param self: Window instance
        :return: None
        """

        # draw border around the window
        border_characters = [0] * 2 + ['='] * 2 + ['#'] * 4
        self.screen.border(*border_characters)

        # print title
        string_line = [('Do', self.BOLD | self.header_attr),
                       ('cker ', self.header_attr),
                       ('P', self.BOLD | self.header_attr),
                       ('riority ', self.header_attr),
                       ('Q', self.BOLD | self.header_attr),
                       ('ueue -- ', self.header_attr),
                       ('DopQ', self.BOLD | self.header_attr)]
        self.nextline()
        self.addline(string_list=string_line, newline=1, center=True, y=1, x=0)

        self.screen.hline('~', self.size[1]-2*self.indent, self.BOLD | self.header_attr)
        self.nextline(newline=3)

        return self.yx

    def execute_function(self, func):
        """
        prepares a window in which a control function is executed. window is deleted afterwards
        :param func: control function to call
        :return: None
        """

        # make a new window for executing the function in
        height, width = self.size
        new_window = Window(curses.newwin(height, width, 0, 0), self.offset, self.indent, header=('', self.CYAN))

        # print dopq header in the new window
        new_window.navigate(*self.print_header(new_window))

        # execute function
        func(new_window, self.dopq)

        # delete the temporary window
        del new_window

        self.redraw()
        self.print_information()





