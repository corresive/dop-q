import copy
import curses

from math import floor, ceil
from collections import OrderedDict
from viewcontroller.curses_view_controller import DisplayFunction

"""
    >> Helper classes for displaying information in curses subwindow
    Created on Mon March 18 09:50:42 2019

"""

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
