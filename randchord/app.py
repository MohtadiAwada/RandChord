import curses
import random
import json, sys, os
from .soundsys import Music

class Root:
    def __init__(self, filename=None):
        PACKAGE_DIR = os.path.dirname(__file__)
        with open(os.path.join(PACKAGE_DIR, "chords.json"), "r") as chords_file:
            self.chords = json.load(chords_file)
        self.CMDS = {
            curses.KEY_DOWN: self.scrollDown,
            curses.KEY_UP: self.scrollUp,
            14: self.newRand,
            18: self.playRand,
            1: self.appendRand,
            16: self.playSlc,
            23: self.saveTable,
        }
        self.table = []
        self.ltable = []
        self.selected = 0
        self.pos = 0
        self.random = "None"
        self.lrandom = []
        self.run = True
        self.music = Music()
        if filename: self.loadTable(filename)
        with open("err.log", "w") as err_file:
            sys.stderr = err_file
            curses.wrapper(self.main)
        sys.stderr = sys.__stderr__

    def main(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        self.stdscr.clear()
        try:
            while self.run:
                self.stdscr.erase()
                self.showContent()
                self.waitForAndApplyCmd()
        except Exception as e:
            curses.endwin()
            print(f"Error: {e}")
            raise

    def showContent(self):
        TITLE = "RandChords 1.0"
        self.height, width = self.stdscr.getmaxyx()
        #HEADER
        self.stdscr.addstr(0, 0, " " * width, curses.A_REVERSE)
        self.stdscr.addstr(0, (width-len(TITLE))//2, TITLE, curses.A_REVERSE)
        #TABLE
        self.showTable()
        #RANDOM
        random_lbl = "Random:"
        self.stdscr.addstr(self.height-6, 0, "-"*width)
        self.stdscr.addstr(self.height-5, 1, random_lbl)
        self.stdscr.addstr(self.height-5, 2+len(random_lbl), self.random)
        #FOOTER
        self.stdscr.addstr(self.height-4, 0, "━" * width)
        self.stdscr.addstr(self.height-3, (0*((width-2)//4))+1, "Quit: Ctrl+C")
        self.stdscr.addstr(self.height-3, (1*((width-2)//4))+1, "New Rand: Ctrl+N")
        self.stdscr.addstr(self.height-3, (2*((width-2)//4))+1, "Play Rand: Ctrl+R")
        self.stdscr.addstr(self.height-3, (3*((width-2)//4))+1, "Add Rand: Ctrl+A")
        self.stdscr.addstr(self.height-2, (0*((width-2)//4))+1, "Play Slt: Ctrl+P")
        self.stdscr.addstr(self.height-2, (1*((width-2)//4))+1, "Save Table: Ctrl+W")
        self.stdscr.refresh()

    def waitForAndApplyCmd(self):
        try:
            key = self.stdscr.getch()
            cmd = self.CMDS.get(key)
            if cmd: cmd()
        except KeyboardInterrupt: self.run = False

    def showTable(self):
        for i in range(1, min(len(self.table), self.height-7)+1):
            if i-1 + self.pos < len(self.table):
                if i-1 + self.pos == self.selected: self.stdscr.addstr(i, 1, str(self.table[(i-1) + self.pos]), curses.A_REVERSE)
                else: self.stdscr.addstr(i, 1, str(self.table[(i-1) + self.pos]))

    def promptInput(self, label):
        """
        Clears row height-5 and collects a string from the user there.
        Supports normal typing, backspace, Enter to confirm, Escape to cancel.
        Returns the entered string, or None if cancelled.
        """
        _, width = self.stdscr.getmaxyx()
        row = self.height - 5
        buf = ""

        curses.curs_set(1)
        while True:
            # Clear the row and redraw prompt + current buffer
            self.stdscr.move(row, 0)
            self.stdscr.clrtoeol()
            prompt = f"{label}{buf}"
            self.stdscr.addstr(row, 1, prompt)
            self.stdscr.move(row, 1 + len(prompt))
            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key in (curses.KEY_ENTER, 10, 13):   # Enter — confirm
                break
            elif key == 27:                          # Escape — cancel
                buf = None
                break
            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                buf = buf[:-1]
            elif 32 <= key <= 126:                   # Printable ASCII
                buf += chr(key)

        curses.curs_set(0)
        return buf

    #COMMANDS
    def scrollDown(self):
        self.selected = min(self.selected+1, len(self.table)-1)
        if self.selected > self.pos + self.height - 8:
            self.pos += 1

    def scrollUp(self):
        self.selected = max(self.selected-1, 0)
        if self.selected < self.pos: self.pos -= 1

    def newRand(self):
        rand_choices = []
        for i in range(4): rand_choices.append(random.choice(self.chords))
        rand = " | ".join(rand_choices)
        self.random = rand
        self.lrandom = rand_choices
        self.stdscr.erase()
        self.showContent()
        self.playRand()

    def appendRand(self):
        if self.random != "None":
            self.table.append(self.random)
            self.ltable.append(self.lrandom)
        self.selected = len(self.table)
        self.scrollDown()

    def playRand(self):
        self.music.playProg(self.lrandom)

    def playSlc(self):
        self.music.playProg(self.ltable[self.selected])

    def saveTable(self):
        filename = self.promptInput("Save as: ")
        if not filename:
            return
        if "." not in filename:
            filename += ".crdprog"
        with open(filename, "w") as f:
            for prog in self.table:
                f.write(prog + "\n")
    
    def loadTable(self, filename):
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.table.append(line)
                        self.ltable.append(line.split(" | "))
        except FileNotFoundError:
            pass   # just start empty if file doesn't exist

if __name__ == "__main__":
    root = Root()