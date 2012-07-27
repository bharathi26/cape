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
        args = {'newangle': [float, 'New rudder angle (-1;0;1)']}

        if isinstance(newangle, float): # TODO: Bad, we should do argument typechecking at a higher (RPC) level!
            target = (self.center + (self.delta / 2) * msg.arg)
            #print(("\n\n\n##### ENGINE TARGET: ", target))

            # Construct the bytes to send to the maestro
            byte[0] = 0x84
            byte[1] = self.address
            byte[2] = (target*4) & 0x7f
            byte[3] = ((target*4) >> 7) & 0x7F
            #print(("##### ENGINE BYTES: ", byte, "\n\n\n"))

            self.send(Message(self.name, "MAESTRO", "Write", byte))
            return True
        else:
            return (False, "WRONG ARGUMENT")

Registry.ComponentTemplates['SimpleRudder'] = [SimpleRudder, "Simple Rudder (Maestro Controlled) Component"]
