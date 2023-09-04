#!/usr/bin/env python3
# -*- encoding: utf8 -*-

# TODO-List for this file:
#   - BUG: The cursor position is not visible when running the application in Windows OS

# TODO-List for features
#   - handle mouse click inputs
#   - handle terminal resize

import curses


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

    def __init__(self, window: curses.window, colors, init_str=""):
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

        # first try to draw the whole text into the window. Assume that it fits in there
        str_start = 0
        str_end = len(self.content)

        draw_cursor_at = self.cursor_position
        # put the cursor on its assigned position

        # If the text does not fit some modifications have to be made
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

    def add(self, insert: str) -> None:
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

        # update view
        self.draw()

        # return a None object because this keystroke was handled and there are no more operations needed
        return None

    def delete(self) -> None:
        """
        This will delete the character before the cursor, as long as the cursor is not at position 0 in the string
        """
        # delete the character before the cursor
        if self.cursor_position > 0:
            self.content = self.content[0:self.cursor_position - 1] + self.content[self.cursor_position:]
            self.cursor_position -= 1
        else:
            return curses.KEY_BACKSPACE

        # update view
        self.draw()

        # return a None object because this keystroke was handled and there are no more operations needed
        return None

    def move_cursor_right(self) -> None | int:
        """
        Move the cursor one position to the right (if possible).
        If the cursor is at the end of the string: leave it at the same position and return curses.KEY_RIGHT

        Returns
        -------
        return : None | int
            if the cursor was moved one position to the right: return an None (there is no more key to handle).
            When the cursor is at the end of the string and there is no possibility to move it one position to the right: return curses.KEY_RIGHT as an indicator for the keystroke which still needs to be processed
        """

        # move cursor to right
        if self.cursor_position < len(self.content):
            self.cursor_position += 1
            self.draw()
            return None
        else:
            # if the boundary is reached: send an information
            return curses.KEY_RIGHT

    def cursor_to_end(self):
        """
        Move the cursor to the end of the string
        """
        self.cursor_position = len(self.content)

    def move_cursor_left(self) -> None | int:
        """
        Move the cursor one position to the left (if possible).
        If the cursor is at the beginning of the string: leave it at the same position and return curses.KEY_LEFT

        Returns
        -------
        return : None | int
            if the cursor was moved one position to the left: return an None (there is no more key to handle).
            When the cursor is at the beginning of the string and there is no possibility to move it one position to the left: return curses.KEY_LEFT as an indicator for the keystroke which still needs to be processed
        """

        # move cursor to left
        if self.cursor_position > 0:
            self.cursor_position -= 1
            self.draw()
            return None
        else:
            # if the boundary is reached: send an information
            return curses.KEY_LEFT

    def input(self, in_char: str | int) -> None | str:
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
        # TODO: Handle more inputs, e.g. CTRL+LEFT/RIGHT to skip words or CTRL+w to delete words backwards.

        if type(in_char) == str and not (in_char in ["\n", "\t"]):  # noqa: E721
            # add printable characters except newline and tab
            return self.add(in_char)

        elif type(in_char) == int:  # noqa: E721
            # Here are all the non printable characters which the text
            # field has to handle
            match in_char:
                case curses.KEY_DC | curses.KEY_BACKSPACE:

                    """
                    # if the text field has a limited length and there is nothing inside the text field: send an information
                    if self.limited and len(self.content) == 0:
                        return in_char
                    """

                    # Backspace Key
                    return self.delete()

                case curses.KEY_LEFT:
                    # move cursor to left
                    return self.move_cursor_left()

                case curses.KEY_RIGHT:
                    # move cursor to right
                    return self.move_cursor_right()

        # no operation was done and the function has still returned nothing
        return in_char


class textfield_fixed(textfield):
    """
    The same as `textfield` but the input length is set to an upper limit
    """

    # call the same constructor as for the `textfield` class
    def __init__(self, window: curses.window, colors, init_str=""):
        super().__init__(window, colors, init_str)

    def draw(self) -> None:
        """
        This function draws the text field with its content and the cursor.
        It is mostly used to draw the initial state and redraw it after every update
        """
        self.window.clear()

        self.window.insstr(0, 0, self.content)
        if (self.cursor_position < self.window_length):
            self.window.move(0, self.cursor_position)

        self.window.refresh()

    def add(self, insert: str) -> None:
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

        # update view
        self.draw()

        if len(self.content) >= self.window_length:
            # return a movement one place to the right as a signal that the input field is full and a switch to the next form object should be done
            return curses.KEY_RIGHT
        else:
            # keystroke was handled and there are no further operations needed
            return None

    def delete(self) -> None:
        """
        This will delete the character before the cursor, as long as the cursor is not at position 0 in the string
        """
        # delete the character before the cursor
        if self.cursor_position > 0:
            self.content = self.content[0:self.cursor_position - 1] + self.content[self.cursor_position:]
            self.cursor_position -= 1
        else:
            return curses.KEY_BACKSPACE

        # update view
        self.draw()

        # return a None object because this keystroke was handled and there are no more operations needed
        return None

    def move_cursor_right(self) -> None | int:
        """
        Move the cursor one position to the right (if possible).
        If the cursor is at the end of the string: leave it at the same position and return curses.KEY_RIGHT

        Returns
        -------
        return : None | int
            if the cursor was moved one position to the right: return an None (there is no more key to handle).
            When the cursor is at the end of the string and there is no possibility to move it one position to the right: return curses.KEY_RIGHT as an indicator for the keystroke which still needs to be processed
        """

        # move cursor to right
        if self.cursor_position < len(self.content) - 1:
            self.cursor_position += 1
            self.draw()
            return None
        else:
            # if the boundary is reached: send an information
            return curses.KEY_RIGHT


class button:
    """
    Create a button with curses

    Attributes
    ----------
    window : curses.window
        The Window object in which the button will be drawn
    text : str
        The text inside the button
    colors :
        The colors used for this button (inverted when active)

    """

    def __init__(self, window: curses.window, colors, text: str):
        self.window = window
        self.text = text

        self.colors = colors
        self.window.bkgd(self.colors)

        self.deactivate()
        self.draw()

    def draw(self):
        """
        Draw the button
        """
        self.window.insstr(0, 0, "< " + self.text + " >")
        self.window.refresh()

    def deactivate(self):
        """
        deactivate the button
        """
        curses.curs_set(1)
        self.window.attron(curses.A_REVERSE)
        self.draw()

    def activate(self):
        """
        activate the button
        """
        curses.curs_set(0)
        self.window.attroff(curses.A_REVERSE)
        self.draw()

    def input(self, in_char):
        """
        Dummy input function, because a button processes no input

        Parameters
        ----------
        in_char : str, int
            the input character

        Returns
        -------
        in_char : str, int
            same as the parameter
        """
        return in_char

    def cursor_to_end(self):
        """
        Dummy function, because otherwise it might break the code
        """
        pass

    def delete(self):
        """
        Dummy function, because otherwise it might break the code
        """
        pass


class quit_button(button):
    """
    Create a button which terminates the program if ENTER is pressed

    Attributes
    ----------
    window : curses.window
        The Window object in which the button will be drawn
    text : str
        The text inside the button
    colors :
        The colors used for this button (inverted when active)

    """

    def __init__(self, window: curses.window, colors, text: str):
        super().__init__(window, colors, text)

    def input(self, in_char):
        """

        Parameters
        ----------
        in_char : str, int
            The input character

        Returns
        -------
        in_char : str, int
            same as the parameter but only if it is not ENTER

        """
        if in_char in ["\n"]:
            exit(0)  # the program should be aborted
        else:
            return in_char


keys = []

if __name__ == "__main__":
    """
    This function only exists to test the development of the module and provide an example. It creates objects of the containing classes and provides a simple demo and how to use them
    """
    def main(stdscr: curses.window):

        # choose a color pair for demonstration purpose
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        COLORS = curses.color_pair(1)

        # draw some explaining text to this example
        stdscr.addstr(4, 5, "This is an example text field with infinite length")
        stdscr.addstr(6, 5, "Here are two example text fields with finite length")
        stdscr.addstr(8, 5, "Again an example text field with infinite length")

        forms = [
            textfield(curses.newwin(1, 10, 5, 5), COLORS, "Test"),
            textfield_fixed(curses.newwin(1, 5, 7, 5), COLORS, ""),
            textfield_fixed(curses.newwin(1, 5, 7, 15), COLORS, ""),
            textfield(curses.newwin(1, 10, 9, 5), COLORS, "Test"),
            quit_button(curses.newwin(1, 8, 12, 5), COLORS, "Quit"),
            button(curses.newwin(1, 8, 12, 15), COLORS, "Exit")
        ]

        stdscr.refresh()

        # draw all the text-fields and the button so they are visible
        for i in forms:
            i.draw()

        current_field = forms[0]    # first text field should be set as starting point
        current_field.draw()    # set cursor position to the right object

        # this loop handles all the input events
        while True:
            key = current_field.input(stdscr.get_wch())

            if isinstance(current_field, button):
                current_field.deactivate()
                current_field.draw()

            global keys
            keys.append(key)

            if key in [curses.KEY_RIGHT, "\n", "\t"]:

                if key in ["\n", "\t"] and current_field == forms[-1]:
                    break

                # move one place to the right / downstairs if possible
                position = forms.index(current_field)
                if position != (len(forms) - 1):
                    current_field = forms[position + 1]

            if key in [curses.KEY_LEFT, curses.KEY_DC, curses.KEY_BACKSPACE]:
                # move one place to the left / upstairs
                position = forms.index(current_field)
                if position > 0:
                    current_field = forms[position - 1]

                if key in [curses.KEY_DC, curses.KEY_BACKSPACE]:
                    # if the key was a backspace key: delete cursor
                    current_field.cursor_to_end()
                    current_field.delete()
                if key == curses.KEY_LEFT and not isinstance(current_field, button):
                    # move cursor one position to the left
                    current_field.move_cursor_left()

            if isinstance(current_field, button):
                current_field.activate()
            current_field.draw()

    curses.wrapper(main)

    print("The following keystrokes were reported to the surrounding code:")
    from pprint import pprint
    pprint(keys)
