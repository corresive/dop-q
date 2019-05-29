from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QListWidget, QTextEdit, QApplication

import sys
from  pyqt_interface import qt_display_process
from pyqt_interface.base_window_controller import Window
from PyQt5.QtCore import Qt
from utils import log

LOG = log.get_module_log(__name__)

def qt_main(dopq):
    app = QtWidgets.QApplication(sys.argv)
    window_obj = InterfacePyQT()
    window_obj.show()
    window_obj.thread_connector(dopq)
    sys.exit(app.exec_())



class InterfacePyQT(Window):
    def __init__(self):
        super(InterfacePyQT, self).__init__()
        #self.dock_widget_list = self.initialize_subwindows()
        #self.dopq = dopq
        #self.subwindows = self.split_screen()

    # Function for updating dock widgets
    # Data sent from QThread using signal

    def update_status_widget_from_thread_test(self, data):
        print("call is in update_widget_from_thread_test ")
        list_widget = self.status_dock.widget()
        final_string = "Status Entry:\n---------------\n"
        for key, val in data.items():
            if (key == "Provider Status"):
                final_string += "\n"

            final_string += key + " : " + val
            final_string += " | "
        final_string += "\n"
        list_widget.addItems([final_string])
        self.status_dock.setWidget(list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.status_dock)

    def update_enqueue_widget_from_thread_test(self, data):
        print("call is in update_widget_from_thread_test ")
        list_widget = self.enqueued_dock.widget()
        final_string = "Enqueued Containers Entry:\n--------------------------------\n"
        for key, val in data.items():
            if (key == "provider status"):
                final_string += "\n"

            final_string += key + " : " + val
            final_string += " | "

        final_string += "\n"
        list_widget.addItems([final_string])
        self.enqueued_dock.setWidget(list_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.enqueued_dock)

    def update_runnning_widget_from_thread_test(self, data):
        print("call is in update_widget_from_thread_test ")
        list_widget = self.running_containers_dock.widget()
        print(self.running_containers_dock)
        final_string = "Running Containers Entry:\n------------------------------\n"
        for key, val in data.items():
            if (key == "provider status"):
                final_string += "\n"

            final_string += key + " : " + val
            final_string += " | "

        final_string += "\n"
        list_widget.addItems([final_string])
        self.running_containers_dock.setWidget(list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.running_containers_dock)

    def thread_connector(self, dopq):
        self.thread_obj = qt_display_process.QThreadWorker(dopq)
        LOG.info('Call is in : {}'.format("thread_connector function"))
        self.thread_obj.sig1.connect(self.update_status_widget_from_thread_test)
        self.thread_obj.sig2.connect(self.update_runnning_widget_from_thread_test)
        self.thread_obj.sig3.connect(self.update_enqueue_widget_from_thread_test)
        self.thread_obj.start()

    def __call__(self, *args, **kwargs):
        """
        infinite loop that displays information and watches for input
        :param args: not used
        :param kwargs: not used
        :return: None
        """
        pass


