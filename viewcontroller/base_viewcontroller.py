import os
from abc import ABC, abstractmethod

"""
    >> Abstract View Controller for the DopQ UI creation.
    >> Provides methods for different GUI implementations.
    >> Provides user with flexibility of changing GUI. 
    
    Created on Mon March 18 09:50:42 2019

"""

__authors__ = "Md Rezaur Rahman, Ilja Manakov, Markus Rohm"
__copyright__ = "Copyright 2019, The DopQ Project"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Reza, Ilja, Markus"
__status__ = "Dev"


class AbstractBaseViewController(object):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def navigate(self, *args):
        """
        Moves the current cursor to another specific coordinate
        :param args: Current cursor position as coordinate.
        :return: New coordinate position
        """
        pass

    @abstractmethod
    def add_string(self, *args):
        """
        Adding specific string/word in the display window.
        Developer should change return type according to GUI requirement.
        :param args: String to write, with text formatting as attributes
        :return: cursor coordinates after writing the string.
        """
        pass

    @abstractmethod
    def add_line(self, *args):
        """
        Writing a list of strings, each with their own formatting, onto a line in the window.
        Developer should change return type according to GUI requirement.
        :param args: List of strings with their formatting
        :return: cursor coordinates after writing the strings.
        """
        pass

    @abstractmethod
    def refresh(self, *args):
        """
        Refresh the display window object
        :param args:
        :return: None
        """
        pass

    @abstractmethod
    def erase(self, *args):
        """
        Erase text from display window
        :param args:
        :return: None
        """
        pass

