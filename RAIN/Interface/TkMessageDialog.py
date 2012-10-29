#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      - Tk Admin Interface Message Dialog
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

import RAIN.Messages
from RAIN.System.LoggableComponent import LoggableComponent


from Kamaelia.UI.Tk.TkWindow import TkWindow, tkInvisibleWindow

try:
    unicode
    from Tkinter import * #as tkinter
    import tkMessageBox as messagebox
    import Pmw
except NameError:
    import tkinter
    from tkinter import *
    import tkinter.messagebox as messagebox

import jsonpickle
import json

class TkMessageDialog(TkWindow, LoggableComponent):
    def __init__(self, parent, msg):
        # TODO:
        # * interaction!
        # * integrate TkArgsDialog
        top = self.top = Toplevel(parent)
        self.msg = msg

        self.messageFrame = fr = Frame(top)
        self._textTimestamp = Pmw.ScrolledText(fr, label_text="Timestamp", labelpos="w")
        self._textTimestamp._textbox.config(height=1)
        self._textTimestamp.settext(msg.timestamp)
        self._textTimestamp.pack(fill=X)

        self._textSender = Pmw.ScrolledText(fr, label_text="Sender", labelpos="w")
        self._textSender._textbox.config(height=1)
        self._textSender.settext(msg.sender)
        self._textSender.pack(fill=X)

        self._textRecipient = Pmw.ScrolledText(fr, label_text="Recipient", labelpos="w")
        self._textRecipient._textbox.config(height=1)
        self._textRecipient.settext(msg.recipient)
        self._textRecipient.pack(fill=X)

        self._textFunc = Pmw.ScrolledText(fr, label_text="Function", labelpos="w")
        self._textFunc._textbox.config(height=1)
        self._textFunc.settext(msg.func)
        self._textFunc.pack(fill=X)

        self._textArg = Pmw.ScrolledText(fr, label_text="Arguments", labelpos="n")
        argstring = str(msg.arg)
        if len(argstring) < 2000:
            self._textArg._textbox.insert(END, argstring)
        else:
            self._textArg._textbox.insert(END, "Too large to display (%i characters)." % len(argstring))
        self._textArg.pack(expand=1, fill=BOTH)

        self.messageFrame.pack(side=TOP, expand=1, fill=BOTH)

        self.buttonFrame = fr = Frame(top)
        self._buttonClose = Button(fr, text="Close")
        self._buttonClose.pack(side=RIGHT)

        self._buttonCopy = Button(fr, text="Copy JSON")
        self._buttonCopy.pack(side=LEFT)

        self._buttonCopy.bind('<ButtonRelease-1>' \
                    ,self.__on_buttonCopy_Release)
        self._buttonClose.bind('<ButtonRelease-1>' \
                    ,self.__on_buttonClose_Release)

        self.buttonFrame.pack(side=BOTTOM, fill=X)

    def __on_buttonCopy_Release(self, Event=None):
        self.top.clipboard_clear()
        text = self.msg.jsonencode()
        text = text.encode("UTF-8")
        self.top.clipboard_append(text, type="STRING")
        pass

    def __on_buttonClose_Release(self, Event=None):
        self.top.destroy()

