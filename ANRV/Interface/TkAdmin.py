#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#      - Tk Admin Interface (providing Message relaying and log display)
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

from ANRV.System import Registry
from ANRV.System import RPCComponent
from ANRV.Messages import Message
from ANRV.System import  Identity
from ANRV.System.LoggableComponent import LoggableComponent

from Kamaelia.UI.Tk.TkWindow import TkWindow, tkInvisibleWindow

import tkinter
import tkinter.messagebox

import jsonpickle

class TkAdmin(TkWindow, LoggableComponent):
    def __init__(self):
        self.title = "ANRV TkAdmin - [%s]" % Identity.SystemName

        # The invisibleroot is necessary to avoid stopping Tk's eventloop
        # upon closure of tkWindows.
        # TODO: Good idea to already activate here?
        # TODO: Don't we need a central InvisibleWindow thats kept inbetween destruction of tkinterfaces?
        self._invisibleRoot = tkInvisibleWindow().activate()
        self.clearInput = tkinter.BooleanVar()
        super(TkAdmin, self).__init__()


    def setupWindow(self):
        self.logdebug("Setting up TkAdmin GUI")
        self.window.geometry('640x480+10+10')
        self.window.master.geometry('640x480+10+10')


        self.frameOutput= tkinter.Frame(self.window)
        self.labelOutput = tkinter.Label(self.frameOutput, text="System Output")
        self.labelOutput.grid(row=0, column=0)
        self.textboxOutput = tkinter.Text(self.frameOutput)
        self.textboxOutput.grid(row=1, column=0, sticky=tkinter.E+tkinter.N+tkinter.W+tkinter.S)
        self.frameOutput.grid(row=0, column=0, sticky=tkinter.W)

        self.frameLog = tkinter.Frame(self.window)
        self.labelLog = tkinter.Label(self.frameLog, text="Log")
        self.labelLog.grid(row=0, column=0)
        self.textboxLog = tkinter.Text(self.frameLog)
        self.textboxLog.grid(row=1, column=0, sticky=tkinter.W+tkinter.N+tkinter.E+tkinter.S)
        self.frameLog.grid(row=0, column=1, sticky=tkinter.E)


        self.frameInput = tkinter.Frame(self.window)
        self.textboxInput = tkinter.Text(self.frameInput)
        self.textboxInput.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)
        self.buttonsend = tkinter.Button(self.frameInput, text="Transmit", command=self.transmit)
        self.buttonsend.grid(row=0, column=2, sticky=tkinter.E)
        self.checkboxClear = tkinter.Checkbutton(self.frameInput, text="Clear", variable=self.clearInput)
        self.checkboxClear.grid(row=0, column=3, sticky=tkinter.E)
        self.frameInput.grid(row=1, column=0, columnspan=2, sticky=tkinter.E+tkinter.W+tkinter.S)

        self.statusLabel = tkinter.Label(self.window, text="Ready.")
        self.statusLabel.grid(row=3, column=0, columnspan=2, sticky=tkinter.W)

        self.window.title(self.title)

        self.defaultcolors = {'bg': self.window['bg'], 'fg': self.textboxInput['fg']}


        #self.window.rowconfigure(0, weight=1)
        #self.window.columnconfigure(0, weight=1)

    def transmit(self):
        message = self.textboxInput.get("1.0", tkinter.END)

        if len(message) <= 1:
            self.logdebug("No message to send entered.")
            return

        try:
            msg = jsonpickle.decode(message)
            if msg.sender != self.name:
                msg.sender = self.name
            self.loginfo("Transmitting message '%s'" % msg)
            self.send(msg, "outbox")
        except ValueError as e:
            errmsg = 'Invalid JSON:\n%s' % e
            self.logwarning(errmsg)
            self.textboxInput['bg'] = 'red'
            self.textboxInput['fg'] = 'yellow'
            tkinter.messagebox.showinfo("Transmit failed!", errmsg)

        if self.clearInput.get():
            self.textboxInput.delete('1.0', tkinter.END)
            self.textboxInput['bg'] = self.defaultcolors['bg']
            self.textboxInput['fg'] = self.defaultcolors['fg']

    def main(self):
        """  
        Main loop. Stub method, reimplement with your own functionality.

        Must regularly call self.tkupdate() to ensure tk event processing happens.
        """
        while not self.isDestroyed():
            yield 1
            if self.dataReady("control"):
                msg = self.recv("control")
                if isinstance(msg, producerFinished) or isinstance(msg, shutdownMicroprocess):
                    self.send(msg, "signal")
                    self.window.destroy()
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                self.logdebug("RECEIVED MESSAGE: %s" % msg)
                self.textboxOutput.insert(tkinter.END, msg)
            self.tkupdate()

Registry.ComponentTemplates['TkAdmin'] = [TkAdmin, "Simple Admin GUI providing message relaying and log viewing."]
