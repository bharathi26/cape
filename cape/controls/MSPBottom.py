#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#      Simple Thrust Control Virtual Component (SRCVC)
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
from cape.messages import Message

class MSPBottom(RPCComponent.RPCComponent):
    """
    = Bottom MSP430 Computer Component =

    """

    def rpc_init(self):
        "Initializes the serial connection and the MSP430."

        port = self.Configuration['SerialPort']

        self.logdebug("Initializing MSP430 at '%s'." % self.Configuration['SerialPort'])
        self.send(Message(self.name, port, "subscribe", {"name": self.name, "function": "serialsubscription"}))

        self.send(Message(self.name, port, "connect"))
        self.send(Message(self.name, port, "write", "\n"))
        self.send(Message(self.name, port, "write", "hello\n"))

    def rpc_serialsubscription(self, data):
        "Return calls from the MSP430"
        self.logdebug("'%s'" % data)
        if data == "MSPBottom":
            self.loginfo("Initialized MSPBottom successfully.")
            self._setLights(0)

    def handleResponse(self, response):
        if response.error == "Not connected.": # TODO: WHAT THE HECK. Not like this.
            self.logwarning("Serialport not connected. Trying to connect.")
            self.send(Message(self.name, self.Configuration['SerialPort'], "connect"))

    def __init__(self):
        self.MR['rpc_init'] = {}
        self.MR['rpc_serialsubscription'] = {'default': [str, "Responses from the serial device."]}

        super(MSPBottom, self).__init__()
        self.Configuration[
        'SerialPort'] = "cape.Communication.SerialPort.SerialPort_14" # TODO: For development purposes

Registry.ComponentTemplates['MSPBottom'] = [MSPBottom, "Bottom MSP430 Computer"]
