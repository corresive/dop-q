import curses
import traceback

from viewcontroller.interface_dev import Interface
from utils import log, gpu
from viewcontroller.base_viewcontroller import AbstractBaseViewController

"""
    Implements base_viewcontroller Class
    GUI creation based on curses framework

"""

__authors__ = "Md Rezaur Rahman, Ilia Manakov, Markus Rohm"
__copyright__ = "Copyright 2019, The DopQ Project"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Reza, Ilia, Markus"
__status__ = "Dev"

LOG = log.get_module_log(__name__)


class CursesViewController(AbstractBaseViewController):
    def __init__(self, dopq):
        super().__init__()
        self.start_interface(dopq)
        #self.screen = curses.wrapper(self.main, dopq)
        #self.height, self.width = self.screen.self.screen.getmaxyx()

    def start_interface(self, dopq):
        try:
            curses.wrapper(self.main, dopq)
        except:
            LOG.error(traceback.format_exc())
        finally:
            gpu.GPU.stop_hardware_monitor()

    def main(self, screen, dopq):
        # define color pairs
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)

        screen.idcok(False)
        screen.idlok(False)

        interface = Interface(dopq, screen, offset=4, indent=2)
        interface()


    def base_window_creation(self, screen=None):
        if screen != None:
            self.screen = screen
        #print(self.height, " <--> ",self.width)



if __name__ == "__main__":
    x = "sfdsff"
    obj = CursesViewController(x)
    #obj.base_window_creation()