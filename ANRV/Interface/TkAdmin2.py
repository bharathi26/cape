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
import ANRV.Messages
from ANRV.System import  Identity
from ANRV.System.LoggableComponent import LoggableComponent

from Kamaelia.UI.Tk.TkWindow import TkWindow, tkInvisibleWindow

import Axon

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

from pprint import pprint

class TkAdmin2(TkWindow, LoggableComponent):
    def __init__(self):
        self.title = "ANRV TkAdmin - [%s]" % Identity.SystemName

        # The invisibleroot is necessary to avoid stopping Tk's eventloop
        # upon closure of tkWindows.
        # TODO: Good idea to already activate here?
        # TODO: Don't we need a central InvisibleWindow thats kept inbetween destruction of tkinterfaces?
        self._invisibleRoot = tkInvisibleWindow().activate()
#        self.clearInput = tkinter.BooleanVar()
        self.componentlist = {}

        super(TkAdmin2, self).__init__()

    def __on_ButtonClear_Press(self,Event=None):
        self.clearEntry() 

    def __on_ButtonTransmit_Release(self,Event=None):
        self.transmit()

    def __on_EntryInput_Enter__C(self,Event=None):
        self.transmit()

    def clearEntry(self):
        self.__EntryInput.delete(0,END)
        self.__FrameInput['bg'] = self.defaultcolors['bg']
#        self.__EntryInput['fg'] = self.defaultcolors['fg']

    def scanregistry(self):
        msg = ANRV.Messages.Message(sender=self.name, recipient=self.systemregistry, func="listRegisteredComponents", arg=None)
        self.send(msg, "outbox")

    def scancomponent(self, name):
        self.logdebug("Looking for component '%s'." % name)
        print(self.componentlist)
        if name in self.componentlist:
            self.loginfo("Scanning component '%s'." % name)
            msg = ANRV.Messages.Message(sender=self.name, recipient=name, func="getComponentInfo", arg=None)
            self.send(msg, "outbox")

    def transmit(self):
        message = self.__EntryInput.get()

        if len(message) <= 1:
            self.logdebug("No message to send entered.")
            return

        try:
            msg = jsonpickle.decode(message)
            if msg.sender != self.name:
                msg.sender = self.name
            self.loginfo("Transmitting message '%s'" % msg)
            self.send(msg, "outbox")
            self.__FrameInput['bg'] = self.defaultcolors['bg']
        except ValueError as e:
            errmsg = 'Invalid JSON:\n%s' % e
            print(e)
            if "column" in errmsg:
                col = errmsg.split("(char ")[1].split(")")[0]
                self.__EntryInput.icursor(col)
            self.logwarning(errmsg)
            self.__FrameInput['bg'] = 'red'
#            self.__FrameInput['fg'] = 'yellow'
            messagebox.showinfo("Transmit failed!", errmsg)

        if self.autoclear.get():
            self.clearEntry()

    def _handleMsg(self, msg):
        if isinstance(msg, ANRV.Messages.Message):
            if msg.sender == self.systemregistry:
                self.loginfo("Message from Registry: Method '%s'." % msg.func)
                if msg.func == "listRegisteredComponents":
                    self.loginfo("Got a list of registered components. Parsing.")
                    if isinstance(msg.arg, tuple):
                        success, result = msg.arg
                        if success:
                            for comp in result:
                                ComponentMenu = Menu(self.__MenuComponents)
                                ComponentMenu.add_command(label="Scan", command=lambda name=comp: self.scancomponent(name))
                                self.__MenuComponents.add_cascade(label=comp, menu=ComponentMenu)
                                self.componentlist[comp] = ComponentMenu
#                        self.__ComponentMenu.append(ComponentMenu)
            elif msg.func == "getComponentInfo":
                if isinstance(msg.arg, tuple):
                    success, result = msg.arg
                    if success:
                        if msg.sender not in self.componentlist:
                            if self.autoscan:
                                self.loginfo("Unknown component '%s'. Rescanning registry." % msg.sender)
                                self.scanregistry()
                            else:
                                self.loginfo("Unknown component's ('%s') info encountered. Ignoring.")
                        else:
                            self.loginfo("Got a component's ('%s') RPC info. Parsing." % msg.sender)
                            pprint(result)
                            for meth in result['methods']:
                                self.loginfo("Got method '%s'." % meth)
                                self.componentlist[msg.sender].add_command(label=meth)


    def _filteredMsg(self, msg):
        return False


    def quit(self):
        Axon.Scheduler.scheduler.run.stop()

    def setupWindow(self):
        self.logdebug("Setting up TkAdmin GUI")

        self.window.title(self.title)



#############################################################################################################
        self.__FrameMenu = Frame(self.window)
        self.__FrameMenu.pack(anchor='n',side='top')

        print(self.window.__dict__)
        self.__Menu = Menu(self.window)
        self.__MenuFile = Menu(self.__Menu)
        self.__MenuEdit = Menu(self.__Menu)
        self.__MenuComponents = Menu(self.__Menu)
        self.__Menu.add_cascade(menu=self.__MenuFile, label="File")
        self.__Menu.add_cascade(menu=self.__MenuEdit, label="Edit")
        self.__Menu.add_cascade(menu=self.__MenuComponents, label="Components")
        self.window.config(menu=self.__Menu)

        self.__MenuFile.add_command(label="Quit", command=self.quit)

        self.__MenuComponents.add_command(label="Scan", command=self.scanregistry)

        self.__FrameOutput = Frame(self.window)
        self.__FrameOutput.pack(side='top',fill='both',expand='yes')

        self.__FrameInput = Frame(self.window, borderwidth=2)
        self.__FrameInput.pack(anchor='s',expand='yes',fill='both',side='top')

        self.__FrameStatusbar = Frame(self.window, relief='raised')
        self.__FrameStatusbar.pack(anchor='sw',side='top') # ,fill='x'

        self.__LabelStatus = Label(self.__FrameStatusbar,text='Ready.')
        self.__LabelStatus.pack(anchor='w',expand='yes',side='top') # ,fill='both'

        self.__FrameResponses = Frame(self.__FrameOutput)
        self.__FrameResponses.pack(anchor='w',expand='yes',side='left')

        self.__LabelResponses = Label(self.__FrameResponses,text='Responses')
        self.__LabelResponses.pack(anchor='n',expand='yes',fill='x',side='top')

        self.__TextResponses = Text(self.__FrameResponses)
        self.__TextResponses.pack(side='top', expand='yes',fill='both')

        self.__FrameLog = Frame(self.__FrameOutput)
        self.__FrameLog.pack(anchor='e',side='left')

        self.__LabelLog = Label(self.__FrameLog,text='Log')
        self.__LabelLog.pack(anchor='n',expand='yes',fill='x',side='top')

        self.__TextLog = Text(self.__FrameLog)
        self.__TextLog.pack(expand='yes',fill='both',side='top')

        self.__FrameInputEntry = Frame(self.__FrameInput)
        self.__FrameInputEntry.pack(side='left')

        self.__LabelInput = Label(self.__FrameInputEntry,text='Input')
        self.__LabelInput.pack(anchor='w',expand='yes',fill='both',side='left')

        self.__Frame1 = Frame(self.__FrameInput)
        self.__Frame1.pack(expand='yes',fill='x',side='left')

        self.__EntryInput = Entry(self.__Frame1, foreground="white")
        self.__EntryInput.pack(expand='yes',fill='both',side='top')
        self.__EntryInput.bind('<Control-Return>',self.__on_EntryInput_Enter__C)

        self.__FrameTransmitButton = Frame(self.__FrameInput)
        self.__FrameTransmitButton.pack(anchor='w',side='left')

        self.__ButtonTransmit = Button(self.__FrameTransmitButton
            ,text='Transmit')
        self.__ButtonTransmit.pack(expand='yes',fill='both',side='top')
        self.__ButtonTransmit.bind('<ButtonRelease-1>' \
            ,self.__on_ButtonTransmit_Release)
        self.__FrameClearButton = Frame(self.__FrameInput)
        self.__FrameClearButton.pack(anchor='w',side='left')
        self.__ButtonClear = Button(self.__FrameClearButton,text='Clear')
        self.__ButtonClear.pack(expand='yes',fill='both',side='top')
        self.__ButtonClear.bind('<ButtonPress-1>',self.__on_ButtonClear_Press)
        self.__FrameAutoclear = Frame(self.__FrameInput)
        self.__FrameAutoclear.pack(anchor='w',side='left')
        self.autoclear = IntVar()
        self.__CheckbuttonAutoclear = Checkbutton(self.__FrameAutoclear
            ,borderwidth=0,text='Autoclear',variable=self.autoclear)
        self.__CheckbuttonAutoclear.pack(fill='both',side='top')



#############################################################################################################
#
#        self.window.geometry('640x480+10+10')
#        self.window.master.geometry('640x480+10+10')
#
#
#        self.frameOutput= tkinter.Frame(self.window)
#        self.labelOutput = tkinter.Label(self.frameOutput, text="System Output")
#        self.labelOutput.grid(row=0, column=0)
#        self.textboxOutput = tkinter.Text(self.frameOutput)
#        self.textboxOutput.grid(row=1, column=0, sticky=tkinter.E+tkinter.N+tkinter.W+tkinter.S)
#        self.frameOutput.grid(row=0, column=0, sticky=tkinter.W)
#
#        self.frameLog = tkinter.Frame(self.window)
#        self.labelLog = tkinter.Label(self.frameLog, text="Log")
#        self.labelLog.grid(row=0, column=0)
#        self.textboxLog = tkinter.Text(self.frameLog)
#        self.textboxLog.grid(row=1, column=0, sticky=tkinter.W+tkinter.N+tkinter.E+tkinter.S)
#        self.frameLog.grid(row=0, column=1, sticky=tkinter.E)
#
#
#        self.frameInput = tkinter.Frame(self.window)
#        self.textboxInput = tkinter.Text(self.frameInput)
#        self.textboxInput.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)
#        self.buttonsend = tkinter.Button(self.frameInput, text="Transmit", command=self.transmit)
#        self.buttonsend.grid(row=0, column=2, sticky=tkinter.E)
#        self.checkboxClear = tkinter.Checkbutton(self.frameInput, text="Clear", variable=self.clearInput)
#        self.checkboxClear.grid(row=0, column=3, sticky=tkinter.E)
#        self.frameInput.grid(row=1, column=0, columnspan=2, sticky=tkinter.E+tkinter.W+tkinter.S)
#
#        self.statusLabel = tkinter.Label(self.window, text="Ready.")
#        self.statusLabel.grid(row=3, column=0, columnspan=2, sticky=tkinter.W)
#



        #self.window.rowconfigure(0, weight=1)
        #self.window.columnconfigure(0, weight=1)

        self.defaultcolors = {'bg': self.window['bg'], 'fg': self.__EntryInput['fg']}

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
                self.logdebug("Received message '%s'" % msg)
                self._handleMsg(msg)
                if not self._filteredMsg(msg):
                    self.__TextResponses.insert(END, "%s\n" % msg)
            self.tkupdate()

Registry.ComponentTemplates['TkAdmin2'] = [TkAdmin2, "Simple Second revision Admin GUI providing message relaying and log viewing."]
