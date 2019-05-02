import sys, os, time
from pyqt_interface import css_layout
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QListWidget, QTextEdit, QApplication
from PyQt5.QtWidgets import QDockWidget, QLabel
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QIcon, QFont


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        title = "DockAble Application"

        self.main_window_screen_resize()
        self.main_window_layout()

        self.textEdit = QTextEdit()
        self.setCentralWidget(None)

        # Initialize SubWindow variables. All are QDockWidget object
        self.status_dock = None
        self.user_stats_dock = None
        self.running_containers_dock = None
        self.enqueued_dock = None
        self.history_dock = None
        self.initialize_subwindows()

    # Load the sub windows for the first time
    def initialize_subwindows(self):
        self.status_dock = self.dock_userstats()
        self.user_stats_dock = self.dock_status()
        self.running_containers_dock = self.dock_running_continers()
        self.enqueued_dock = self.dock_enqueued_containers()
        self.history_dock = self.dock_history()

    def main_window_screen_resize(self):
        self.showMaximized()
        #self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle("  DopQ LMU AugenKlinik")

    def main_window_layout(self):
        self.setStyleSheet(css_layout.main_window_layout)


    def subdoc_font_customization(self):
        current_font = self.font()
        current_font.setBold(True)
        current_font.setPixelSize(25)
        current_font.setFamily("")

        return current_font

    def subdoc_custom_title_bar(self, subwin_name):
        label = None

        if subwin_name == "userstats":
            label = QLabel("                                                     ~~~ User Statistics ~~~"
                           "\n                                                     ----------------------------------")
            label.setStyleSheet(css_layout.userstats_title_bar)

        elif subwin_name == "status":
            label = QLabel("                                                     ~~~ Status ~~~"
                           "\n                                                     -----------------------")
            label.setStyleSheet(css_layout.status_title_bar)

        elif subwin_name == "running":
            label = QLabel("                                             ~~~ Running Containers ~~~"
                           "\n                                             -----------------------------------------")
            label.setStyleSheet(css_layout.running_cont_title_bar)

        elif subwin_name == "enqueued":
            label = QLabel("                                             ~~~ Enqueued Containers ~~~"
                           "\n                                             -------------------------------------------")
            label.setStyleSheet(css_layout.enqueued_cont_title_bar)

        elif subwin_name == "history":
            label = QLabel("                                                  ~~~ History ~~~"
                           "\n                                                  ------------------------")
            label.setStyleSheet(css_layout.history_title_bar)


        return label

    def screen_geometry_details(self):
        screenGeometry = QApplication.desktop()
        rect = screenGeometry.availableGeometry()
        print("Screen_width: ", rect.width())
        print("Screen_Height: ", rect.height())
        return rect.height(), rect.width()

    def dock_header(self):
        dock = QDockWidget(self)
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("header"))
        dock.setFeatures(dock.NoDockWidgetFeatures)
        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width)
        dock.setFixedHeight(height // 10 ) # 10% of total height


    def dock_status(self):
        dock = QDockWidget(self)
        #dock.setWindowTitle("~~~ Current Status ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("status"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight(height//5 - 10) # 1/5th of total height

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.data = ["Entry 1", "======================\nRexa", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "hfdjh", "Pear", "Banana",
                        "Entry 2", "======================", "Pear", "Banana",
                        "App", "Melon", "shetw", "Banana",
                        "dhfjhd", "sdh", "Pear", "erere"]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def dock_userstats(self):
        dock = QDockWidget(self)
        #dock.setWindowTitle("~~~ User Statistics ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("userstats"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight(height//5 - 10) # 1/5th of total height

        dock.setStyleSheet(css_layout.dockwidget_layout)

        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.data = ["App", "Melon", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "hfdjh", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "Melon", "shetw", "Banana",
                        "dhfjhd", "sdh", "Pear", "erere"]
        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def dock_running_continers(self):
        dock = QDockWidget(self)
        #dock.setWindowTitle("~~~ Running Containers ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("running"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight((height*4)//5 - 20) # 80% of the height

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.data = ["Entry 1", "======================\nRexa", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "hfdjh", "Pear", "Banana",
                        "Entry 2", "======================", "Pear", "Banana",
                        "App", "Melon", "shetw", "Banana",
                        "dhfjhd", "sdh", "Pear", "erere",
                        "Entry 3", "======================", "Pear", "Banana",
                        "App", "Melon", "shetw", "Banana",
                        "dhfjhd", "sdh", "Pear", "erere"]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def dock_enqueued_containers(self):
        dock = QDockWidget(self)
        #dock.setWindowTitle("~~~ Enqueued Containers ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("enqueued"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width // 2)
        dock.setFixedHeight((height//5) * 2 - 12)

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.data = ["Entry 1", "======================\nRexa", "Pear", "Banana",
                         "App", "Melon", "Pear", "Banana",
                         "App", "Melon", "Pear", "Banana",
                         "App", "hfdjh", "Pear", "Banana",
                         "Entry 2", "======================", "Pear", "Banana",
                         "App", "Melon", "shetw", "Banana",
                         "dhfjhd", "sdh", "Pear", "erere"]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def dock_history(self):
        dock = QDockWidget(self)
        #dock.setWindowTitle("~~~ History ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("history"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width // 2)
        dock.setFixedHeight((height//5) * 2 - 12)

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.data = ["Entry 1", "======================\nRexa", "Pear", "Banana",
                         "App", "Melon", "Pear", "Banana",
                         "App", "Melon", "Pear", "Banana",
                         "App", "hfdjh", "Pear", "Banana",
                         "Entry 2", "======================", "Pear", "Banana",
                         "App", "Melon", "shetw", "Banana",
                         "dhfjhd", "sdh", "Pear", "erere"]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)


"""
    Each subwindow is a QDockWidget instance
"""
'''
class SubWindow(Window):
    def __init__(self):
        super(SubWindow, self).__init__()

        self.status_dock = self.subwindow_status()

    def subdoc_custom_title_bar(self):
        label = QLabel("                                     ~~~ Status ~~~"
                       "\n                                   ---------------")
        label.setStyleSheet(css_layout.userstats_title_bar)
        return label

    def subwindow_status(self):
        dock = QDockWidget(self)
        dock.setWindowTitle("~~~ Current Status ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar())
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight(height//2 - 10)

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.data = ["Entry 1", "======================\nRexa", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "hfdjh", "Pear", "Banana",
                        "Entry 2", "======================", "Pear", "Banana",
                        "App", "Melon", "shetw", "Banana",
                        "dhfjhd", "sdh", "Pear", "erere"]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        return dock

    def update_doc(self, dock):
        list_widget = dock.widget()
        self.data = ["Updated Entry", "======================\nMikayla", "Markus", "Banana",
                     "App", "Melon", "Pear", "Banana",
                     "App", "Melon", "Pear", "Banana",
                     "App", "hfdjh", "Pear", "Banana"]
        list_widget.addItems(self.data)
        dock.setWidget(list_widget)
        
        #self.addDockWidget(Qt.RightDockWidgetArea, dock)
        return dock
        '''

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")
    mainWin = Window()
    mainWin.show()

    sys.exit(app.exec_())