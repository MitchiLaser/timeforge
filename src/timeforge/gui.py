#!/usr/bin/env python3
# -*- encoding: utf8 -*-

"""
a long List of TODO Notes
-------------------------

- Capture signals p.Ex. SIGINT (CTRL + C) or SIGTERM 

Roadmap
-------

- Draw the tui with all the textfields
- Make the right interconnections between the textfields
- Place a "Save" and an "Exit" button
- verify user input
- Make a save dialog to enter the file location and name
- Call main application and create file

"""

import curses
import string
from datetime import datetime

class tui:
    """
    The Text user interface for the TimeForge Application
    """

    def __init__(self):
        """
        initialise the tui and set some session parameters
        """

        # initialise curses 
        self.stdscr = curses.initscr()
        try:
            self._init_curses()
            self._update_size()
            self._init_default_form()
            #TODO: Add further function calls here
        except curses.error as e:
            self._reverse()
            print("Cursed Error: %s"%e)
        except Exception as e:
            self._reverse()
            print("Error: %s"%e)

        #TODO: Only for testing and developing purpose here:
        _ = self.stdscr.get_wch()

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
        """
        Initialise the Curses Session
        """

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
        self._surrounding_background = curses.color_pair(0) # 0 is always wired to White and Black and cannot be changed
        self.stdscr.bkgd(self._surrounding_background)
        
        # display initialised screen with background color
        self.stdscr.refresh()

    def _update_size(self):
        """
        Get the size of stdscr which is takeing the full space of the terminal
        """
        h, w = self.stdscr.getmaxyx()
        self.h, self.w = h, w

    def _init_default_form(self):
        """
        intiialise the forumlar with all the description texts and everything else
        """
        # this is a list containing lists with the description text and the lengths of the window objects
        # it is needed to define the size of the whole form and will later be used to initialise all the window objects for the textfields
        # The first boolean value is used to determine weather the input fields in this line should have a fixed length or not
        # Each sting is placed as is and each number will be replaced with a text field of the corresponding length
        structure = [
            [True, "Month / Year: ", 2, 4], # row for the month and the year
            [False, "Name, first name: ", 20], # row for the name
            [True, "Personel number: ", 7], # row for the personal number (7 digits, fixed)
            [False, "Organisation (OE): ", 20], # row for the organisation
            [True, "Working hours: ", 2, "hours"], # the monthly working hours
            [True, "hourly wage: ", 2, ".", 2, "€"] # the hourly wage in euros and cents
        ]

        # determine the width of the longest line in the formular field
        max_length = 0;
        for i in structure:
            line_length = 0;
            for j in i:
                if isinstance(j, str):
                    line_length += len(j)
                if isinstance(j, int):
                    line_length += j
            if line_length > max_length:
                max_length = line_length

        # now this information can be used to calculate the space the form needs

        window_height = 1 + # this is the top line, needed for the surrounding border box (with title)
                        1 + # padding to the top
                        len(structure) + # main content as defined in the structure 2d list
                        1 + # one line gap in between
                        1 + # this is the row for the "Save" and the "Exit" button
                        1 + # padding to the bottom
                        1 # lowest line, needed for the surrounding 

        max_length += 2 # add extra space at the corners
        # not that the maximal length of a line is known the width of the form is known
        # TODO: continue with height -> add save and exit buttons
        height = len(structure) + 2
        height *= 2 # add a space line between each row
        height += 2 # add extra space at the corners

        h, w = self.stdscr.getmaxyx()
        start_window_y = h//2 - height//2
        start_window_x = w//2 - max_length//2

        self.form = curses.newwin(height, max_length, start_window_y, start_window_x)
        self.form.bkgd(self._base_color)
        
        #TODO: Draw the contents
        current_line = 1
        for i in structure:
            pass #TODO: Continue

        self.form.refresh()


if __name__ == "__main__":
    tui = tui()
    del tui
