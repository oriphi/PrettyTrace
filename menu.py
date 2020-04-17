import shutil
import sys
import tty
from os import system


class MenuItem():
    def __init__(self, item, subItems = []):
        self.item = item
        self.sub = subItems
        self.w, self.h = shutil.get_terminal_size()
        self.collapsed = True
        self.selected = u"\u001b[1;30;43m{}\u001b[0m"
        self.parentSelected = u"\u001b[1;1;42m{}\u001b[0m"

    def isSelected(self, start = 0, selected = 0):
        if start == selected:
            return self
        if self.collapsed:
            return None
        start += 1
        for i in self.sub:
            r = i.isSelected(start, selected)
            start += len(i)
            if r:
                return r
        return None

    def toggle(self):
        self.collapsed = 1 - self.collapsed
        self.length = len(self)

    def __len__(self):
        res = 1
        if not(self.collapsed):
            for i in self.sub:
                res += len(i)
        return res

    def fullLength(self):
        res = 1
        for i in self.sub:
            res += i.fullLength()
        return res

    def print(self, prefix = "", start = 0, selected = 0):
        l = len(self)
        if (start == selected) or (self.collapsed and start <= selected < start + l):
            print(prefix + self.selected.format(self.item))
        else:
            print(prefix + self.item)
        if self.collapsed:
            return
        start += 1
        for i in self.sub:
            i.print(prefix + "  ", start, selected)
            start += len(i)

    def printLine(self,content):
        sys.stdout.write(content + '\r\n')
        sys.stdout.flush()

    def repr(self, prefix = "", start = 0, selected = 0, beg = 0, end = 0, parentSel = False):
        """
            prefix : indentation
            start : position of the first item of the menu
            beg: start of the window
            end: end of the window
            selected: selected item
            parentSel: is parent selected

        """
        a = len(self)
        if start >= end or start  + a< beg:
            # lines outside of the window
            return
        if (start == selected) :
            parentSel = True
            self.printLine(prefix + self.selected.format(self.item))
        else:

            if(parentSel):
                self.printLine(prefix + self.parentSelected.format(self.item))
            else:
                self.printLine(prefix + self.item)
        if self.collapsed:
            return
        start += 1
        for i in self.sub:
            i.repr(prefix = prefix + "  ",
                start = start,
                selected = selected,
                beg = beg,
                end = end,
                parentSel = parentSel)
            start += len(i)
            #self.printLine(prefix + "  len: {} -- Start: {}".format(i.length, start))
        return


class Menu():
    def __init__(self, items):
        self.items = items
        self.index = 0
        self.w,self.h = shutil.get_terminal_size()



        # Run the main loop
        self.mainloop()


    def printLine(self,content):
        sys.stdout.write(content)
        sys.stdout.flush()

    def clearScreen(self):
        self.printLine('\u001b[2J')
        self.printLine(u"\u001b[{}B".format(self.h))

    def length(self):
        l = 0
        for i in self.items:
            l += len(i)
        return l

    def printMenu(self):
        self.clearScreen()
        lines = []
        start = 0
        self.w, self.h = shutil.get_terminal_size()
        k = 0


        l = self.length()
        if(self.index < self.h // 2):
            beg = 0
            end = self.h

        elif(self.index > l - self.h // 2):
            end = l
            beg = end - self.h
        else:
            beg =  self.index - self.h // 2
            end =  self.index + self.h // 2
            if self.h % 2:
                end += 1

        with open("out","a") as f:
            f.write("beg: {} - end: {}\n".format(beg, end))

        for i in self.items:
            i.repr(prefix = "", start = k, selected = self.index,beg = beg, end = end, parentSel = False)
            k += len(i)


    def mainloop(self):
        tty.setraw(sys.stdin)
        c = "a"
        self.clearScreen()
        self.printMenu()
        while(ord(c) != 113):
            c = sys.stdin.read(1)
            if ord(c) == 3:
                break

            if ord(c) == 106:
                # j
                l = self.length()
                if self.index + 1 < l:
                    self.index += 1

            if ord(c) == 107:
                # j
                if self.index > 0:
                    self.index -= 1

            if ord(c) == 32:
                # Space
                r = None
                start = 0
                for i in self.items:
                    r = i.isSelected(start = start, selected = self.index)
                    if (r):
                        break
                    start += len(i)
                if(r):
                    r.toggle()

            self.clearScreen()
            self.printMenu()
        system("stty sane")


if __name__ == "__main__":
    N = 50
    import random


    def generateSubitem(depth, M = 5):
        res = []
        if depth == 0:
            for i in range(M):
                r = str(random.randint(0,100000000))
                res.append(MenuItem(r))
            return MenuItem(str(random.randint(0,10000000)), res)
        else:
            for i in range(M):
                res.append(generateSubitem(depth - 1))
            return MenuItem(str(random.randint(0,10000000)), res)

    res = [generateSubitem(3) for i in range(N)]
    menu = Menu(res)
