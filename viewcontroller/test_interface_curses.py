import copy
import time
import curses
import traceback

from utils import log, gpu
from math import floor, ceil
from collections import OrderedDict

from viewcontroller.curses_view_controller import Window, SubWindow, SubWindowAndPad, DisplayFunction
from utils import interface_funcs

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
    # define color pairs
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
                                  func=Status,
                                  indent=self.indent*4),
            'containers': self.subwin(height=sub_height_lower,
                                      width=sub_width_left,
                                      y=self.offset + sub_height_upper + vertical_gap,
                                      x=self.indent,
                                      header='~~Running Containers~~',
                                      func=Containers,
                                      offset=2),
            'userstats': self.subwin(pad=True,
                                     height=sub_height_upper,
                                     width=sub_width_right,
                                     y=self.offset,
                                     x=self.indent + sub_width_left + horizontal_gap,
                                     offset=1,
                                     indent=4,
                                     header='~~User Stats~~',
                                     func=UserStats),
            'enqueued': self.subwin(pad=True,
                                    height=sub_height_lower // 2,
                                    width=sub_width_right,
                                    y=self.offset + sub_height_upper + vertical_gap,
                                    x=self.indent + sub_width_left + horizontal_gap,
                                    offset=1,
                                    indent=4,
                                    pad_height_factor=10,
                                    header='~~Enqueued Containers~~',
                                    func=ContainerList,
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
                                   func=ContainerList,
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



class Status(DisplayFunction):

    def __init__(self, subwindow, dopq):
        """
        initializes template and displayed information
        :param subwindow: instance of Subwindow
        :param dopq: instance of DopQ
        """

        super(Status, self).__init__(subwindow, dopq)

        # init fields
        self.fields = {'queue status': '',
                       'queue uptime': '',
                       'queue starttime': '',
                       'provider status': '',
                       'provider uptime': '',
                       'provider starttime': ''}

        # init information dict
        self.displayed_information = copy.deepcopy(self.fields)

        # init template
        width = self.screen.size[1]
        width_unit = width // 8
        self.template = [[pad_with_spaces('queue:', width_unit)],
                           [pad_with_spaces('uptime:  ', 2*width_unit, 'prepend'),
                            pad_with_spaces('starttime:  ', 2*width_unit, 'prepend')],
                           [''],
                           [pad_with_spaces('provider:', width_unit)],
                           [pad_with_spaces('uptime:  ', 2*width_unit, 'prepend'),
                            pad_with_spaces('starttime:  ', 2*width_unit, 'prepend')],
                           ['']]

    def update(self):
        """
        gathers new information and overwrites only the portions int the template that have changed
        :return: None
        """
        # gather new information
        information = {}
        information['queue status'] = self.dopq.status
        if information['queue status'] == 'running':
            information['queue uptime'], information['queue starttime'] = self.dopq.uptime
            information['provider status'] = self.dopq.provider.status
            if information['provider status'] == 'running':
                information['provider uptime'], information['provider starttime'] = self.dopq.provider.uptime
            else:
                information['provider uptime'], information['provider starttime'] = '', ''
        else:
            information['queue uptime'], information['queue starttime'] = '', ''
            information['provider status'] = ''
            information['provider uptime'], information['provider starttime'] = '', ''

        # update displayed information
        for field, value in list(information.items()):

            # skip if information has not changed
            if value == self.displayed_information[field]:
                continue

            # overwrite information that has changed
            attrs = pick_color(value) | self.screen.BOLD if 'status' in field else 0
            self.update_field(value, self.fields[field], attrs)

        self.displayed_information = information

    def write_template(self):
        """
        writes template to display on first call
        :return:
        """

        # get the beginning and end coordinates for every string in the template
        coordinates = self.screen.addmultiline(self.template)
        fields = {'queue status': coordinates[0][0],
                  'queue uptime': coordinates[1][0],
                  'queue starttime': coordinates[1][1],
                  'provider status': coordinates[3][0],
                  'provider uptime': coordinates[4][0],
                  'provider starttime': coordinates[4][1]
                  }

        # sort the dict according to y coordinates first and x coordinates second
        def sort_fn(item):
            return item[1]['beginning']['y'], item[1]['beginning']['x']

        fields = OrderedDict(sorted(list(fields.items()), key=sort_fn))
        self.fields = self.calculate_field_properties(fields)
        self.first_call = False


class Containers(DisplayFunction):

    def __init__(self, subwindow, dopq):
        """
        initializes fields, displayed_information and form template
        :param subwindow: instance of SubWindowAndPad
        :param dopq: instance of DopQ
        """

        super(Containers, self).__init__(subwindow, dopq)

        width = self.screen.size[1]
        width_unit = width // 8

        # init fields dict
        self.fields = [{'name': '',
                        'status': '',
                        'docker name': '',
                        'executor': '',
                        'run_time': '',
                        'created': '',
                        'cpu': '',
                        'memory': '',
                        'id': '',
                        'usage': ''}]

        # init information dict
        self.displayed_information = []

        # init template
        self.template = {'base': [['name:  ', # name
                                   pad_with_spaces('status:  ', 5 * width_unit, 'prepend')],  # end of first line
                                  ['-' * (width - 2 * self.screen.indent)],  # hline
                                  [pad_with_spaces('docker name:  ', 2 * width_unit, 'prepend'),
                                   pad_with_spaces('executor:  ', 3 * width_unit, 'prepend')], # end of second line
                                  [pad_with_spaces('uptime:  ', 2 * width_unit, 'prepend'),
                                   pad_with_spaces('created:  ', 3 * width_unit, 'prepend')],  # end of third line
                                  [pad_with_spaces('cpu usage:  ', 2 * width_unit, 'prepend'),
                                   pad_with_spaces('memory usage:  ', 3 * width_unit, 'prepend')]],  # end of fourth line

                         'gpu': [pad_with_spaces('gpu minor:  ', 2 * width_unit, 'prepend'),
                                 pad_with_spaces('gpu usage:  ', 3 * width_unit, 'prepend')]}

    def update(self):
        """
        gets new information from the queue and updates the fields that have changed
        :return: None
        """

        # gather new information
        information = []
        containers = copy.copy(self.dopq.running_containers)
        for container in self.dopq.running_containers:
            information.append(container.container_stats())

            # reformat gpu info
            gpu_info = information[-1].pop('gpu', False)
            if gpu_info:
                minors, usages = [], []
                for info in gpu_info:
                    minors.append(info['id'])
                    usages.append(info['usage'])
                information[-1]['id'] = minors
                information[-1]['usage'] = ''.join([str(usage) + '% ' for usage in usages])

        # check if the containers are the same
        rewrite_all = False
        if len(information) != len(self.displayed_information):
            self.write_template(containers)
            rewrite_all = True
        else:
            for index, container in enumerate(self.dopq.running_containers):
                if container.name != self.displayed_information[index]['name']:
                    # rewrite template because gpu settings of the changed container may be different from the previously displayed
                    self.write_template()
                    rewrite_all = True
                    break

        # update displayed information
        for index, container_information in enumerate(information):
            for field, value in list(container_information.items()):

                if rewrite_all or value != self.displayed_information[index][field]:
                    attrs = 0
                    if 'status' in field:
                        attrs = pick_color(value) | self.screen.BOLD
                    elif 'name' in field:
                        attrs = self.screen.BOLD
                    try:
                        self.update_field(value, self.fields[index][field], attrs)
                    except:
                        pass
                else:
                    continue

        # update stored information
        self.displayed_information = information

    def write_template(self, containers=[]):
        """
        write the form template to the screen and get fields
        :return: None
        """
        # clear screen
        self.screen.redraw()

        # combine parts of the template according to number and gpu settings of containers
        templates, use_gpu = [], []
        for container in containers:
                if container.use_gpu:
                    template = copy.deepcopy(self.template['base'])
                    template.append(self.template['gpu'])
                    templates.append(template)
                    use_gpu += [True]
                else:
                    templates.append(self.template['base'])
                    use_gpu += [False]

        # write the template to the display and get fields
        heigth = (self.screen.size[0] - self.screen.offset) // len(templates) if templates else 0
        lines = [self.screen.offset + i*heigth for i, _ in enumerate(templates)]
        fields_list = []
        for index, (line, template) in enumerate(zip(lines, templates)):
            self.screen.navigate(y=line, x=self.screen.indent)
            coordinates = self.screen.addmultiline(template)
            fields = {'name': coordinates[0][0],
                      'status': coordinates[0][1],
                      'docker name': coordinates[2][0],
                      'executor': coordinates[2][1],
                      'run_time': coordinates[3][0],
                      'created': coordinates[3][1],
                      'cpu': coordinates[4][0],
                      'memory': coordinates[4][1]}
            if use_gpu[index]:
                fields['id'] = coordinates[5][0]
                fields['usage'] = coordinates[5][1]

            def sort_fn(item):
                return item[1]['beginning']['y'], item[1]['beginning']['x']

            # sort the fields by their y coordinate first and x coordinate second
            fields = OrderedDict(sorted(list(fields.items()), key=sort_fn))
            fields_list.append(self.calculate_field_properties(fields))

        self.fields = fields_list
        self.first_call = False


class UserStats(DisplayFunction):

    def __init__(self, subwindow, dopq):
        """
        initialize fields, displayed information and form template
        :param subwindow: instance of SubWindowAndPad
        :param dopq: instance of DopQ
        """

        super(UserStats, self).__init__(subwindow, dopq)

        width = self.screen.size[1]
        width_unit = width // 8

        # init fields dict
        self.fields = [{'user': '',
                        'containers run': '',
                        'penalty': '',
                        'containers enqueued': ''}]

        # init information dict
        self.displayed_information = copy.deepcopy(self.fields)

        # init template
        self.template = [['user:  '],
                         ['-' * (width - 2 * self.screen.pad_indent)],  # hline
                         [pad_with_spaces('penalty:  ', width_unit, 'prepend'),
                          pad_with_spaces('containers run:  ', 3 * width_unit, 'prepend'),
                          pad_with_spaces('containers enqueued:  ', 3 * width_unit, 'prepend')]]

        self.height = len(self.template) + 2

    def update(self):
        """
        obtains new information and prints the fields that changed
        :return: NOne
        """

        # get new information from queue
        user_stats = self.dopq.users_stats

        # check if length of the user list has changed, if yes, redraw everything

        if len(user_stats) != len(self.displayed_information):
            self.write_template()
            self.rewrite_all = True

        # cycle users and print their stats if they have changed or if redraw_all
        for index, user in enumerate(user_stats):
            for field, value in list(user.items()):
                if self.rewrite_all or value != self.displayed_information[index][field]:
                    attrs = self.screen.BOLD if 'user' in field else 0
                    self.update_field(value, self.fields[index][field], attrs)
                else:
                    continue

        # update displayed information
        self.displayed_information = user_stats

        self.rewrite_all = False

    def write_template(self):
        """
        write form template to the screen and get fields
        :return: None
        """

        # combine parts of the template according to number and gpu settings of containers
        templates = [self.template] * len(self.dopq.user_list)

        # write the template to the display and get fields
        lines = [self.screen.offset + i * self.height for i, _ in enumerate(templates)]  # starting line for each template
        fields_list = []
        for index, (line, template) in enumerate(zip(lines, templates)):
            self.screen.navigate(y=line, x=self.screen.indent)
            coordinates = self.screen.addmultiline(template)
            fields = {'user': coordinates[0][0],
                      'penalty': coordinates[2][0],
                      'containers run': coordinates[2][1],
                      'containers enqueued': coordinates[2][2]}

            def sort_fn(item):
                return item[1]['beginning']['y'], item[1]['beginning']['x']

            fields = OrderedDict(sorted(list(fields.items()), key=sort_fn))
            fields_list.append(self.calculate_field_properties(fields))

        self.fields = fields_list
        self.first_call = False

        # limit scrolling, so that it stops on the last displayed container
        self.screen.scroll_limit = lines[-2]


class ContainerList(DisplayFunction):

    def __init__(self, subwindow, dopq, mode):
        """
                initializes fields, displayed_information and form template
                :param subwindow: instance of SubWindowAndPad
                :param dopq: instance of DopQ
                """

        super(ContainerList, self).__init__(subwindow, dopq)

        # store which list to fetch on update
        self.mode = mode

        width = self.screen.size[1]
        width_unit = width // 8

        # init fields dict
        self.fields = [{'position': '',
                        'name': '',
                        'status': '',
                        'docker name': '',
                        'executor': '',
                        'run time': '',
                        'created': ''}]

        # init information dict
        self.displayed_information = []

        # init template
        self.template = [['', '  ', # position
                          ' name:  ',  # name
                          pad_with_spaces('status:  ', 5 * width_unit, 'prepend')],  # end of first line
                         ['-' * (width - 2 * self.screen.indent -1 )],  # hline
                         [pad_with_spaces('docker name:  ', 2 * width_unit, 'prepend'),
                          pad_with_spaces('executor:  ', 3 * width_unit, 'prepend')],  # end of second line
                         [pad_with_spaces('uptime:  ', 2 * width_unit, 'prepend'),
                          pad_with_spaces('created:  ', 3 * width_unit, 'prepend')]]  # end of third line

        self.height = len(self.template) + 2
        self.max_containers = self.screen.height // self.height

    def get_list(self):
        """
        obtains the relevant container list from the queue depending on the set mode
        :return: list of Container objects
        """

        if self.mode == 'history':
            container_list = self.dopq.history
        elif self.mode == 'enqueued':
            container_list = self.dopq.container_list
        else:
            raise ValueError('invalid mode of operation: {}'.format(self.mode))

        if len(container_list) > self.max_containers:
            container_list = container_list[:self.max_containers]

        return container_list

    def update(self):
        """
        gets new information from the queue and updates the fields that have changed
        :return: None
        """

        # gather new information
        container_list = self.get_list()
        information = [container.history_info() for container in container_list]
        # check if the container list length is the same
        rewrite_all = False
        if len(information) != len(self.displayed_information):
            self.write_template(len(container_list))
            rewrite_all = True

        # update displayed information
        for index, container_information in enumerate(information):
            container_information['position'] = index
            for field, value in list(container_information.items()):

                # only rewrite field if it has changed
                if rewrite_all or value != self.displayed_information[index][field]:
                    attrs = 0
                    if 'status' in field:
                        attrs = pick_color(value) | self.screen.BOLD
                    elif 'name' in field or 'position' in field:
                        attrs = self.screen.BOLD
                    self.update_field(value, self.fields[index][field], attrs)
                else:
                    continue

        # update stored information
        self.displayed_information = information

    def write_template(self, n_containers=0):
        """
        write the form template to the screen and get fields
        :return: None
        """

        # clear screen
        self.screen.redraw()

        # update number of max containers on display
        self.max_containers = self.screen.pad_height // self.height

        # combine templates according to number of containers in the list
        templates = [self.template] * n_containers

        # write the template to the display and get fields
        lines = [self.screen.offset + i * self.height for i, _ in enumerate(templates)]
        fields_list = []
        for index, (line, template) in enumerate(zip(lines, templates)):
            self.screen.navigate(y=line, x=self.screen.indent)
            coordinates = self.screen.addmultiline(template)
            fields = {'position': coordinates[0][0],
                      'name': coordinates[0][2],
                      'status': coordinates[0][3],
                      'docker name': coordinates[2][0],
                      'executor': coordinates[2][1],
                      'run_time': coordinates[3][0],
                      'created': coordinates[3][1]}

            def sort_fn(item):
                return item[1]['beginning']['y'], item[1]['beginning']['x']

            # sort the fields by their y coordinate first and x coordinate second
            fields = OrderedDict(sorted(list(fields.items()), key=sort_fn))
            fields_list.append(self.calculate_field_properties(fields))

        self.fields = fields_list if fields_list else self.fields
        self.first_call = False

        # limit scrolling, so that it stops on the last displayed container
        self.screen.scroll_limit = lines[-2] if isinstance(lines, list) and len(lines) >= 2 else self.height



def pad_with_spaces(string, total_length, mode='append'):
    string_length = len(string)
    difference = total_length - string_length
    if difference < 0:
        # compact given string to max length
        string = string[:total_length]
        difference = 0

    append, prepend, center = False, False, False
    if mode == 'append':
        append = True
        prepend = False
        center = False
    elif mode == 'prepend':
        append = False
        prepend = True
    elif mode == 'center':
        append = True
        prepend = True
        center = True
    else:
        raise ValueError('unknown mode: {}'.format(mode))

    padding = (' ' * int(floor(difference / (1+center))), ' ' * int(ceil(difference / (1+center))))
    padded_string = (prepend * padding[0]) + string + (append * padding[1])

    return padded_string


def pick_color(status):
    """
    helper for choosing an appropriate color for a status string
    :param status: status string
    :return: curses.colo_pair or 0 if status was not matched
    """

    if status == 'not started':
        return curses.color_pair(3)
    elif status == 'created':
        return curses.color_pair(3)
    elif status == 'paused':
        return curses.color_pair(3)
    elif status == 'running':
        return curses.color_pair(4)
    elif status == 'terminated':
        return curses.color_pair(5)
    elif status == 'exited':
        return curses.color_pair(5)
    elif status == 'dead':
        return curses.color_pair(5)
    else:
        return 0
