#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
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

from RAIN.System import Registry
from RAIN.System import RPCComponent
from RAIN.Messages import Message

class MSPTop(RPCComponent.RPCComponent):
    """
    = Top MSP430 Computer Component =

    """

    def rpc_init(self):
        "Initializes the serial connection and the MSP430."

        port = self.Configuration['SerialPort']

        self.logdebug("Initializing MSP430 at '%s'." % self.Configuration['SerialPort'])
        self.send(Message(self.name, port, "subscribe", {"name": self.name, "function": "serialsubscription"}))

        self.send(Message(self.name, port, "connect"))
        self.send(Message(self.name, port, "write", "\n"))
        self.send(Message(self.name, port, "write", "hello\n"))

    def _setLights(self, mode):
        if mode >= 0 and mode < 4:
            self.send(Message(self.name, self.Configuration['SerialPort'], "write", "lights%i\n" % mode))
            # TODO: Instead of this, we should enter a state here and await a response before returning our OK.
            return (True, "New lights set.")

    def rpc_setLights(self, mode):
        return self._setLights(mode)

    def rpc_blinkLight(self, light, count):
        if light <= 1:
            for blink in range(count):
                self.send(Message(self.name, self.Configuration['SerialPort'], "write", "toggle%i\n" % light))
            return (True)
        else:
            return (False, "Not more than two lights available.")

    def rpc_measureHygro(self):
        self.logdebug("Measuring hygrometer's voltage.")
        self.send(Message(self.name, self.Configuration['SerialPort'], "write", "measurehygro\n"))

    def rpc_serialsubscription(self, data):
        "Return calls from the MSP430"
        self.logdebug("'%s'" % data)
        if data == "MSPTop":
            self.loginfo("Initialized MSPTop successfully.")
            self._setLights(0)

    def handleResponse(self, errorcode):
        if response.error == "Not connected.": # TODO: WHAT THE HECK. Not like this.
            self.logwarning("Serialport not connected. Trying to connect.")
            self.send(Message(self.name, self.Configuration['SerialPort'], "connect"))

    def __init__(self):
        self.MR['rpc_init'] = {}
        self.MR['rpc_measureHygro'] = {}
        self.MR['rpc_setLights'] = {'mode': [int, "Lightmode [0: off, 1: Steerboard on, 2: Port on, 3: Both on"]}
        self.MR['rpc_blinkLight'] = {'light': [int, "Which light to blink."],
                                     'count': [int, "How many times to blink."],
                                    }
        self.MR['rpc_serialsubscription'] = {'data': [str, "Responses from the serial device."]}

        super(MSPTop, self).__init__()
        self.Configuration['SerialPort'] = "RAIN.Communication.SerialPort.SerialPort_14" # TODO: For development purposes

Registry.ComponentTemplates['MSPTop'] = [MSPTop, "Top MSP430 Computer"]
