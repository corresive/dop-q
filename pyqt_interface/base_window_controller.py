from pyqt_interface import css_layout
from PyQt5.QtWidgets import QMainWindow, QWidget, QListWidget, QListView, QPlainTextEdit, QTextEdit, QApplication, QListWidgetItem
from PyQt5.QtWidgets import QDockWidget, QLabel, QHBoxLayout, QVBoxLayout, QLayout, QSizePolicy
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextDocument, QFontDatabase, QFontInfo
from utils import log

from pyqt_interface import qt_display_process

LOG = log.get_module_log(__name__)

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        title = "DockAble Application"

        self.main_window_screen_resize()
        self.main_window_layout()

        self.textEdit = QTextEdit()
        self.setCentralWidget(None)

        # Initialize SubWindow variables. All are QDockWidget object
        self.header_dock = None
        self.status_dock = None
        self.user_stats_dock = None
        self.running_containers_dock = None
        self.enqueued_dock = None
        self.history_dock = None
        self.initialize_subwindows()

    # Load the sub windows for the first time
    def initialize_subwindows(self):
        self.header_dock = self.dock_header()
        self.status_dock = self.dock_status()
        self.user_stats_dock = self.dock_userstats()
        self.running_containers_dock = self.dock_running_continers()
        self.enqueued_dock = self.dock_enqueued_containers()
        self.history_dock = self.dock_history()

        return [self.header_dock, self.status_dock, self.user_stats_dock, self.running_containers_dock,
                self.enqueued_dock, self.history_dock]


    def main_window_screen_resize(self):
        self.showMaximized()
        #self.setWindowState(QtCore.Qt.WindowMaximized)
        #self.setWindowTitle("  DopQ LMU AugenKlinik")

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
            label = QLabel()
            label.setText(css_layout.USER_STAT_TITLE_HTML)
            label.setAlignment(Qt.AlignCenter)
            new_font = QFont("Lucida Console", 15, QFont.Bold)
            label.setFont(new_font)
            label.adjustSize()
            label.setStyleSheet(css_layout.userstats_title_bar)

        elif subwin_name == "status":
            label = QLabel()
            label.setText(css_layout.STATUS_TITLE_HTML)
            label.setAlignment(Qt.AlignCenter)
            new_font = QFont("Courgette", 15, QFont.Bold)
            label.setFont(new_font)
            label.adjustSize()
            label.setStyleSheet(css_layout.status_title_bar)

        elif subwin_name == "running":
            label = QLabel()
            label.setText(css_layout.RUNNING_CONT_TITLE_HTML)
            label.setAlignment(Qt.AlignCenter)
            new_font = QFont("Courgette", 15, QFont.Bold)
            label.setFont(new_font)
            label.adjustSize()
            label.setStyleSheet(css_layout.running_cont_title_bar)

        elif subwin_name == "enqueued":
            label = QLabel()
            label.setText(css_layout.ENQUEUED_CONT_TITLE_HTML)
            label.setAlignment(Qt.AlignCenter)
            new_font = QFont("Courgette", 15, QFont.Bold)
            label.setFont(new_font)
            label.adjustSize()
            label.setStyleSheet(css_layout.enqueued_cont_title_bar)

        elif subwin_name == "history":
            label = QLabel()
            label.setText(css_layout.HISTORY_TITLE_HTML)
            label.setAlignment(Qt.AlignCenter)
            new_font = QFont("Courgette", 15, QFont.Bold)
            label.setFont(new_font)
            label.adjustSize()
            label.setStyleSheet(css_layout.history_title_bar)

        return label

    def screen_geometry_details(self):
        screenGeometry = QApplication.desktop()
        rect = screenGeometry.availableGeometry()
        print("Screen_width: ", rect.width())
        print("Screen_Height: ", rect.height())
        return rect.height(), rect.width()

    """
        Definition of the Main Window Header
        HBoxLayout can be used ....
    """

    def dock_header(self):
        dock = QDockWidget(self)
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("header"))
        dock.setFeatures(dock.NoDockWidgetFeatures)
        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width)
        dock.setFixedHeight(height * 7// 100 )  # 10% of total height

        label = QLabel()
        label.setText(css_layout.MAIN_HEADER_HTML)
        # label.setPixmap(QPixmap("../icons/lmu_aug"))
        label.setAlignment(Qt.AlignCenter)
        new_font = QFont("Courgette", 17, QFont.Bold)
        label.setFont(new_font)
        label.adjustSize()
        print("Header Label Width: ", label.height())
        dock.setStyleSheet(css_layout.dockwidget_main_header_layout)

        dock.setWidget(label)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)

        return dock

    """
        Definition of the status sub-window
    """

    def dock_status(self):
        dock = QDockWidget(self)
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("status"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight(height//4 - 10) # 25% of total height

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.data = [""]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        return dock

    """
        Definition of the User-Status sub-window
    """

    def dock_userstats(self):
        dock = QDockWidget(self)
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("userstats"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight(height * 13 // 50 - 5) # 26% of total height

        dock.setStyleSheet(css_layout.dockwidget_layout)

        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.data = [""]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        return dock

    """
        Definition of the Runinng Container sub-window
    """

    def dock_running_continers(self):
        dock = QDockWidget(self)
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("running"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width//2)
        dock.setFixedHeight((height * 66) // 100 - 5) # 60% of the height

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.data = [""]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        return dock


    """
        Definition of the Enqueued Container sub-window
    """

    def dock_enqueued_containers(self):
        dock = QDockWidget(self)
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("enqueued"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width // 2)
        dock.setFixedHeight(((height * 8) // 25)) # 32% of the height

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.data = [""]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        return dock

    """
        Definition of the History sub-window
    """

    def dock_history(self):
        dock = QDockWidget(self)
        dock.setTitleBarWidget(self.subdoc_custom_title_bar("history"))
        dock.setFont(self.subdoc_font_customization())
        dock.setFeatures(dock.NoDockWidgetFeatures)

        height, width = self.screen_geometry_details()
        dock.setFixedWidth(width // 2)
        dock.setFixedHeight(((height * 8) // 25)) # 32% of the height

        dock.setStyleSheet(css_layout.dockwidget_layout)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.data = [""]

        self.listwidget = QListWidget(dock)
        self.listwidget.addItems(self.data)
        dock.setWidget(self.listwidget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        return dock
