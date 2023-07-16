#!/usr/bin/env python3
# -*- encoding: utf8 -*-

## TODO-List for this file:
#   - BUG: The cursor position is not visible when running the application in Windows OS
#   - Implement a text-field with a fixed size that switches to the next one when it is full

import curses
import string

class textfield:
    """
    A class to handle a curses input field
    Every input field is its own curses window. Each keystroke has to be passed by the window (because some keystrokes might be reserved to move the cursor to another text field). The constructor takes a window as an argument and changes it to a text window (important: the window has to be one row high)

    Parameters
    ----------
    window : curses.window
        This whole window object will be turned into a text-field. The window needs to have a height of 1 line, otherwise the call of this function will raise an Exception
    colors : curses color pair
        This is the color pair specifying he foreground and the background color for the window
    init_str : str, optional
        The text field can be filled with a default string in the beginning. The cursor position will always be set after the last character of the string
    """

    def __init__(self, window : curses.window, colors, init_str = ""):
        self.window = window
        self.content = init_str
        self.cursor_position = len(self.content)
        height, self.window_length = window.getmaxyx()
        if not int(height) == 1:
            raise Exception("Error while initialising text field: Height of window is not 1")

        self.colors = colors
        self.window.bkgd(self.colors)

        self.draw()

    def draw(self):
        """
        This function draws the text field with its content and the cursor.
        It is mostly used to draw the initial state and redraw it after every update
        """
        self.window.clear()

        ## first try to draw the whole text into the window. Assume that it fits in there
        str_start = 0
        str_end = len(self.content)
        
        draw_cursor_at = self.cursor_position
        # put the cursor on its assigned position

        ## If the text does not fit some modifications have to be made
        if len(self.content) > (self.window_length - 1):
            center = self.window_length // 2
            # the Center of the text field

            if self.cursor_position <= center:
                # the cursor is close to the left half of the text field
                str_end = self.window_length - 1
                # start position stays at 0
                # cursor position stays unmodified
            elif self.cursor_position > (len(self.content) - (self.window_length - 1 - center) - 1):
                # the cursor is close to the right end of the string
                # the -1 which will be subtracted is the extra space for the cursor
                # furthermore the window_length has to be decremented because the index count
                # starts by 0 while the length count starts by 1
                str_start = str_end - (self.window_length - 1)
                draw_cursor_at = self.cursor_position - str_start
            else:
                # cursor is somewhere in the middle of the string
                # put everything in the middle
                draw_cursor_at = center
                str_start = self.cursor_position - center
                str_end = str_start + (self.window_length)

        self.window.insstr(0, 0, self.content[str_start:str_end])
        self.window.move(0, draw_cursor_at)

        self.window.refresh()

    def _add(self, insert : str) -> None:
        """
        Add a character to the string at the current cursor position

        Parameters
        ----------
        insert : string
            This string will be added at the current cursor position and the cursor will move the needed amount of characters to the right side
        """
        # Add a string
        self.content = self.content[0:self.cursor_position] + insert + self.content[self.cursor_position:]
        self.cursor_position += len(insert)

    def _delete(self) -> None:
        """
        This will delete the character before the cursor, as long as the cursor is not at position 0 in the string
        """
        # delete the character before the cursor
        if self.cursor_position > 0:
            self.content = self.content[0:self.cursor_position - 1] + self.content[self.cursor_position:]
            self.cursor_position -= 1

    def input(self, in_char : str | int) -> None | str:
        """
        Handle user input. This function takes the return value from curses stdscr.get_wch() and performs the needed task to update the content of the text window, the cursor position and redraw the updated text field.
        When the input is not a string then some special operations e.G. move the cursor one position to the left / right are being processed.
        If everything went fine this function returns a None, otherwise if no rule for this specified input was specified it returns the input parameter to inform the surrounding code which called this function about this case.

        Parameters
        ----------
        in_char : string, int
            This is the inserted operation (string containing a printable character or key-code for some controlling operations) which this text field should process. In general this should most likely be the return value from stdscr.get_wch()

        Returns
        -------
        in_char : None, int
            If for this character an operation could be performed then this function returns a None object. Otherwise it returns the input character so some other code can process it.
        """
        #TODO: Handle more inputs, e.g. CTRL+LEFT/RIGHT to skip words or CTRL+w to delete words backwards.

        if type(in_char) == str and not (in_char in ["\n", "\t"]):
            # add printable characters except newline and tab
            self._add(in_char)

        elif type(in_char) == int:
            # Here are all the non printable characters which the text
            # field has to handle
            match in_char:
                case curses.KEY_DC | curses.KEY_BACKSPACE:
                    # Backspace Key
                    self._delete()

                case curses.KEY_LEFT:
                    # move cursor to left
                    if self.cursor_position > 0:
                        self.cursor_position -= 1
                    else:
                        # if the boundary is reached: send an information
                        return in_char

                case curses.KEY_RIGHT:
                    # move cursor to right
                    if self.cursor_position < len(self.content):
                        self.cursor_position += 1
                    else:
                        # if the boundary is reached: send an information
                        return in_char

        else:
            return in_char

        self.draw()
        return None


if __name__ == "__main__":
    def main(stdscr : curses.window):
        win = curses.newwin(1,20, 5, 5)
        stdscr.refresh()

        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        COLORS = curses.color_pair(1)

        form_input = textfield(win, COLORS, "Test")

        while True:
            key = form_input.input(stdscr.get_wch())
            if key == "\n":
                break;


curses.wrapper(main)
