import time
import types
import curses
import traceback

from curses import panel
from utils import log, gpu
from viewcontroller.base_viewcontroller import AbstractBaseViewController

"""
    Implements base_viewcontroller Class
    GUI creation based on curses framework

"""

__authors__ = "Md Rezaur Rahman, Ilja Manakov, Markus Rohm"
__copyright__ = "Copyright 2019, The DopQ Project"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Reza, Ilia, Markus"
__status__ = "Dev"

LOG = log.get_module_log(__name__)


class ParentWindow(AbstractBaseViewController):
    def __init__(self, screen, offset=0, indent=0, header=None):
        """
        Window wraps a curses window object to simplify and streamline navigating, formatting and writing in it
        :param screen: curses window object
        :param offset: number of blank lines to keep at the top of the window
        :param indent: number of whitespaces to keep at the left side of every line
        :param header: title that will be printed at the top of the window
        """

        self.screen = screen
        self.offset = offset
        self.left_indent = indent
        self.header = header[0] if header is not None else ''
        self.header_attr = header[1] if header is not None else 0

        # define constants
        self.OFFSET = offset
        self.INDENT = indent

        # define some attributes
        self.BOLD = curses.A_BOLD
        self.CYAN = curses.color_pair(2)
        self.YELLOW = curses.color_pair(3)
        self.GREEN = curses.color_pair(4)
        self.RED = curses.color_pair(5)
        self.BLUE = curses.color_pair(6)


    @property
    def size(self):
        """
        wrapper for getting window height and width
        :return: tuple(height, width)
        """
        return self.screen.getmaxyx()

    @property
    def current_cursor(self):
        """
        wrapper for getting current cursor position
        :return: tuple(y, x)
        """
        return self.screen.getyx()

    def navigate(self, y=None, x=None):
        """
        move cursors to specified position, the unspecified coordinate will remain unchanged
        :param y: y coordinate to navigate to, will remain unchanged if None is given
        :param x: x coordinate to navigate to, will remain unchanged if None is given
        :return: tuple(new y, new x)
        """
        current_y, current_x = self.current_cursor
        new_y = y if y is not None else current_y
        new_x = x if x is not None else current_x
        self.screen.move(new_y, new_x)

        return new_y, new_x

    def nextline(self, newline=1):
        """
        move cursor down one or more lines and start at indent position
        :param newline: number of lines to move down
        :return: new coordinates (y, x)
        """
        y, _ = self.current_cursor
        new_x = self.left_indent
        new_y = y + newline

        return self.navigate(new_y, new_x)

    def add_string(self, string, attrs=0, newline=0, indent=None, center=False, y=None, x=None):
        """
        write a string to the window
        :param string: string to write
        :param attrs: formatting of the string
        :param newline: number of lines to move down after writing
        :param indent: indent to use for this string
        :param center: if True string will be centered in the window
        :return: cursor coordinates after writing the string but before going to newline
        """

        # navigate to coordinates
        if any([coord is not None for coord in (y, x)]):
            self.navigate(y=y, x=x)

        LOG.info('\n<rrr> Current window size in ParentWindow.add_string(): {}'.format(self.size))
        x = (self.size[1] - len(string)) // 2 if center else indent
        self.navigate(x=x)
        current_y, current_x = self.current_cursor
        coordinates = {'beginning': {'y': y, 'x': x}}
        self.screen.addstr(string, attrs)  # System call, write string in the curses window

        y, x = self.current_cursor
        coordinates['end'] = {'y': y, 'x': x}

        if newline:
            self.nextline(newline=newline)

        return coordinates

    def add_line(self, string_list, newline=0, center=False, y=None, x=None):
        """
        allows writing a list of strings, each with their own formatting, onto a line in the window
        :param string_list: list of strings and / or (string, formatting) tuples
        :param newline: number of lines to move down after writing
        :param center: if True, line will be centered on the window
        :return: list of cursor coordinates after writing the strings but before going to newline
        """
        # initialize coordinates for return
        coords = []

        # navigate to coordinates
        if any([coord is not None for coord in (y, x)]):
            self.navigate(y=y, x=x)

        # protection against generators
        if iter(string_list) is iter(string_list):
            raise TypeError('Window.addline expects an iterable, not a generator!')

        # get length of aggregated string if center flag is set
        if center:
            total_length = 0
            for string in string_list:

                # account for possibility of string attributes
                if isinstance(string, tuple):
                    total_length += len(string[0])
                else:
                    total_length += len(string)
            center = (self.size[1] - total_length) // 2
            self.navigate(x=center)

        # print the strings in string list sequentially
        for string in string_list:

            # check if string has attributes
            if isinstance(string, tuple):
                attr = string[1]
                string = string[0]
            else:
                attr = 0

            coords.append(self.add_string(string, attr))

        if newline:
            self.nextline(newline=newline)

        return coords

    def add_multiline(self, string_multiline, newline=1, center=False, y=None, x=None):
        """
        allow writing of several lines onto the screen
        :param string_multiline: matrix of strings and / or (string, formatting) tuples
        :param newline: number of lines to move down after writing
        :param center: if True, each line will be centered on the window
        :return: None
        """

        # initialize coordinate matrix for return
        coords = []

        # navigate to coordinates
        if any([coord is not None for coord in (y, x)]):
            self.navigate(y=y, x=x)

        # protection against generators
        if iter(string_multiline) is iter(string_multiline):
            raise TypeError('Window.addline expects an iterable, not a generator!')

        for line in string_multiline:
            coords.append(self.add_line(string_list=line, newline=newline, center=center))

        return coords

    def refresh(self):
        """
        wrapper for refresh method of the curses window object
        :return: None
        """
        self.screen.refresh()

    def erase(self):
        """
        wrapper for erase method of the curses window object
        :return: None
        """
        self.screen.erase()

    def getch(self):
        """
        wrapper for getch (get character) method of the curses window object
        :return: None
        """
        return self.screen.getch()

    def print_header(self):
        """
        print the window header bold and centered at the top of the window. stored header formatting is also applied
        :return: None
        """

        self.add_string(self.header, self.BOLD | self.header_attr, center=True, y=0, x=0)
        self.navigate(self.offset, self.indent)


class SubWindow(ParentWindow):

    def __init__(self, parent, height, width, y, x, header, offset=None, indent=None, func=None, pad = False, pad_height_factor=0, **kwargs):
        """
        this class represents a subwindow embedded in the parent window and is meant to be used for displaying task specific information
        :param parent: instance of Window in which this object will be embedded
        :param height: height of the subwindow
        :param width: width of the subwindow
        :param y: y coordinate of the top left corner
        :param x: x coordinate of the top left corner
        :param header: header string of subwindow. Subwindow uses the header formatting of the parent
        :param offset: number of blank lines to keep at the top of the window
        :param indent: number of whitespaces to keep at the left side of every line
        :param func: DisplayFunction that is executed when this object is called
        """

        self.parent = parent
        offset = offset if offset is not None else parent.offset
        indent = indent if indent is not None else parent.indent
        screen = self.parent.screen.subwin(height, width, y, x)
        super(SubWindow, self).__init__(screen, offset, indent)
        self.pos_x = x
        self.pos_y = y
        self.height = height
        self.width = width
        self.header = header
        self.header_attr = parent.header_attr
        if isinstance(func, type):
            self.func = func(self, self.parent.dopq, **kwargs)
            self.args = []
        elif isinstance(func, types.FunctionType):
            self.func = func
            self.args = [self.screen, self.parent.dopq, ]
        else:
            time.sleep(15)
            self.func = DisplayFunction(self, self.parent.dopq)
            self.args = []

        #self.redraw()

        if pad == True:
            #####################################
            # Padding specific variables update #
            #####################################

            # initialize regular Subwindow
            self.pad_initialized = False
            self.pad_indent = 1 if indent is None else indent
            self.pad_offset = 1 if offset is None else offset

            # add a scrollable pad with same width and pad_height_factor * height
            self.pad_height = self.height * pad_height_factor
            pad = curses.newpad(self.pad_height, self.width)

            # define variables with regard to refreshing the pad
            self.pad_line = 0
            self.top_left = [self.pos_y + 1 + self.pad_offset, self.pos_x + 1 + self.pad_indent]
            self.bottom_right = [self.pos_y + self.height - 2, self.pos_x + self.width - 1 - self.pad_indent]
            self.pad_display_coordinates = self.top_left + self.bottom_right
            self.scroll_limit = self.pad_height - self.height + 1

            # substitute self.screen with pad, move self.screen to self.window
            self.window = self.screen
            self.screen = pad
            if self.args:
                self.args[0] = pad
            self.pad_initialized = True


            # move subwindow underneath pad (panel has to be stored, otherwise it is garbage collected)
            self.panel = panel.new_panel(self.window)
            self.panel.bottom()

            # adjust indent and offset due to pad
            self.indent -= 1 if self.indent > 0 else 0
            self.offset -= 1 if self.offset > 0 else 0

            #####################################
            ###   End of padding updatation   ###
            #####################################


        else:
            #redraws the window borders and header, without pad
            self.erase()
            self.screen.box()
            self.print_header()

    def refresh(self):
        if self.pad_initialized:
            self.window.refresh()
            self.screen.refresh(self.pad_line, 0, *self.pad_display_coordinates)
        else:
            self.screen.refresh()

    def redraw(self):
        self.erase()
        if self.pad_initialized:
            self.window.box()
        else:
            self.screen.box()
        self.print_header()
        LOG.info('\n<rrr> Type of self.func is : {}'.format(type(self.func)))
        LOG.info('\n<rrr> Type of DisplayFunction is : {}'.format(type(DisplayFunction)))

        if isinstance(self.func, DisplayFunction) or issubclass(self.func, DisplayFunction):
            self.func.first_call = True


    def __call__(self, **kwargs):
        """
        execute self.func when this object is called
        :param args: positional arguments passed to self.func
        :param kwargs: keyword arguments passed to self.func
        :return: returnvalue of self.sunc
        """

        return self.func(*self.args, **kwargs)

    def print_header(self):
        if self.pad_initialized:
            pad = self.screen
            self.screen = self.window
        super(SubWindowAndPad, self).print_header()
        if self.pad_initialized:
            self.screen = pad

    def scroll_up(self):
        self.pad_line -= 1 if self.pad_line > 0 else 0

    def scroll_down(self):
        self.pad_line += 1 if self.pad_line < self.scroll_limit else 0

    def set_focus(self):
        border_chars = ['|'] * 2 + ['-'] * 2
        self.window.attron(self.BOLD | self.CYAN)
        self.window.border(*border_chars)
        self.window.attroff(self.BOLD | self.CYAN)
        self.print_header()


    '''def redraw(self):
        """
        redraws the window borders and header
        :return: None
        """
        self.erase()
        self.screen.box()
        self.print_header()'''


class DisplayFunction(object):

    def __init__(self, subwindow, dopq):
        """
        class for stateful display functions
        :param subwindow: instance of Subwindow, passed automatically in Interface.split_screen()
        :param dopq: Instance of DopQ
        """
        self.displayed_information = None
        self.template = None
        self.first_call = True
        self.rewrite_all = False
        self.screen = subwindow
        self.dopq = dopq
        self.template = ''
        self.fields = {}

    def __call__(self, *args, **kwargs):
        """
        write template to screen if its the first time calling this class, then update the information in the template
        :param args: not used
        :param kwargs: not used
        :return: None
        """

        if self.first_call:
            self.reset_displayed_information()
            self.write_template()
            self.update()
        else:
            self.update()

    def update(self):
        """
        update displayed information
        :return: None
        """
        raise NotImplementedError('abstract method')

    def write_template(self):
        """
        write template to display on first function call
        :return: None
        """
        raise NotImplementedError('abstract method')

    def update_field(self, string, field, attrs=0):
        """
        fill the field with whitespaces before writing the string
        :param string: string to write to the field
        :param field: field as given in self.fields.values()
        :param attrs: formatting for the string. defaults to 0 (no formatting)
        :return: None
        """
        (y, x), length = field
        self.screen.navigate(y, x)
        self.screen.addstr(' ' * length)
        self.screen.navigate(y, x)
        self.screen.addstr(str(string), attrs)

    def calculate_field_properties(self, fields):
        """
        calculates the length of each field and appends this length to the coordinates already stored in the fields dict
        :return: None
        """
        width = self.screen.size[1] - self.screen.indent

        # cycle items in the ordered dict to calculate lengths
        item_list = list(fields.items())
        for index, (field, coordinates) in enumerate(item_list[:-1]):

            # get the next field name and its coordinates
            next_field, next_coordinates = item_list[index + 1]

            start = coordinates['end']['x']

            # find the end by checking where the next field begins
            if next_coordinates['beginning']['y'] != coordinates['beginning']['y']:
                # next field is in a different line, use window width as endpoint
                end = width - self.screen.indent
            else:
                # next field is in the same line
                end = next_coordinates['beginning']['x']

            length = end - start

            fields[field] = ((coordinates['end']['y'], coordinates['end']['x']), length)

        else:
            # account for the last field
            field, coordinates = item_list[-1]
            fields[field] = ((coordinates['end']['y'], coordinates['end']['x']), width - coordinates['end']['x'])

        return fields

    def reset_displayed_information(self):

        for index, info in enumerate(self.displayed_information):
            if isinstance(info, str):
                self.displayed_information[info] = ''
            else:
                for field in list(info.keys()):
                    self.displayed_information[index][field] = ''


