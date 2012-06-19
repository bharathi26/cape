#!/usr/bin/python
# -*- coding: utf-8 -*-
#

if __name__ == "__main__":
    from Axon.Scheduler import scheduler
    from Kamaelia.UI.Tk.TkWindow import TkWindow
    import Tkinter
    from Tkinter import *

    class JSONClientWindow(TkWindow):
        def __init__(self, title):
            self.title = title
            super(JSONClientWindow,self).__init__()

        def setupWindow(self):
            self.label = Label(self.window, text=self.text)

            self.window.title(self.title)

            self.label.grid(row=0, column=0, sticky=Tkinter.N+Tkinter.E+Tkinter.W+Tkinter.S)
            self.window.rowconfigure(0, weight=1)
            self.window.columnconfigure(0, weight=1)

    my = JSONClientWindow("JSON Client").activate()
    
    scheduler.run.runThreads(slowmo=0)
    
