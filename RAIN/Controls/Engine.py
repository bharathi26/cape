#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
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

from ANRV.System import Registry
from ANRV.System import RPCComponent
from ANRV.Messages import Message

class SimpleEngine(RPCComponent.RPCComponent):
    """
    = Simple Engine Component =

    Used mainly to control the motorship 0's 3,7kW engine via Maestro controller.
    """

    address = 0x01
    upper = 1616
    lower = 1408

    delta = self.Configuration['Upper'] - self.Configuration['Lower']
    center = self.Configuration['Lower'] + (delta / 2)

    def rpc_setThrust(self, newthrust):
        """Calculates the new servo value for a given thrust.
        Arranges 4 bytes to contain the control command, servo address and new target.
        Transmits a Message containing these bytes to the Maestro Component and returns True.
        """

#        Problems:
#        * We don't really know what name the Maestro has.
#        * Most of the stuff isn't really configureable right now, this has to wait for the configuration system to be
#          fully grown to potential.
#        * This is a very Maestro centric component, and should be defined as such.
#        * It cannot really decide wether the maestro actually sent the command, unless we integrate states and defers
#          (It has to talk back with the Maestro and await its response before it can reliably give the requesting
#           party a response)

        target = int(self.center + (self.delta / 2) * newthrust)
        #print(("\n\n\n##### ENGINE TARGET: ", target))

        # Construct the bytes to send to the maestro
        byte = chr(0x84) + chr(self.address) + chr((target*4) & 0x7f) + chr(((target*4) >> 7) & 0x7F)
        #print(("##### ENGINE BYTES: ", byte, "\n\n\n"))

        self.send(Message(self.name, self.Configuration['Maestro'], "write", {"args": byte}))

        # TODO: Instead of this, we should enter a state here and await a response before returning our OK.
        return (True, "New thrust set.")

    def handleResponse(self, response):
        return True

    def __init__(self):
        self.MR['rpc_setThrust'] = {'newthrust': [float, "New thrust as float. Range [-1;0;1]."]}

        super(SimpleEngine, self).__init__()
        self.Configuration.update({
            'Maestro': ''
            'Upper': 0
            'Lower': 0
        })

Registry.ComponentTemplates['SimpleEngine'] = [SimpleEngine, "Simple Engine (Maestro Controlled) Component"]
