#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
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

from RAIN.System import Identity
from RAIN.System import Registry
from RAIN.System.RPCComponent import RPCComponent
from RAIN.Messages import Message

from RAIN.Interface.TkMessageDialog import TkMessageDialog 
from RAIN.Interface.TkRPCArgDialog import TkRPCArgDialog

from Kamaelia.UI.Tk.TkWindow import TkWindow, tkInvisibleWindow

from Tkinter import Frame, Menu, Label, Entry, Button, Canvas, BooleanVar, TOP, BOTTOM, END
import tkMessageBox as messagebox

import jsonpickle
import Pmw

from Axon import Scheduler

class TkAdmin(TkWindow, RPCComponent):
    """
    Development graphical user interface for RAIN systems.
    """
    
    unique = True
    directory_name = "TkAdmin"

    # TODO:
    # * Clean up user interface
    # * Develop interaction elements for all primitives

    def __init__(self):
        self.nodelist = {}
        self.messages = []
        
        self.title = "RAIN TkAdmin - [%s]" % Identity.SystemName
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
        self.MapViewer = None

    def __on_ButtonClear_Press(self, Event=None):
        self.clearEntry()

    def __on_ButtonTransmit_Release(self, Event=None):
        self.usertransmit()

    def __on_EntryInput_Enter__C(self, Event=None):
        self.usertransmit()

    def __on_ButtonClearResponses_Press(self, Event=None):
        self.__TextResponses.clear()

    def showMessage(self, ev=None):
        msglb = self.__MessageLog._listbox
        sel = msglb.curselection()
        if len(sel) > 1:
            self.logwarning("Multiple messages selected to display. Can't.")
        msg = self.messages[int(sel[0])]
        msgdialog = TkMessageDialog(self.window, msg)
        
    def composeMessage(self, name="", node="", sender=None):
        if not sender:
            sender = self.name
        msg = Message(sender=sender, recipientnode=node, recipient=name)
        msgdialog = TkMessageDialog(self.window, msg, onclosecallback=self.transmit)  

    def clearEntry(self):
        self.__EntryInput.delete(0, END)
        self.__FrameInput['bg'] = self.defaultcolors['bg']

    #        self.__EntryInput['fg'] = self.defaultcolors['fg']

    def scanregistry(self, node=""):
        msg = Message(sender=self.name, 
                      recipientnode=node, 
                      recipient=self.systemregistry, 
                      func="listRegisteredComponents",
                      arg=None
                      )
        self.transmit(msg)
        msg = Message(sender=self.name,
                      recipientnode=node,
                      recipient=self.systemregistry,
                      func="listRegisteredTemplates",
                      arg=None
                      )
        self.transmit(msg)

    def scangateways(self):
        msg = Message(sender=self.name,
                      recipient=self.systemdispatcher,
                      func="listgateways"
                      )
        self.transmit(msg)

    def dumpnodelist(self):
        from pprint import pprint
        pprint(self.nodelist)        

    def scancomponent(self, name, node=""):
        self.logdebug("Scanning component '%s'." % name)
        msg = Message(sender=self.name, recipientnode=node, recipient=name, func="getComponentInfo", arg=None)
        self.transmit(msg)

    def createcomponent(self, name, node=""):
        self.loginfo("Creating component from template '%s'." % name)
        msg = Message(sender=self.name, recipientnode=node, recipient=self.systemregistry, func="createComponent", arg={'templatename': name})
        self.transmit(msg)
        
    def copystring(self, name):
        self.window.clipboard_clear()
        self.window.clipboard_append(name)        

    def callComplexMethod(self, componentname, node, func):
        self.loginfo("Creating function dialog for '%s'@'%s'." % (func, componentname))
        
        componentlist = self.nodelist[node]['componentlist']
        component = componentlist[componentname]
        componentinfo = component["info"]
        methods = componentinfo["methods"]
        methodregister = methods[func]
        
        InputDialog = TkRPCArgDialog(self.window, self.callComplexMethodFinal, componentname, node, func, methodregister)

    def callComplexMethodFinal(self, name, node, func, args):
        self.loginfo("Finally calling func '%s'@'%s' with args '%s'" % (func, name, args))
        msg = Message(sender=self.name, recipientnode=node, recipient=name, func=func, arg=args)
        self.transmit(msg)

    def callSimpleMethod(self, name, node, func):
        self.loginfo("Calling '%s'@'%s'." % (func, name))
        msg = Message(sender=self.name, recipient=name, recipientnode=node, func=func, arg=None)
        self.transmit(msg)

    def transmit(self, msg):
        self.logdebug("Transmitting Message '%s'" % msg)
        self.recordMessage(msg)
        self.send(msg, "outbox")

    def recordMessage(self, msg):
        self.messages.append(msg)
        self.updateMessageLog()

    def updateMessageLog(self):
        loglistbox = self.__MessageLog._listbox
        loglistbox.delete(0, END) # GAH. Addition should be sufficient. CHANGE!

        for msg in sorted(self.messages, key=lambda msg: msg.timestamp):
            loglistbox.insert(END, msg)
            if msg.recipient == self.name:
                loglistbox.itemconfig(END, bg='green', fg='black')
            else:
                loglistbox.itemconfig(END, bg='red', fg='black')

    def editIdentity(self):
        self.logerror("Not implemented. Here is a dump of this node's identity:")
        self.loginfo(Identity.SystemIdentity)
        self.loginfo(Identity.SystemUUID)

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

    def rebuildNodeMenu(self):
        NodeMenu = self.__MenuNodes
        NodeMenu.delete(4, END)

        for node in self.nodelist:
            NodeMenu.add_cascade(menu=self.nodelist[node]['menu'], label=node if node != "" else "LOCAL")
            

    def __handleNewNode(self, node):
        if node not in self.nodelist:
            self.loginfo("New node appeared! Hmm.")
        else:       
            self.loginfo("Node rescanned.")
            print self.__MenuNodes   
            
        componentlist = {}
        ComponentMenu = Menu(self.__MenuNodes)
        ComponentMenu.add_command(label="Scan", command=lambda node=node: self.scanregistry(node))
        ComponentMenu.add_command(label="Copy Name", command=lambda node=node: self.copystring(node))
        ComponentMenu.add_separator()

        nodeinfo = {'componentlist': componentlist,
                    'menu': ComponentMenu}
            
        self.nodelist[node] = nodeinfo



    def handleResponse(self, msg):
        self.recordMessage(msg)

        def __handleListRegisteredTemplates(msg):
            TemplateMenu = Menu(self.__MenuSystem)
            
            for template in sorted(msg.arg):
                node = ''
                TemplateMenu.add_command(label=template, command=lambda (name,node)=(template, node): self.createcomponent(name, node))
        
            self.__MenuSystem.add_cascade(label='Create Component', menu=TemplateMenu)
        

        def __handleComponentInfo(msg):
            node = msg.sendernode
            if node not in self.nodelist:
                self.logerror('Node unknown')
            else:
                componentlist = self.nodelist[node]['componentlist']
            
            if msg.sender not in componentlist:
                if self.autoscan.get():
                    self.loginfo("Unknown component '%s'. Rescanning registry." % msg.senderid)
                    self.scanregistry(node)
                else:
                    self.loginfo("Unknown component's ('%s') info encountered. Ignoring.")
            else:
                self.logdebug("Got a component's ('%s') RPC info. Parsing." % msg.sender)

                component = msg.sender
                result = msg.arg

                componentlist[component]["info"] = result
                
                FuncMenu = componentlist[component]["menu"]
                FuncMenu.delete(5, END)

                mr = result['methods']

                for meth in mr:
                    self.logdebug("Got method '%s'." % meth)
                    if len(mr[meth]['args']) > 0:
                        FuncMenu.add_command(label=meth,
                                             command=lambda (node, name, meth)=(node, component, meth): self.callComplexMethod(name, node, meth))
                    else:
                        FuncMenu.add_command(label=meth,
                                             command=lambda (node, name, meth)=(node, component, meth): self.callSimpleMethod(name, node, meth))

        def __handleRegisteredComponents(msg):
            node = msg.sendernode
            
            self.loginfo("Got a list of registered components from '%s'. Parsing." % node)
            
            self.__handleNewNode(node)
                     
            # Schema nodelist:
            # {nodeUUID: {'componentlist': componentlist, 'menu': ComponentMenu}
            # Schema componentlist:
            # {componentname: {'funclist': funclist, 'menu': funcmenu}
            # Schema funclist:
            # {func: menu}
            
            components = msg.arg
            componentlist = self.nodelist[node]['componentlist']
            ComponentMenu = self.nodelist[node]['menu']
            
            for comp in components:
                self.loginfo("Adding component '%s@%s'" % (comp, node))
                if self.autoscan.get() and comp not in componentlist:
                    self.scancomponent(comp, node)
                FuncMenu = Menu(ComponentMenu)
                FuncMenu.add_command(label="Scan", command=lambda (name,node)=(comp, node): self.scancomponent(name, node))
                FuncMenu.add_command(label="Copy Name", command=lambda name=comp: self.copystring(name))
                FuncMenu.add_command(label="Compose...", command=lambda (name,node)=(comp,node): self.composeMessage(name, node))
                FuncMenu.add_separator()
                FuncMenu = Menu(ComponentMenu)

                ComponentMenu.add_cascade(label=comp, menu=FuncMenu)
                componentlist[comp] = {'menu': FuncMenu}
                
            self.rebuildNodeMenu() 

        def __handleGatewayList(msg):
            self.loginfo("Received a list of connected nodes.")
            
            for node in msg.arg:
                self.__handleNewNode(node)
                if self.autoscan.get():
                    self.scanregistry(node)
                
            self.rebuildNodeMenu()
            

        if isinstance(msg, Message):
            if msg.sender == self.systemdispatcher:
                if msg.func == "listgateways":
                    __handleGatewayList(msg)
            if msg.sender == self.systemregistry:
                if msg.func == "listRegisteredComponents":
                    if not msg.error:
                        __handleRegisteredComponents(msg)
                elif msg.func == "listRegisteredTemplates":
                    if not msg.error:
                        __handleListRegisteredTemplates(msg)
            if msg.func == "getComponentInfo":
                if not msg.error:
                    __handleComponentInfo(msg)
            if msg.func in ("renderArea", "renderCoord"):
                if not msg.error:
                    if self.MapViewer:
                        self.MapViewer.drawMap(msg.arg)
                    else:
                        self.MapViewer = TkMapDialog(msg.arg)
                        self.MapViewer.activate()

    def scanlinetest(self):
        polygon = [[50, 5], [100, 270], [150, 270], [220, 30]]
        ScanlineTestDialog = TkScanlineTestDialog(polygon)

    def quit(self):
        self.logcritical("Shutting down hard.")
        try:
            import cherrypy
            self.loginfo("WebGate running. Stopping cherrypy first.")
            cherrypy.engine.stop()
        except ImportError:
            self.loginfo("WebGate not running. Not killing cherrypy.")
        Scheduler.scheduler.run.stop()

    def setupWindow(self):
        self.logdebug("Setting up TkAdmin GUI")

        Pmw.initialise(self.window)

        self.window.title(self.title)


        ### Menu ###
        self.__FrameMenu = Frame(self.window)
        self.__FrameMenu.pack(anchor='n', side='top')

        self.__Menu = Menu(self.window)
        self.__MenuFile = Menu(self.__Menu)
        self.__MenuEdit = Menu(self.__Menu)
        self.__MenuMessage = Menu(self.__Menu)
        self.__MenuSettings = Menu(self.__Menu)
        self.__MenuSystem = Menu(self.__Menu)
        self.__Menu.add_cascade(menu=self.__MenuFile, label="File")
        self.__Menu.add_cascade(menu=self.__MenuEdit, label="Edit")
        self.__Menu.add_cascade(menu=self.__MenuMessage, label="Message")
        self.__Menu.add_cascade(menu=self.__MenuSettings, label="Settings")
        self.__Menu.add_cascade(menu=self.__MenuSystem, label="System")
        self.window.config(menu=self.__Menu)

        self.__MenuFile.add_command(label="Update Message Log", command=self.updateMessageLog)
        self.__MenuFile.add_command(label="Quit", command=self.quit)

        self.autoscan = BooleanVar()
        self.fixsender = BooleanVar()
        self.autoclear = BooleanVar()
        self.showresponses = BooleanVar()

        self.__MenuMessage.add_command(label="View", command=self.showMessage)
        self.__MenuMessage.add_command(label="Compose New", command=self.composeMessage)

        self.__MenuSettings.add_checkbutton(label="Fix sender", onvalue=True, offvalue=False, variable=self.fixsender)
        self.__MenuSettings.add_checkbutton(label="Autoscan", onvalue=True, offvalue=False, variable=self.autoscan)
        self.__MenuSettings.add_checkbutton(label="Autoclear", onvalue=True, offvalue=False, variable=self.autoclear)
        self.__MenuSettings.add_checkbutton(label="Show responses", onvalue=True, offvalue=False,
                                            variable=self.showresponses)
        
        self.__MenuSystem.add_command(label="View/Edit Identity", command=self.editIdentity)
        
        self.__MenuNodes = Menu(self.__Menu)
        self.__MenuNodes.add_command(label="Update connected nodes", command=self.scangateways)
        self.__MenuNodes.add_command(label="Scan Local", command=self.scanregistry)
        self.__MenuNodes.add_command(label="Dump Nodelist", command=self.dumpnodelist)

        self.__MenuNodes.add_separator()
        self.__Menu.add_cascade(menu=self.__MenuNodes, label="Nodes")


        ### /Menu ###

        ### Output ###

        self.__FrameOutput = Frame(self.window)
        self.__FrameOutput.pack(side='top', fill='both', expand='yes')

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
        self.__FrameInput.pack(anchor='s', expand='no', fill='x', side='top')

        self.__FrameStatusbar = Frame(self.window, relief='raised')
        self.__FrameStatusbar.pack(anchor='sw', side='top') # ,fill='x'

        self.__LabelStatus = Label(self.__FrameStatusbar, text='Ready.')
        self.__LabelStatus.pack(anchor='w', expand='yes', side='top') # ,fill='both'

        self.__FrameResponses = Frame(self.__PageResponses, background="yellow")

        self.__FrameResponsesHeader = Frame(self.__FrameResponses)

        self.__LabelResponses = Label(self.__FrameResponsesHeader, text='Responses')
        self.__LabelResponses.pack(anchor='e', side='right', fill='x')

        self.__ButtonClearResponses = Button(self.__FrameResponsesHeader, text='Clear')
        self.__ButtonClearResponses.pack(anchor='w', side='left')

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
        self.__EntryInput.pack(expand='yes', fill='both', side='left')

        self.__FrameTransmitButton = Frame(self.__FrameInput)
        self.__FrameTransmitButton.pack(anchor='w', side='left')

        self.__ButtonTransmit = Button(self.__FrameTransmitButton
            , text='Transmit')
        self.__ButtonTransmit.pack(expand='yes', fill='both', side='top')
        self.__FrameClearButton = Frame(self.__FrameInput)
        self.__FrameClearButton.pack(anchor='w', side='left')
        self.__ButtonClear = Button(self.__FrameClearButton, text='Clear')
        self.__ButtonClear.pack(expand='yes', fill='both', side='top')

        self.__FrameInputEntry.pack(side='left')

        ### /Input ###

        ### Bindings ###

        self.__MessageLog._listbox.bind("<Double-Button-1>", self.showMessage)
        self.__ButtonClearResponses.bind('<ButtonRelease-1>'
            , self.__on_ButtonClearResponses_Press)
        self.__ButtonTransmit.bind('<ButtonRelease-1>'
            , self.__on_ButtonTransmit_Release)
        self.__ButtonClear.bind('<ButtonPress-1>', self.__on_ButtonClear_Press)
        self.__EntryInput.bind('<Control-Return>', self.__on_EntryInput_Enter__C)

        self.defaultcolors = {'bg': self.window['bg'], 'fg': self.__EntryInput['fg']}

    def main(self):
        """  
        Main loop. Stub method, reimplement with your own functionality.

        Must regularly call self.tkupdate() to ensure tk event processing happens.
        """

        if self.autoscan.get():
            self.loginfo("Local autoscan initiated.")
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
                self.handleRPC(msg)
                if self.showresponses.get():
                    self.__TextResponses.insert(END, "%s\n" % msg)
            self.tkupdate()

Registry.ComponentTemplates['TkAdmin'] = [TkAdmin,
                                          "Simple Second revision Admin GUI providing message relaying and log viewing."]
