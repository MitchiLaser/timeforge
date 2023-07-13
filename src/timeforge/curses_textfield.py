#!/usr/bin/env python3
# -*- encoding: utf8 -*-

import curses
import string

class textfield:
    """
    A class to handle a curses input field
    Every input field is its own curses window. Each keystroke has to be passed by the window (because some keystrokes might be reserved to move the cursor to another text field). The constructor takes a window as an argument and changes it to a text window (important: the window has to be one row high)
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
        self.window.clear()

        # first draw an underscore everywhere to mark all the unused fields
        self.window.insstr(0, 0, "_" * self.window_length)

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
        # Add a string
        self.content = self.content[0:self.cursor_position] + insert + self.content[self.cursor_position:]
        self.cursor_position += len(insert)

    def _delete(self) -> None:
        # delete the character before the cursor
        if self.cursor_position > 0:
            self.content = self.content[0:self.cursor_position - 1] + self.content[self.cursor_position:]
            self.cursor_position -= 1

    def input(self, in_char : str) -> None | str:
        if type(in_char) == str and not (in_char in ["\n", "\t"]):
            # add printable characters except newline and tab
            # TODO: catch Control Characters, e.g. <C-w>, <C-t>, <C-V>
            # for this the curses raw mode needs to be enabled
            # TODO: Error, when trying to input Emojis the cursor position is wrong
            # \_ Check this later, this is a low priority bug because no sane person would use emojis
            self._add(in_char)
        elif type(in_char) == int:
            #TODO: everything except backspace
            match in_char:
                case curses.KEY_DC | curses.KEY_BACKSPACE:
                    # Backspace Key
                    self._delete()
                 # TODO: Continue case 
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

        form_input = textfield(win, COLORS, "Test-String")

        for i in range(10):
            form_input.input(stdscr.get_wch())

    curses.wrapper(main)
