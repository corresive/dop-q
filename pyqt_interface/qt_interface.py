from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QListWidget, QTextEdit, QApplication

import sys
import  pyqt_interface.qt_display_process as display_process
from pyqt_interface.base_window_controller import Window, SubWindow
from utils import log

LOG = log.get_module_log(__name__)

def qt_main(dopq):
    app = QtWidgets.QApplication(sys.argv)
    mywindow = InterfacePyQT(dopq)
    mywindow.show()
    #mywindow()
    sys.exit(app.exec_())


class InterfacePyQT(Window):
    def __init__(self, dopq, interval=1):
        super(InterfacePyQT, self).__init__()
        self.dock_widget_list = self.initialize_subwindows()
        self.dopq = dopq
        #self.subwindows = self.split_screen()

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


    def sub_dock_update(self, parent, func, dockwidget):
        """
        Function call for updating sub-windows/ Dock Widgets
        :param :
        :return: None
        """
        LOG.info('Command is in: {}'.format("call() is in sub_dock_update"))
        return SubWindow(parent, func, dockwidget)

    """
        Wrapper for initializing subwindows from parent Window class
    """
    def split_screen(self):
        #sub_win_objs = self.initialize_subwindows()
        LOG.info('Command is in: {}'.format("call() is in split_screen"))
        # create subwindows
        subwindows = {
            'status': self.sub_dock_update(self, display_process.Status, self.dock_widget_list[0]),
            'containers': self.sub_dock_update(self, display_process.RunningContainers, self.dock_widget_list[2]),
            'userstats': self.sub_dock_update(self, display_process.UserStats, self.dock_widget_list[1]),
            'enqueued': self.sub_dock_update(self, display_process.EnqueuedContainers, self.dock_widget_list[3]),
            'history': self.sub_dock_update(self, display_process.History, self.dock_widget_list[4])
        }


        return subwindows

    def print_information(self):
        """
        wrapper for calling all subwindow functions
        :return:
        """

        for sub in list(self.subwindows.values()):
            LOG.info('Command is in: {}'.format("call() is in print_information"))
            sub()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle("Fusion")
    mainWin = InterfacePyQT("")

    sys.exit(app.exec_())