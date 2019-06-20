from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QListWidget, QTextEdit, QApplication, QListWidgetItem, QLabel
from PyQt5.QtGui import QFont

import sys
from  pyqt_interface import qt_display_process
from pyqt_interface.base_window_controller import Window
from pyqt_interface import css_layout
from PyQt5.QtCore import Qt
from utils import log

LOG = log.get_module_log(__name__)


__authors__ = "Md Rezaur Rahman, Ilja Manakov, Markus Rohm"
__copyright__ = "Copyright 2019, The DopQ Project"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Reza, Ilja, Markus"
__status__ = "Dev"


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
        self.prev_enqueued_containers = None
        self.prev_user_stat = None

    # Function for updating dock widgets
    # Data sent from QThread using signal

    def update_history_widget(self):

        pass

    def update_user_status_widget_from_thread_test(self, data):
        print("call is in user_status_widget_from_thread_test ")
        list_widget = QListWidget()

        if data is not None and data != self.prev_user_stat:
            for container in data:
                html_text = css_layout.user_status_widget_richtext_formatting(container)
                qlistitem_obj = QListWidgetItem()
                qlabel_obj = QLabel()
                qlabel_obj.setText(html_text)
                new_font = QFont("Arial", 16, QFont.Bold)
                qlabel_obj.setFont(new_font)
                qlabel_obj.adjustSize()

                qlistitem_obj.setSizeHint(qlabel_obj.sizeHint())
                list_widget.addItem(qlistitem_obj)
                list_widget.setItemWidget(qlistitem_obj, qlabel_obj)

            self.prev_user_stat = data

            self.user_stats_dock.setWidget(list_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.user_stats_dock)

    def update_status_widget_from_thread_test(self, data, isupdate):
        print("call is in dopq_status_widget_from_thread_test ")
        list_widget = QListWidget()
        if isupdate:
            html_text = css_layout.dopq_status_widget_richtext_formatting(data)
            qlistitem_obj = QListWidgetItem()
            qlabel_obj = QLabel()
            qlabel_obj.setText(html_text)
            new_font = QFont("Arial", 16, QFont.Bold)
            qlabel_obj.setFont(new_font)
            qlabel_obj.adjustSize()

            qlistitem_obj.setSizeHint(qlabel_obj.sizeHint())
            list_widget.addItem(qlistitem_obj)
            list_widget.setItemWidget(qlistitem_obj, qlabel_obj)
            self.status_dock.setWidget(list_widget)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.status_dock)

    def update_enqueue_widget_from_thread_test(self, data):
        print("call is in Enqueued_widget_from_thread_test ")
        list_widget = QListWidget()
        cnt = 1
        if data is not None and data != self.prev_enqueued_containers:
            for container in data:
                html_text = css_layout.enqueued_containers_richtext_formatting(container, cnt)
                cnt += 1
                qlistitem_obj = QListWidgetItem()
                qlabel_obj = QLabel()
                qlabel_obj.setText(html_text)
                new_font = QFont("Arial", 16, QFont.Bold)
                qlabel_obj.setFont(new_font)
                qlabel_obj.adjustSize()

                qlistitem_obj.setSizeHint(qlabel_obj.sizeHint())
                list_widget.addItem(qlistitem_obj)
                list_widget.setItemWidget(qlistitem_obj, qlabel_obj)

            self.enqueued_dock.setWidget(list_widget)
            self.prev_enqueued_containers = data
            self.addDockWidget(Qt.RightDockWidgetArea, self.enqueued_dock)

    def update_runnning_widget_from_thread_test(self, data):
        print("call is in Running_widget_from_thread_test ")
        list_widget = QListWidget()
        cnt = 1

        for container in data:
            html_text = css_layout.running_containers_richtext_formatting(container, cnt)
            cnt += 1
            qlistitem_obj = QListWidgetItem()
            qlabel_obj = QLabel()
            qlabel_obj.setText(html_text)
            new_font = QFont("Arial", 16, QFont.Bold)
            qlabel_obj.setFont(new_font)
            qlabel_obj.adjustSize()

            qlistitem_obj.setSizeHint(qlabel_obj.sizeHint())
            list_widget.addItem(qlistitem_obj)
            list_widget.setItemWidget(qlistitem_obj, qlabel_obj)

        self.running_containers_dock.setWidget(list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.running_containers_dock)

    def thread_connector(self, dopq):
        self.thread_obj = qt_display_process.QThreadWorker(dopq)
        LOG.info('Call is in : {}'.format("thread_connector function"))
        self.thread_obj.sig1.connect(self.update_status_widget_from_thread_test)
        self.thread_obj.sig4.connect(self.update_user_status_widget_from_thread_test)
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


