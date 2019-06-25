import sys
from utils import log
from . import interface_curses
from pyqt_interface import qt_display_process, qt_interface
from PyQt5 import QtWidgets


LOG = log.get_module_log(__name__)

"""
    Entry Point for different GUI creation.
    
"""

class GUICreation():
    def __init__(self, dopq):
        self.command = dopq.gui_option
        self.dopq_obj = dopq
        self.view_controller_creation()

    def view_controller_creation(self):
        if self.command == 'curses':
            LOG.info('Command is: {}'.format(self.command))
            interface_curses.start_interface(self.dopq_obj)


        elif self.command == 'pyqt':
            LOG.info('Command is: {}'.format(self.command))
            #app = QtWidgets.QApplication(sys.argv)
            #mywindow = qt_interface.InterfacePyQT(self.dopq_obj)
            #mywindow.show()
            #sys.exit(app.exec_())
            qt_interface.qt_main(self.dopq_obj)



        elif self.command == 'None':
            # No UI, direct print progress of DOPQ in terminal
            pass
