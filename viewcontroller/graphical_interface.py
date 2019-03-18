from viewcontroller.curses_view_controller import *

class GUICreation():
    def __init__(self, dopq, command=None):
        self.command = command
        self.dopq_obj = dopq

    def view_controller_creation(self):
        if self.command == 'curses':
            curses_obj = CursesViewController(self.dopq_obj)

        elif self.command == 'tkinter':
             pass

        elif self.command == 'None':
            # No UI, direct print progress of DOPQ in terminal
            pass

