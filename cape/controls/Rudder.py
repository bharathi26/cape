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

class SimpleRudder(RPCComponent.RPCComponent):
    """
    This is currently essentially a copy of the Rudder Component but shouldn't
    be just an inheritance of it.
    """

    address = 0x00
    upper = 1744
    lower = 1104

    delta = upper - lower
    center = lower + (delta / 2)

    def rpc_setRudder(self, newangle):
        """Calculates the new servo value for a given angle.
        Arranges 4 bytes to contain the control command, servo address and new target.
        Transmits a Message containing these bytes to the Maestro Component and returns True.
        """

        target = int(self.center + (self.delta / 2) * newangle)
        #print(("\n\n\n##### ENGINE TARGET: ", target))

        # Construct the bytes to send to the maestro
        byte = chr(0x84) + chr(self.address) + chr((target * 4) & 0x7f) + chr(((target * 4) >> 7) & 0x7F)
        #print(("##### ENGINE BYTES: ", byte, "\n\n\n"))

        self.send(Message(self.name, self.Configuration['Maestro'], "write", {"args": byte}))

        # TODO: Instead of this, we should enter a state here and await a response before returning our OK.
        return (True, "New angle set.")

    def handleResponse(self, response):
        return True

    def __init__(self):
        self.MR['rpc_setRudder'] = {'newangle': [float, "New angle as float. Range [-1;0;1]."]}

        super(SimpleRudder, self).__init__()
        self.Configuration.update({
            'Maestro': 'cape.Maestro'
        })

Registry.ComponentTemplates['SimpleRudder'] = [SimpleRudder, "Simple Rudder (Maestro Controlled) Component"]
