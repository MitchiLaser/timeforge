#!/usr/bin/env python3
# -*- encoding: utf8 -*-

"""
a long List of TODO Notes
-------------------------

- Capture signals p.Ex. SIGINT (CTRL + C) or SIGTERM 

"""

import curses
from datetime import datetime

class tui:
    """
    The Text user interface for the TimeForge Application
    """

    def __init__(self):
        """
        initialise the curses session and set some session parameters
        """

        # initialise curses 
        self.stdscr = curses.initscr()
        try:
            self._init_curses()
            self._init_default_form()
        except curses.error as e:
            self._reverse()
            print("Cursed Error: %s"%e)
        except Exception as e:
            self._reverse()
            print("Error: %s"%e)

        #TODO Only for development purpose
        _ = self.stdscr.getch() # wait for keyboard input to stop application

    def __del__(self):
        self._reverse()

    def _reverse(self):
        """
        End the curses session and restore the terminal to its original state
        """
        curses.nocbreak()                   # enable line buffer
        curses.echo()                       # turn echo back on
        curses.curs_set(True)               # restore blinking cursor
        curses.endwin()                     # restore terminal to original state

    def _init_curses(self):

        if curses.has_colors():
            curses.start_color()
        else:
            # this application won't work when the terminal does not support colours
            raise IOError
        
        # kein Anzeigen gedrückter Tasten
        curses.noecho()

        # kein Line-Buffer
        curses.cbreak()

        # Escape-Sequenzen aktivieren
        self.stdscr.keypad(1)

        # No blinking cursor
        curses.curs_set(False)

        # clear screen
        self.stdscr.clear()

        ## define background screen
        if curses.can_change_color():
            # if background colour can be changed: use own definition
            # the curses colour definitions take the values from 0 to 7 so the first
            # self defined colour will start at 8 (first parameter)
            curses.init_color(8, 28, 212, 264)
            # RGB values have to be set to integers from 0 to 1000 (last 3 parameters) so 
            # this colour definition is equivalent to #073642
            curses.init_pair(1, curses.COLOR_WHITE, 8)
        else:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self._base_color = curses.color_pair(1)
        self.stdscr.bkgd(self._base_color)
        
        # display initialised screen with background color
        self.stdscr.refresh()

    def _update_size(self):
        h, w = self.stdscr.getmaxyx()
        self.h, self.w = h, w

    def _init_default_form(self):
        self._title = "TimeForge"
        
        self._main_form_content = {
            "Monat":datetime.now().month,
            "Year":datetime.now().year,
            "Name":"",
            "Number":None,
            "OE":"",
            "Time":None,
            "Money":None
        }

        #TODO: correctly fill in the parameters for this function call
        self._form = self.stdscr.newwin()




if __name__ == "__main__":
    tui = tui()
    del tui
