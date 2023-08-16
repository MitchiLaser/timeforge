#!/usr/bin/env python3
# -*- encoding: utf8 -*-

"""
a long List of TODO Notes
-------------------------

- Capture signals p.Ex. SIGINT (CTRL + C) or SIGTERM 

Roadmap
-------

- Make the right interconnections between the textfields
- verify user input
- Make a save dialog to enter the file location and name
- Call main application and create file

"""

import curses
import string
from datetime import datetime, date
import text_input # TODO: Make this a relative import later when the development here is done

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

        ## No blinking cursor
        #curses.curs_set(False)
        # reduce cursor to small line if possible
        curses.curs_set(1)

        # clear screen
        self.stdscr.clear()

        ## define default application colour scheme
        if curses.can_change_color():
            # if colours can be changed: use own definition
            # the curses colour definitions take the values from 0 to 7 so the first
            # self defined colour will start at 8 (first parameter)
            curses.init_color(8, 28, 212, 264)
            # RGB values have to be set to integers from 0 to 1000 (last 3 parameters) so 
            # this colour definition is equivalent to #073642
            curses.init_pair(1, curses.COLOR_WHITE, 8)
        else:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self._base_color = curses.color_pair(1)

        # define an colour scheme for the text input fields and buttons
        #TODO: Change colours or remove colour 9 and only redefine blue. I am not sure if this looks fine
        if curses.can_change_color():
            # the curses colour definitions take the values from 0 to 7 so the first
            # self defined colour will start at 8 (first parameter)
            curses.init_color(9, 142, 600, 972)
            # RGB values have to be set to integers from 0 to 1000 (last 3 parameters) so 
            # this colour definition is equivalent to #073642
            curses.init_pair(2, curses.COLOR_WHITE, 9)
            # colour 8 was defined previously
        else:
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        self._form_color = curses.color_pair(2)

        # define a background colour for the terminal
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
            [True, "Month / Year: ", 2, "/", 4], # row for the month and the year
            [False, "Name, first name: ", 20], # row for the name
            [True, "Personel number: ", 7], # row for the personal number (7 digits, fixed)
            [False, "Organisation (OE): ", 20], # row for the organisation
            [True, "Working hours: ", 2,".", 1, "hours"], # the monthly working hours
            [True, "hourly wage: ", 2, ".", 2, "€"], # the hourly wage in euros and cents
        ]

        # determine the width of the longest line in the form field
        # this will also be the length of the window object corresponding to the form field
        window_length  = 0;
        for i in structure:
            line_length = 0;
            for j in i:
                if type(j) == str:
                    line_length += len(j)
                elif type(j) == int:
                    line_length += j
            if line_length > window_length :
                window_length  = line_length

        # now this information can be used to calculate the space the form needs
        # The height of the window is the sum of the following spaces:
        #   - length of the `structure` list, describing each line with an input field
        #   - one line as a gap in between
        #   - a line for the "Save" and "Exit" Button
        window_height = len(structure) + 2

        # get the size of the stdscr object to calculate the top left coordinates for the form window
        # the form window should be in the Center of the screen
        h, w = self.stdscr.getmaxyx()

        # now calculate the position of the top left corner for the form window object
        start_window_y = h//2 - window_height//2
        start_window_x = w//2 - window_length//2

        # before initialising the window object: check weather the form window and a surrounding border
        # (which needs the space of one character in each direction) fits on the screen. It is simple to check weather 1 character
        # would not fit in between the window object and the border of the screen and throw an error if this condition is met
        if (start_window_x < 1) or (start_window_y < 1) or (h - start_window_y - window_height < 1) or (w - start_window_x - window_length < 1):
            raise Exception("Error: Your terminal window is not big enough to display the whole applications user interface")

        # draw a border around the form window
        self.border = curses.newwin(window_height + 2, window_length + 2, start_window_y - 1, start_window_x - 1)
        self.border.bkgd(self._base_color)
        self.border.box()
        # add a title to the border
        title = "TimeForge"
        start_title_x = (window_length + 2)//2 - len(title)//2
        self.border.addstr(0, start_title_x - 1, "┤" + str(title) + "├")
        # draw the currently generated border
        self.border.refresh()

        # now start drawing the form window
        self.form = curses.newwin(window_height, window_length, start_window_y, start_window_x)
        self.form.bkgd(self._base_color)
        # draw the form based on the content of the `structure` variable
        # furthermore store all the text input fields in a separate structure
        self.textfields = []
        for i in range(len(structure)):
            # put cursor on current line
            self.form.move(i,0) 
            self.textfields.append([])

            # the boolean which is being used to determine if the text fields should have a fixed length or not
            fixed_length = structure[i][0]

            # now print each string or create a text field with the length of each integer
            for j in structure[i]:

                # print strings
                if type(j) == str:
                    self.form.addstr(j)

                # convert integers to text fields
                elif type(j) == int:
                    y, x = self.form.getyx()
                    # add (fixed length) input fields
                    field_generator = text_input.textfield_fixed if fixed_length else text_input.textfield
                    self.textfields[i].append(
                        field_generator(
                            curses.newwin(1, j, start_window_y + y, start_window_x + x),
                            self._form_color,
                            init_str=""
                        )
                    )
                    # add empty spaces to move the cursor to the end of the form window in case a string is following in the list
                    self.form.addstr(" "*j)
    
        # add the current month and year to the text fields in the beginning
        now = datetime.now()
        self.textfields[0][0].add(f"{now.month:02d}")
        self.textfields[0][1].add(f"{now.year:04d}")

        # Draw "save" and "Quit" buttons
        self.textfields.append(
            [
                text_input.button(
                    curses.newwin(1, 8, start_window_y + window_height - 1, start_window_x + 1),
                    self._form_color,
                    "Save"
                ),
                text_input.quit_button(
                   curses.newwin(1, 8, start_window_y + window_height - 1, start_window_x + window_length - 8 - 1),
                    self._form_color,
                    "Exit"
                )
            ]
        )

        # update the drawing of the main field and after that all the text fields
        # inside (otherwise the text fields will be overdrawn)
        self.form.refresh()
        for i in self.textfields:
            for j in i:
                j.draw()

        # put the cursor into the name input field 
        self.textfields[1][0].draw()

        # TODO: continue with the input handling and all the interconnects between the input fields

if __name__ == "__main__":
    tui = tui()
    _ = tui.stdscr.get_wch()
    del tui
