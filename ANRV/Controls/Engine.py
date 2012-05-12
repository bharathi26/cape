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

import Axon

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from ..Messages import Message
from ..Primitives import Angle

class SimpleEngine(Axon.Component.component):
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol"}

    verbosity = 1
    address = 0x01
    upper = 1616
    lower = 1408

    delta = upper - lower
    center = lower + (delta / 2)

    def SetThrust(self, msg):
        if isinstance(msg.arg, float):
            target = (self.center + (self.delta / 2) * msg.arg)
            print(("\n\n\n##### ENGINE TARGET: ", target))

            byte[0] = 0x84
            byte[1] = self.address
            byte[2] = (target*4) & 0x7f
            byte[3] = ((target*4) >> 7) & 0x7F
            print(("##### ENGINE BYTES: ", byte, "\n\n\n"))

            #response = Message(self.name, "MAESTRO", "Write", byte)
        else:
            response = msg.response((False, "WRONG ARGUMENT"))
        return response

    def main(self):
        while True:
            while not self.anyReady():
                # Thumb twiddling.
                self.pause()
                yield 1
            response = None
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if msg.recipient == "Engine":
                    if msg.func == "SetThrust":
                        response = self.SetThrust(msg)
                    if msg.func == "SetVerbosity":
                        self.verbosity = int(msg.arg)
                        response = msg.response(True)
            if response:
                self.send(response, "outbox")
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

