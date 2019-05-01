import sys, os
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
        top = 400
        left = 400
        width = 600
        height = 500

        icon = "icon.png"

        #self.setWindowTitle(title)
        #self.setGeometry(top,left, width, height)
        self.main_window_screen_resize()
        self.main_window_color()
        #self.setWindowIcon(QIcon("icon.png"))

        self.textEdit = QTextEdit()
        self.setCentralWidget(None)

        self.dock_userstat()
        self.dock_enqueued()
        self.dock_running_continers()
        self.dock_finished_containers()
        self.dock_history()

    def main_window_screen_resize(self):
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle("  DopQ LMU AugenKlinik")


    def main_window_color(self):
        self.setStyleSheet("background-color: rgb(250,250,210); "
                           "margin:5px; "
                           "border:0px solid rgb(0, 255, 0);")

    def subdoc_font_customization(self):
        current_font = self.font()
        current_font.setBold(True)
        current_font.setPixelSize(25)
        current_font.setFamily("")

        return current_font

    def subdoc_custom_title_bar(self):
        label = QLabel("                                     ~~~ User Statistics ~~~"
                       "\n                                   --------------------------------")
        label.setStyleSheet(css_layout.dockwidget_title_bar)
        return label

    def screen_geometry_details(self):
        screenGeometry = QApplication.desktop()
        rect = screenGeometry.availableGeometry()
        print("Screen_width: ", rect.width())
        print("Screen_Height: ", rect.height())
        return rect.height(), rect.width()

    def dock_enqueued(self):
        dock = QDockWidget(self)
        dock.setWindowTitle("~~~ Enqueued ~~~")
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

    def dock_userstat(self):
        dock = QDockWidget(self)
        dock.setWindowTitle("~~~ User Statistics ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar())
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight(height//2 - 10)

        dock.setStyleSheet(css_layout.dockwidget_layout)
        '''dock.setStyleSheet("background-color: rgb(128, 0, 128); "
                           "margin:5px; "
                           "border:7px solid rgb(255, 255, 240);")'''
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.myfruit = ["App", "Melon", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "hfdjh", "Pear", "Banana",
                        "App", "Melon", "Pear", "Banana",
                        "App", "Melon", "shetw", "Banana",
                        "dhfjhd", "sdh", "Pear", "erere"]
        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.myfruit)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def dock_running_continers(self):
        dock = QDockWidget(self)
        dock.setWindowTitle("~~~ Running Containers ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar())
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight(height//3 - 10)

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

    def dock_finished_containers(self):
        dock = QDockWidget(self)
        dock.setWindowTitle("~~~ Finished ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar())
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width // 2)
        dock.setFixedHeight(height // 3 - 10)

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

    def dock_history(self):
        dock = QDockWidget(self)
        dock.setWindowTitle("~~~ History ~~~")
        dock.setTitleBarWidget(self.subdoc_custom_title_bar())
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width // 2)
        dock.setFixedHeight(height // 3 - 10)

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

'''
class mywindow(QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.setCentralWidget(None)
        self.main_window_screen_resize()
        self.main_window_color()
        self.topleftdockwindow()

    def main_window_screen_resize(self):
        QWidget.showMaximized(self)

    def main_window_color(self):
        self.setStyleSheet("background-color: rgb(15,150,119); "
                           "margin:5px; "
                           "border:1px solid rgb(0, 255, 0);")

    def topleftdockwindow(self):
        topleft_window = QDockWidget('Info',self)
        topleft_window.setStyleSheet("background-color: rgb(212,150,119);\
                                     margin:5px; \
                                     border:5px solid rgb(255, 120, 0);")
        topleft_window.resize(50,60)
        # Stick window to left or right
        topleft_window.setAllowedAreas(Qt.NoDockWidgetArea)
        self.addDockWidget(Qt.TopDockWidgetArea, topleft_window)

        #topleftwindow.setWidget()
        #topleftwindow.resize( topleftwindow.minimumSize())
        #bottomleftwindow = QDockWidget("Matplot",self)
        #bottomleftwindow.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        #self.addDockWidget(Qt.BottomDockWidgetArea, bottomleftwindow)
        #bottomleftwindow.setWidget(createplotwidget())
        #self.setDockNestingEnabled(True)
        #topleftwindow.resize( topleftwindow.minimumSize() )
        #self.splitDockWidget(topleftwindow, bottomleftwindow , Qt.Vertical)
'''


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")
    mainWin = Window()
    mainWin.show()
    sys.exit(app.exec_())