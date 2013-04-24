#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#     - Interface.TkRPCArgDialog
#    Copyright (C) 2011-2012  riot <riot@hackerfleet.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from cape.system.loggablecomponent import LoggableComponent

from Kamaelia.UI.Tk.TkWindow import TkWindow

from Tkinter import Frame, Label, Entry, Button

import json


class TkRPCArgDialog(TkWindow, LoggableComponent):
    def __init__(self, parent, callback, componentname, node, methodname, methodinfo):
        # TODO:
        # * Clean up (ownerships etc)
        # * parsing of args and interaction with them (export etc)
        super(TkRPCArgDialog, self).__init__()

        argspec = methodinfo['args']
        doc = methodinfo['doc']

        title = "%s@%s:%s" % (componentname, node, methodname)
        self.window.title(title)

        self.argspec = argspec
        self.callback = callback
        self.node = node
        self.componentname = componentname
        self.methodname = methodname

        self._methFrame = Frame(self.window)
        self._methLabel = Label(self._methFrame, text=title)
        self._methLabel.pack(fill='x', expand='yes', side='top')
        self._methDoc = Label(self._methFrame, text=doc)
        self._methDoc.pack(fill='x', expand='yes', side='bottom')
        self._methFrame.pack(fill='x', expand='yes', side='top')

        self.argEntries = {}
        self.argDocs = {}
        self._argsFrame = Frame(self.window)

        for arg in argspec:
            argFrame = Frame(self._argsFrame)
            argDocFrame = Frame(argFrame)
            argDoc = Label(argDocFrame, text=argspec[arg][1], height=3)
            argDoc.pack(fill='x', side="left")
            argDocFrame.pack(fill="x", expand="yes")

            argEntry = Entry(argFrame)
            #argEntry._textbox.config(height=1)
            argEntry.pack(fill='x', expand="yes", side="right")
            argLabel = Label(argFrame, text="%s (%s)" % (arg, argspec[arg][0].__name__))
            argLabel.pack(side='left')
            argFrame.pack(fill='x', expand='yes')

            self.argEntries[arg] = {'Frame': argFrame, 'Entry': argEntry, 'Doc': argDoc}

        self._argsFrame.pack(expand='yes', fill='both', side="top")

        self._buttonFrame = Frame(self.window)

        self._submitButton = Button(self._buttonFrame, text='Submit', command=self.transmit)
        self._closeButton = Button(self._buttonFrame, text='Close', command=self.close)
        self._submitButton.pack(side="left")
        self._closeButton.pack(side="right")

        self._buttonFrame.pack(side="bottom", fill="x", expand="yes")

    def transmit(self):
        arguments = {}

        for args in self.argEntries:
            self.logdebug("Checking '%s' against '%s'" % (args, self.argspec[args]))
            # TODO: There's a bug here, that prevents bools and probably a lot of other stuff from
            # being parsed correctly.
            if self.argspec[args][0] == dict:
                arguments[args] = json.loads(self.argEntries[args]['Entry'].get())
            else:
                arguments[args] = self.argspec[args][0](self.argEntries[args]['Entry'].get())
        self.callback(self.componentname, self.node, self.methodname, arguments)

    def close(self):
        self.window.destroy()

