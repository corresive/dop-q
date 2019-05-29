import copy
from collections import OrderedDict
from pyqt_interface.base_window_controller import DisplayFunction
from PyQt5.QtCore import pyqtSignal, QThread

from math import floor, ceil

from utils import log

LOG = log.get_module_log(__name__)


def fetch_running_containers_info(dopq):
    information = []
    containers = copy.copy(dopq.running_containers)
    for container in dopq.running_containers:
        print("container: ", container.container_stats())
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

    infor = {}
    infor['Enqueued Status'] = 'Still Running ...'
    infor['Container Name'] = 'Captain Loser'
    infor['Container starttime'] = '15:45, 1971'

    return infor


def fetch_enqueued_containers_info(dopq):
    information = {}
    information['Enqueued Status'] = 'Still Running ...'
    information['Container Name'] = 'Captain Loser'
    information['Container starttime'] = '15:45, 1971'

    return information


def fetch_status_info(dopq):
    information = {}
    information['Name'] = 'Reza ...'
    information['Purpose'] = 'Testing'

    information['Queue Status'] = dopq.status
    information['Queue Uptime'], information['Queue Starttime'] = dopq.uptime
    information["Provider Status"] = dopq.provider.status
    information['Provider Uptime'], information['Provider Starttime'] = dopq.provider.uptime

    return information

class QThreadWorker(QThread):
    sig1 = pyqtSignal(dict)
    sig2 = pyqtSignal(dict)
    sig3 = pyqtSignal(dict)
    def __init__(self, dopq, parent=None):
        QThread.__init__(self, parent)
        self.dopq = dopq

    def run(self):
        self.running = True
        while self.running:
            self.sig1.emit(fetch_status_info(self.dopq))
            self.sig2.emit(fetch_running_containers_info(self.dopq))
            self.sig3.emit(fetch_enqueued_containers_info(self.dopq))
            self.sleep(3)

""" 
    Display class for DopQ Status information
"""
'''
class Status(DisplayFunction):
    def __init__(self, subwindow, dopq):
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

        self.template = [['queue: '], ['uptime:  '], ['starttime: '],
                           ["\n"],
                           ['provider: '], ['uptime:  '], ['starttime:  '],
                           ['\n']
                        ]


    def update_info(self):

        LOG.info('Command is in: {}'.format("Status call() is in update_info"))

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
            print("field,value :", field, value)

            # skip if information has not changed
            if value == self.displayed_information[field]:
                continue

            # overwrite information that has changed
            #attrs = pick_color(value) | self.screen.BOLD if 'status' in field else 0
            #self.update_dock_content(value, self.fields[field])

        self.displayed_information = information

    def load_template(self):
        """
        writes template to display on first call
        :return:
        """
        LOG.info('Command is in: {}'.format("Status call() is in load_template"))
        # get the beginning and end coordinates for every string in the template
        #coordinates = self.screen.addmultiline(self.template)
        fields = {'queue status': "Not Running",
                  'queue uptime': "Nil",
                  'queue starttime': "Nil",
                  'provider status': "Not Running",
                  'provider uptime': "Nil",
                  'provider starttime': "Nil"
                  }

        # sort the dict according to y coordinates first and x coordinates second
        def sort_fn(item):
            return item[1]['beginning']['y'], item[1]['beginning']['x']

        #fields = OrderedDict(sorted(list(fields.items()), key=sort_fn))
        #self.fields = self.calculate_field_properties(fields)

        self.first_call = False


class RunningContainers(DisplayFunction):
    def __init__(self, subwindow, dopq):
        super(RunningContainers, self).__init__(subwindow, dopq)
        pass


class EnqueuedContainers(DisplayFunction):
    def __init__(self, subwindow, dopq):
        super(EnqueuedContainers, self).__init__(subwindow, dopq)
        pass


class UserStats(DisplayFunction):
    def __init__(self, subwindow, dopq):
        super(UserStats, self).__init__(subwindow, dopq)
        pass


class History(DisplayFunction):
    def __init__(self, subwindow, dopq):
        super(History, self).__init__(subwindow, dopq)
        pass

'''