import curses
from utils import interface_funcs

class Interface():
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

        super(Interface, self).__init__(screen, offset, indent)
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
