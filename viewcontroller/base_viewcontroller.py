import os
from abc import ABC, abstractmethod

"""
    >> Abstract View Controller for the DopQ UI creation.
    >> Provides methods for different GUI implementations.
    >> Provides user with flexibility of changing GUI. 
    
    Created on Mon March 18 09:50:42 2019

"""

__authors__ = "Md Rezaur Rahman, Ilia Manakov, Markus Rohm"
__copyright__ = "Copyright 2019, The DopQ Project"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Reza, Ilia, Markus"
__status__ = "Dev"

class AbstractBaseViewController(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def base_window_creation(self, *args):
        pass

    '''@abstractmethod
    def sub_window_creation(self, *args):
        pass

    @abstractmethod
    def reset_window(self, *args):
        pass

    @abstractmethod
    def get_window_size(self, *args):
        pass

    def set_window_size(self, *args):
        pass

    @abstractmethod
    def add_text_window(self, *args):
        pass

    @abstractmethod
    def get_current_cursor_position(self, *args):
        pass

    @abstractmethod
    def navigate_cursor(self, *args):
        pass
        '''
