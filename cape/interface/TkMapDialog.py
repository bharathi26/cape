#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#      - Tk Admin Interface (Map Dialog)
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

from cape.system import registry
from cape.system import RPCComponent
import cape.messages
from cape.system import  identity
from cape.system.loggablecomponent import LoggableComponent
from cape.system.rpccomponent import RPCComponent

from Kamaelia.UI.Tk.TkWindow import TkWindow, tkInvisibleWindow

import Axon

import PIL
import PIL.Image
import PIL.ImageTk

try: # DEPENDENCYBUG
    import mapnik2 as mapnik
except:
    print "No mapnik2!"

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

import StringIO

class TkMapDialog(TkWindow, LoggableComponent):
    def __init__(self, mapimage=None):
        super(TkMapDialog, self).__init__()

        self.window.title("Map Viewer - [%s]" % identity.SystemName)

        self.frame = Frame(self.window)
        self.canvas = Canvas(self.frame)
        self.canvas.pack(fill="both", expand="yes")

        self.frame.pack(fill="both", expand="yes")

        if mapimage != None:
            self.drawMap(mapimage)

    def drawMap(self, mapimage):
        self.logdebug("Opening Image.")
        # first buffer (is this really necessary?)
        buf = StringIO.StringIO()
        buf.write(mapimage)
        buf.seek(0)

        pil_image = PIL.Image.open(buf)
        # Convert to Tk compatible image
        self.tk_image = PIL.ImageTk.PhotoImage(pil_image)

        self.logdebug("Drawing Image.")
        # TODO:
        # * dynamic map/canvas size, not fixed crap
        self.canvas.create_image(512, 384, image=self.tk_image)

