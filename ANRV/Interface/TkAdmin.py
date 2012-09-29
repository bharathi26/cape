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

# TODO:
# * Needs cleanup and standardization
# * Move RPCArgDialog out of this file

from ANRV.System import Registry
from ANRV.System import RPCComponent
import ANRV.Messages
from ANRV.System import  Identity
from ANRV.System.LoggableComponent import LoggableComponent
from ANRV.System.RPCComponent import RPCComponent

from ANRV.Interface.TkMapDialog import TkMapDialog
from ANRV.Interface.TkMessageDialog import TkMessageDialog

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
import json

from pprint import pprint


class TkRPCArgDialog(TkWindow, LoggableComponent):
    def __init__(self, parent, callback, componentname, methodname, methodinfo):
        # TODO:
        # * Clean up (ownerships etc)
        # * parsing of args and interaction with them (export etc)
        super(TkRPCArgDialog, self).__init__()

        argspec = methodinfo['args']
        doc = methodinfo['doc']

        title = "%s@%s" % (methodname, componentname)
        self.window.title(title)

        self.argspec = argspec
        self.callback = callback
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

        self._submitButton = Button(self._buttonFrame, text='Submit', command=self.send)
        self._closeButton = Button(self._buttonFrame, text='Close', command=self.close)
        self._submitButton.pack(side="left")
        self._closeButton.pack(side="right")

        self._buttonFrame.pack(side="bottom", fill="x", expand="yes")

    def send(self):
        arguments = {}

        for args in self.argEntries:
            self.logdebug("Checking '%s' against '%s'" % (args, self.argspec[args]))
            if self.argspec[args][0] == dict:
                arguments[args] = json.loads(self.argEntries[args]['Entry'].get())
            else:
                arguments[args] = self.argspec[args][0](self.argEntries[args]['Entry'].get())
        self.callback(self.componentname, self.methodname, arguments)

    def close(self):
        self.window.destroy()

class TkAdmin(TkWindow, RPCComponent):
    """
    Development graphical user interface for RAIN systems.
    """

    # TODO:
    # * Clean up user interface
    # * Develop interaction elements for all primitives

    def __init__(self):
        self.title = "ANRV TkAdmin - [%s]" % Identity.SystemName
        super(TkAdmin, self).__init__()

        self.Configuration['fixsender'] = False
        self.Configuration['autoclear'] = True
        self.Configuration['autoscan'] = True
        self.Configuration['showresponses'] = False

        self.autoscan.set(self.Configuration['autoscan'])
        self.fixsender.set(self.Configuration['fixsender'])
        self.autoclear.set(self.Configuration['autoclear'])
        self.showresponses.set(self.Configuration['showresponses'])

        # The invisibleroot is necessary to avoid stopping Tk's eventloop
        # upon closure of tkWindows.
        # TODO: Good idea to already activate here?
        # TODO: Don't we need a central InvisibleWindow thats kept inbetween destruction of tkinterfaces?
        self._invisibleRoot = tkInvisibleWindow().activate()
#        self.clearInput = tkinter.BooleanVar()
        self.componentlist = {}
        self.messages = []
        self.MapViewer = None

    def __on_ButtonClear_Press(self,Event=None):
        self.clearEntry() 

    def __on_ButtonTransmit_Release(self,Event=None):
        self.usertransmit()

    def __on_EntryInput_Enter__C(self,Event=None):
        self.usertransmit()

    def __on_ButtonClearResponses_Press(self,Event=None):
        self.__TextResponses.clear()

    def showMessage(self, ev):
        msglb = self.__MessageLog._listbox
        sel = msglb.curselection()
        if len(sel) > 1:
            self.logwarning("Multiple messages selected to display. Can't.")
        msg = self.messages[int(sel[0])]
        msgdialog = TkMessageDialog(self.window, msg)

    def clearEntry(self):
        self.__EntryInput.delete(0,END)
        self.__FrameInput['bg'] = self.defaultcolors['bg']
#        self.__EntryInput['fg'] = self.defaultcolors['fg']

    def scanregistry(self):
        msg = ANRV.Messages.Message(sender=self.name, recipient=self.systemregistry, func="listRegisteredComponents", arg=None)
        self.transmit(msg)

    def scancomponent(self, name):
        self.loginfo("Scanning component '%s'." % name)
        msg = ANRV.Messages.Message(sender=self.name, recipient=name, func="getComponentInfo", arg=None)
        self.transmit(msg)

    def callComplexMethod(self, componentname, func):
        self.loginfo("Creating function dialog for '%s'@'%s'." % (func, componentname))
        methodregister = self.componentlist[componentname]["info"]["methods"][func]
        InputDialog = TkRPCArgDialog(self.window, self.callComplexMethodFinal, componentname, func, methodregister)

    def callComplexMethodFinal(self, name, func, args):
        self.loginfo("Finally calling func '%s'@'%s' with args '%s'" % (func, name, args))
        msg = ANRV.Messages.Message(sender=self.name, recipient=name, func=func, arg=args)
        self.transmit(msg)

    def callSimpleMethod(self, name, func):
        self.loginfo("Calling '%s'@'%s'." % (func, name))
        msg = ANRV.Messages.Message(sender=self.name, recipient=name, func=func, arg=None)
        self.transmit(msg)

    def transmit(self, msg):
        self.recordMessage(msg)
        self.send(msg, "outbox")

    def recordMessage(self, msg):
        self.messages.append(msg)
        self.updateMessageLog()

    def updateMessageLog(self):
        loglistbox = self.__MessageLog._listbox
        loglistbox.delete(0,END) # GAH. Addition should be sufficient. CHANGE!

        for msg in sorted(self.messages, key=lambda msg: msg.timestamp):
            loglistbox.insert(END,msg)
            if msg.recipient == self.name:
                loglistbox.itemconfig(END, bg='green',fg='black')
            else:
                loglistbox.itemconfig(END, bg='red',fg='black')

    def usertransmit(self):
        def send(msg):
            if self.fixsender.get() and msg.sender != self.name:
                self.loginfo("Fixing sender to '%s'." % self.name)
                msg.sender = self.name
            self.loginfo("Transmitting message '%s'" % msg)
            self.transmit(msg)
            self.__FrameInput['bg'] = self.defaultcolors['bg']

        message = self.__EntryInput.get()

        if len(message) <= 1:
            self.logdebug("No message to send entered.")
            return

        try:
            msg = jsonpickle.decode(message)
            send(msg)
        except ValueError as e:
            errmsg = 'Invalid JSON:\n%s' % e
            self.logerror(e)
            if "column" in errmsg:
                col = errmsg.split("(char ")[1].split(")")[0]
                col = col.split(" -")[0]
                self.__EntryInput.icursor(col)
            self.logwarning(errmsg)
            self.__FrameInput['bg'] = 'red'
#            self.__FrameInput['fg'] = 'yellow'
            messagebox.showinfo("Transmit failed!", errmsg)

        if self.autoclear.get():
            self.clearEntry()


    def _handleMsg(self, msg):
        self.recordMessage(msg)

        def __handleComponentInfo(msg):
            if msg.sender not in self.componentlist:
                if self.autoscan.get():
                    self.loginfo("Unknown component '%s'. Rescanning registry." % msg.sender)
                    self.scanregistry()
                else:
                    self.loginfo("Unknown component's ('%s') info encountered. Ignoring.")
            else:
                self.loginfo("Got a component's ('%s') RPC info. Parsing." % msg.sender)
                #pprint(result)

                success, result = msg.arg
                comp = msg.sender

                self.componentlist[comp]["info"] = result
                MenuSubComponent = self.componentlist[comp]["Menu"]
                MenuSubComponent.delete(3, END)

                mr = result['methods']

                for meth in mr:
                    self.logdebug("Got method '%s'." % meth)
                    if len(mr[meth]['args']) > 0:
                        MenuSubComponent.add_command(label=meth, command=lambda (name,meth)=(comp,meth): self.callComplexMethod(name,meth))
                    else:
                        MenuSubComponent.add_command(label=meth, command=lambda (name,meth)=(comp,meth): self.callSimpleMethod(name,meth))

        def __handleRegisteredComponents(msg):
           self.loginfo("Got a list of registered components. Parsing.")
           success, result = msg.arg
           self.componentlist = {}
           self.__MenuComponents.delete(4,END)
           for comp in result:
               if self.autoscan.get() and comp not in self.componentlist:
                   self.scancomponent(comp)
               MenuSubComponent = Menu(self.__MenuComponents)
               MenuSubComponent.add_command(label="Scan", command=lambda name=comp: self.scancomponent(name))
               MenuSubComponent.add_separator()

               self.__MenuComponents.add_cascade(label=comp, menu=MenuSubComponent)
               self.componentlist[comp] = {"Menu": MenuSubComponent, "info": None}


        if isinstance(msg, ANRV.Messages.Message):
            if msg.sender == self.systemregistry:
                if msg.func == "listRegisteredComponents":
                    if isinstance(msg.arg, tuple):
                        success, result = msg.arg
                        if success:
                            __handleRegisteredComponents(msg)
            if msg.func == "getComponentInfo":
                if isinstance(msg.arg, tuple):
                    success, result = msg.arg
                    if success:
                        __handleComponentInfo(msg)
            if msg.func in ("renderArea", "renderCoord"):
                if isinstance(msg.arg, tuple):
                    success, result = msg.arg
                    if success:
                        if self.MapViewer:
                            self.MapViewer.drawMap(result)
                        else:
                            self.MapViewer = TkMapDialog(result)
                            self.MapViewer.activate()

    def scanlinetest(self):
        polygon = [[50,5],[100,270],[150,270],[220,30]]
        ScanlineTestDialog = TkScanlineTestDialog(polygon)

    def quit(self):
        Axon.Scheduler.scheduler.run.stop()

    def setupWindow(self):
        self.logdebug("Setting up TkAdmin GUI")

        import Pmw
        Pmw.initialise(self.window)

        self.window.title(self.title)


        ### Menu ###
        self.__FrameMenu = Frame(self.window)
        self.__FrameMenu.pack(anchor='n',side='top')

        self.__Menu = Menu(self.window)
        self.__MenuFile = Menu(self.__Menu)
        self.__MenuEdit = Menu(self.__Menu)
        self.__MenuSettings = Menu(self.__Menu)
        self.__Menu.add_cascade(menu=self.__MenuFile, label="File")
        self.__Menu.add_cascade(menu=self.__MenuEdit, label="Edit")
        self.__Menu.add_cascade(menu=self.__MenuSettings, label="Settings")
        self.window.config(menu=self.__Menu)

        self.__MenuFile.add_command(label="Update Message Log", command=self.updateMessageLog)
        self.__MenuFile.add_command(label="Quit", command=self.quit)

        self.autoscan = BooleanVar()
        self.fixsender = BooleanVar()
        self.autoclear = BooleanVar()
        self.showresponses = BooleanVar()

        self.__MenuSettings.add_checkbutton(label="Fix sender", onvalue=True, offvalue=False, variable=self.fixsender)
        self.__MenuSettings.add_checkbutton(label="Autoscan", onvalue=True, offvalue=False, variable=self.autoscan)
        self.__MenuSettings.add_checkbutton(label="Autoclear", onvalue=True, offvalue=False, variable=self.autoclear)
        self.__MenuSettings.add_checkbutton(label="Show responses", onvalue=True, offvalue=False, variable=self.showresponses)

        self.__MenuComponents = Menu(self.__Menu)
        self.__MenuComponents.add_command(label="Scan", command=self.scanregistry)
        self.__MenuComponents.add_separator()

        self.__Menu.add_cascade(menu=self.__MenuComponents, label="Components")


        ### /Menu ###

        ### Output ###

        self.__FrameOutput = Frame(self.window)
        self.__FrameOutput.pack(side='top',fill='both',expand='yes')

        self.__NotebookOutput = Pmw.NoteBook(self.__FrameOutput)
        self.__NotebookOutput.pack(fill='both', expand=1)

        self.__PageMessages = self.__NotebookOutput.add('Messages')
        self.__PageMap = self.__NotebookOutput.add('Map')
        self.__PageResponses = self.__NotebookOutput.add('Responses')
        #self.__PageLog = self.__NotebookOutput.add('Log') # Needs a loggercomponent and revised logging first

        self.__MessageLog = Pmw.ScrolledListBox(self.__PageMessages)
        self.__MessageLog.pack(expand='yes', fill='both')

        self.__NotebookOutput.tab('Messages').focus_set()

        self.__FrameInput = Frame(self.window, borderwidth=2)
        self.__FrameInput.pack(anchor='s',expand='no',fill='x',side='top')

        self.__FrameStatusbar = Frame(self.window, relief='raised')
        self.__FrameStatusbar.pack(anchor='sw',side='top') # ,fill='x'

        self.__LabelStatus = Label(self.__FrameStatusbar,text='Ready.')
        self.__LabelStatus.pack(anchor='w',expand='yes',side='top') # ,fill='both'

        self.__FrameResponses = Frame(self.__PageResponses, background="yellow")

        self.__FrameResponsesHeader = Frame(self.__FrameResponses)

        self.__LabelResponses = Label(self.__FrameResponsesHeader,text='Responses')
        self.__LabelResponses.pack(anchor='e',side='right', fill='x')

        self.__ButtonClearResponses = Button(self.__FrameResponsesHeader, text='Clear')
        self.__ButtonClearResponses.pack(anchor='w',side='left')

        self.__FrameResponsesHeader.pack(anchor='n', fill='x', side=TOP)

        self.__TextResponses = Pmw.ScrolledText(self.__FrameResponses)
        self.__TextResponses.pack(expand=1, fill='both', side=BOTTOM)

        self.__FrameResponses.pack(expand=1, fill="both")

        #self.__FrameLog = Frame(self.__PageLog)
        #self.__FrameLog.pack(side='left', expand=1, fill="both")

        #self.__FrameLogHeader = Frame(self.__FrameLog)
        #self.__FrameLogHeader.pack(anchor='n',expand='yes', fill='x', side='top')

        #self.__LabelLog = Label(self.__FrameLogHeader,text='Log')
        #self.__LabelLog.pack(anchor='e',side='right', fill='both')

        #self.__ButtonClearLog = Button(self.__FrameLogHeader, text='Clear')
        #self.__ButtonClearLog.pack(anchor='w',side='left')

        #self.__TextLog = Pmw.ScrolledText(self.__FrameLog)
        #self.__TextLog.pack(expand=1,fill='both')

        self.__MapCanvas = Canvas(self.__PageMap)
        self.__MapCanvas.pack(expand=1, fill='both')

        self.__NotebookOutput.setnaturalsize()

        ### /Output ###

        ### Input ###

        self.__FrameInputEntry = Frame(self.__FrameInput)

        self.__EntryInput = Entry(self.__FrameInput)
        self.__EntryInput.pack(expand='yes',fill='both',side='left')

        self.__FrameTransmitButton = Frame(self.__FrameInput)
        self.__FrameTransmitButton.pack(anchor='w',side='left')

        self.__ButtonTransmit = Button(self.__FrameTransmitButton
            ,text='Transmit')
        self.__ButtonTransmit.pack(expand='yes',fill='both',side='top')
        self.__FrameClearButton = Frame(self.__FrameInput)
        self.__FrameClearButton.pack(anchor='w',side='left')
        self.__ButtonClear = Button(self.__FrameClearButton,text='Clear')
        self.__ButtonClear.pack(expand='yes',fill='both',side='top')

        self.__FrameInputEntry.pack(side='left')

        ### /Input ###

        ### Bindings ###

        self.__MessageLog._listbox.bind("<Double-Button-1>", self.showMessage)
        self.__ButtonClearResponses.bind('<ButtonRelease-1>' \
            ,self.__on_ButtonClearResponses_Press)
        self.__ButtonTransmit.bind('<ButtonRelease-1>' \
            ,self.__on_ButtonTransmit_Release)
        self.__ButtonClear.bind('<ButtonPress-1>',self.__on_ButtonClear_Press)
        self.__EntryInput.bind('<Control-Return>',self.__on_EntryInput_Enter__C)


        self.defaultcolors = {'bg': self.window['bg'], 'fg': self.__EntryInput['fg']}

    def main(self):
        """  
        Main loop. Stub method, reimplement with your own functionality.

        Must regularly call self.tkupdate() to ensure tk event processing happens.
        """

        if self.autoscan.get():
            self.scanregistry()

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
                if self.showresponses.get():
                    self.__TextResponses.insert(END, "%s\n" % msg)
            self.tkupdate()

Registry.ComponentTemplates['TkAdmin'] = [TkAdmin, "Simple Second revision Admin GUI providing message relaying and log viewing."]
