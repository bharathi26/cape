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
from ANRV.System.RPCComponent import RPCComponent
from ANRV.Interface.TkMapDialog import TkMapDialog

from Kamaelia.UI.Tk.TkWindow import TkWindow, tkInvisibleWindow

import Axon

import PIL
import PIL.Image
import PIL.ImageTk
import mapnik2 as mapnik

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


class TkMessageDialog(TkWindow, LoggableComponent):
    def __init__(self, parent, msg):
        # TODO:
        # * interaction!
        # * integrate TkArgsDialog
        top = self.top = Toplevel(parent)
        self.msg = msg

        self.frame = fr = Frame(top)
        self._labelTimestamp = Label(fr, text=msg.timestamp)
        self._labelTimestamp.pack()

        self._labelSender = Label(fr, text=msg.sender)
        self._labelSender.pack()

        self._labelRecipient = Label(fr, text=msg.recipient)
        self._labelRecipient.pack()

        self._labelFunc = Label(fr, text=msg.func)
        self._labelFunc.pack()

        self._labelArg = Label(fr, text=msg.arg)
        self._labelArg.pack()

        fr.pack()

class TkRPCArgDialog(TkWindow, LoggableComponent):
    def __init__(self, parent, callback, argspec, compname, compfunc):
        # TODO:
        # * Clean up (ownerships etc)
        # * parsing of args and interaction with them (export etc)
        super(TkRPCArgDialog, self).__init__()

        self.argspec = argspec
        self.callback = callback
        self.compname = compname
        self.compfunc = compfunc
        self.argFrames = self.argLabels = self.argEntrys = {}

        for arg in argspec:
            frame = Frame(self.window)
            myLabel = Label(frame, text="%s (%s)" % (arg, argspec[arg][0]))
            myLabel.pack(side="left")

            myEntryBox = Entry(frame)
            myEntryBox.pack(side="right", anchor="e")
            self.argFrames[arg] = frame
            self.argLabels[arg] = myLabel
            self.argEntrys[arg] = myEntryBox

            frame.pack()

        self.mySubmitButton = Button(self.window, text='Submit', command=self.send)
        self.mySubmitButton.pack()

    def send(self):
        arguments = {}
        for args in self.argEntrys:
            self.logdebug("Checking '%s' against '%s'" % (args, self.argspec[args]))
            if self.argspec[args][0] == dict:
                arguments[args] = json.loads(self.argEntrys[args].get())
            else:
                arguments[args] = self.argspec[args][0](self.argEntrys[args].get())
        if len(arguments) == 1:
            arguments = arguments['default']
        self.callback(self.compname, self.compfunc, arguments)
        self.window.destroy()



class TkAdmin2(TkWindow, RPCComponent):
    """
    Development graphical user interface for RAIN systems.
    """

    # TODO:
    # * Clean up user interface
    # * Develop interaction elements for all primitives

    def __init__(self):
        self.title = "ANRV TkAdmin - [%s]" % Identity.SystemName

        # The invisibleroot is necessary to avoid stopping Tk's eventloop
        # upon closure of tkWindows.
        # TODO: Good idea to already activate here?
        # TODO: Don't we need a central InvisibleWindow thats kept inbetween destruction of tkinterfaces?
        self._invisibleRoot = tkInvisibleWindow().activate()
#        self.clearInput = tkinter.BooleanVar()
        self.componentlist = {}
        self.messages = []
        self.MapViewer = None

        super(TkAdmin2, self).__init__()

    def __on_ButtonClear_Press(self,Event=None):
        self.clearEntry() 

    def __on_ButtonTransmit_Release(self,Event=None):
        self.transmit()

    def __on_EntryInput_Enter__C(self,Event=None):
        self.transmit()

    def showMessage(self, ev):
        msglb = self.__MessageLog._listbox
        sel = msglb.curselection()
        if len(sel) > 1:
            self.logwarning("Multiple messages selected to display. Can't.")
        msg = self.messages[int(sel[0])]
        msgdialog = TkMessageDialog(self.window, msg)

    def showHistory(self):
        # TODO:
        # * delete me, messages tab is way more powerful already
        print(self.messages)
        self.HistoryDialog = Pmw.ComboBoxDialog(self.window,
            title = 'Message History',
            buttons = ('OK', 'Cancel'),
            defaultbutton = 'OK',
            combobox_labelpos = 'n',
            label_text = 'Previously sent messages:',
            scrolledlist_items = self.messages,
            command=self.sendPickedHistory)
#        for item in self.messages:
#            self.HistoryDialog.scrolledlist.insert(END, item)
#        self.dialog.withdraw()


#        print(result)

    def sendPickedHistory(self, ev):
        # TODO: Integrate with TkMessageDialog
        if ev == 'Cancel':
            self.HistoryDialog.destroy()
        if ev == 'OK':
            message = self.HistoryDialog.get()
            try:
                self.transmit(jsonpickle.decode(message))
            except:
                print("Couldn't decode message from history: '%s'" % message)



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

    def callComplexMethod(self, name, func, argspec):
        self.loginfo("Preparing call to '%s'@'%s'. with %i args" % (func, name, len(argspec)))
        InputDialog = TkRPCArgDialog(self.window, self.callComplexMethodFinal, argspec, name, func)

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
        message = self.__EntryInput.get()

        if len(message) <= 1:
            self.logdebug("No message to send entered.")
            return

        try:
            msg = jsonpickle.decode(message)
            if msg.sender != self.name:
                msg.sender = self.name
            self.loginfo("Transmitting message '%s'" % msg)
            self.transmit(msg)
            self.__FrameInput['bg'] = self.defaultcolors['bg']
        except ValueError as e:
            errmsg = 'Invalid JSON:\n%s' % e
            self.logerror(e)
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

                self.componentlist[comp]["Info"] = result
                MenuSubComponent = self.componentlist[comp]["Menu"]
                MenuSubComponent.delete(3, END)

                mr = result['methods']

                for meth in mr:
                    self.logdebug("Got method '%s'." % meth)
                    if len(mr[meth]['args']) > 0:
                        MenuSubComponent.add_command(label=meth, command=lambda (name,meth,argspec)=(msg.sender,meth,mr[meth]['args']): self.callComplexMethod(name,meth,argspec))
                    else:
                        MenuSubComponent.add_command(label=meth, command=lambda (name,meth)=(msg.sender,meth): self.callSimpleMethod(name,meth))

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
               self.componentlist[comp] = {"Menu": MenuSubComponent, "Info": None}


        if isinstance(msg, ANRV.Messages.Message):
            if msg.sender == self.systemregistry:
                if msg.func == "listRegisteredComponents":
                    if isinstance(msg.arg, tuple):
                        success, result = msg.arg
                        if success:
                            __handleRegisteredComponents(msg)
            print(msg.sender)
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

    def _filteredMsg(self, msg):
        return False

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



#############################################################################################################
        self.__FrameMenu = Frame(self.window)
        self.__FrameMenu.pack(anchor='n',side='top')

        self.__Menu = Menu(self.window)
        self.__MenuFile = Menu(self.__Menu)
        self.__MenuEdit = Menu(self.__Menu)
        self.__MenuTests = Menu(self.__Menu)
        self.__Menu.add_cascade(menu=self.__MenuFile, label="File")
        self.__Menu.add_cascade(menu=self.__MenuEdit, label="Edit")
        self.__Menu.add_cascade(menu=self.__MenuTests, label="Tests")
        self.window.config(menu=self.__Menu)

        self.__MenuFile.add_command(label="History", command=self.showHistory)
        self.__MenuFile.add_command(label="Update Message Log", command=self.updateMessageLog)
        self.__MenuFile.add_command(label="Quit", command=self.quit)
        
        self.__MenuTests.add_command(label="Scanlinetest", command=self.scanlinetest)


        self.autoscan = BooleanVar()
        self.autoscan.set(True)

        self.__MenuComponents = Menu(self.__Menu)
        self.__MenuComponents.add_checkbutton(label="Autoscan", onvalue=True, offvalue=False, variable=self.autoscan)
        self.__MenuComponents.add_command(label="Scan", command=self.scanregistry)
        self.__MenuComponents.add_separator()

        self.__Menu.add_cascade(menu=self.__MenuComponents, label="Components")


        ##############

        self.__FrameOutput = Frame(self.window)
        self.__FrameOutput.pack(side='top',fill='both',expand='yes')

        self.__NotebookOutput = Pmw.NoteBook(self.__FrameOutput)
        self.__NotebookOutput.pack(fill='both', expand=1)

        self.__PageResponses = self.__NotebookOutput.add('Responses')
        self.__PageLog = self.__NotebookOutput.add('Log')
        self.__PageMap = self.__NotebookOutput.add('Map')
        self.__PageMessages = self.__NotebookOutput.add('Messages')

        self.__MessageLog = Pmw.ScrolledListBox(self.__PageMessages)
        self.__MessageLog._listbox.bind("<Double-Button-1>", self.showMessage)
        self.__MessageLog.pack(expand='yes', fill='both')

        self.__NotebookOutput.tab('Responses').focus_set()

        self.__FrameInput = Frame(self.window, borderwidth=2)
        self.__FrameInput.pack(anchor='s',expand='no',fill='x',side='top')

        self.__FrameStatusbar = Frame(self.window, relief='raised')
        self.__FrameStatusbar.pack(anchor='sw',side='top') # ,fill='x'

        self.__LabelStatus = Label(self.__FrameStatusbar,text='Ready.')
        self.__LabelStatus.pack(anchor='w',expand='yes',side='top') # ,fill='both'

        self.__FrameResponses = Frame(self.__PageResponses)
        self.__FrameResponses.pack(expand=1, fill="both")

        self.__FrameResponsesHeader = Frame(self.__FrameResponses)
        self.__FrameResponsesHeader.pack(anchor='n',expand='yes', fill='x', side='top')

        self.__LabelResponses = Label(self.__FrameResponsesHeader,text='Responses')
        self.__LabelResponses.pack(anchor='e',side='right', fill='both')

        self.__ButtonClearResponses = Button(self.__FrameResponsesHeader, text='Clear')
        self.__ButtonClearResponses.pack(anchor='w',side='left')

        self.__TextResponses = Pmw.ScrolledText(self.__FrameResponses)
        self.__TextResponses.pack(expand=1, fill='both')

        self.__FrameLog = Frame(self.__PageLog)
        self.__FrameLog.pack(side='left', expand=1, fill="both")

        self.__FrameLogHeader = Frame(self.__FrameLog)
        self.__FrameLogHeader.pack(anchor='n',expand='yes', fill='x', side='top')

        self.__LabelLog = Label(self.__FrameLogHeader,text='Log')
        self.__LabelLog.pack(anchor='e',side='right', fill='both')

        self.__ButtonClearLog = Button(self.__FrameLogHeader, text='Clear')
        self.__ButtonClearLog.pack(anchor='w',side='left')

        self.__TextLog = Pmw.ScrolledText(self.__FrameLog)
        self.__TextLog.pack(expand=1,fill='both')

        self.__MapCanvas = Canvas(self.__PageMap)
        self.__MapCanvas.pack(expand=1, fill='both')

        self.__NotebookOutput.setnaturalsize()

        self.__FrameInputEntry = Frame(self.__FrameInput)
        self.__FrameInputEntry.pack(side='left')

        self.__LabelInput = Label(self.__FrameInputEntry,text='Input')
        self.__LabelInput.pack(anchor='w',expand='yes',fill='both',side='left')

        self.__Frame1 = Frame(self.__FrameInput)
        self.__Frame1.pack(expand='yes',fill='x',side='left')

        self.__EntryInput = Entry(self.__Frame1, foreground="White")
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

        if self.Configuration.has_key('autoscan') and self.Configuration['autoscan'] == True:
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
                if not self._filteredMsg(msg):
                    self.__TextResponses.insert(END, "%s\n" % msg)
            self.tkupdate()

Registry.ComponentTemplates['TkAdmin2'] = [TkAdmin2, "Simple Second revision Admin GUI providing message relaying and log viewing."]
