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
    address = 0x01
    upper = 1616
    lower = 1408

    delta = upper - lower
    center = lower + (delta / 2)

    def rpc_setThrust(self, newthrust):
        """Calculates the new servo value for a given thrust.
        Arranges 4 bytes to contain the control command, servo address and new target.
        Transmits a Message containing these bytes to the Maestro Component and returns True.
        """
        args = {'newthrust': [float, 'New thrust (-1;0;1)']}

#        Problems:
#        * We don't really know what name the Maestro has.
#        * Most of the stuff isn't really configureable right now, this has to wait for the configuration system to be
#          fully grown to potential.
#        * This is a very Maestro centric component, and should be defined as such.
#        * It cannot really decide wether the maestro actually sent the command, unless we integrate states and defers
#          (It has to talk back with the Maestro and await its response before it can reliably give the requesting
#           party a response)

        if isinstance(newthrust, float): # TODO: Bad, we should do argument typechecking at a higher (RPC) level!
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

Registry.ComponentTemplates['SimpleEngine'] = [SimpleEngine, "Simple Engine (Maestro Controlled) Component"]
