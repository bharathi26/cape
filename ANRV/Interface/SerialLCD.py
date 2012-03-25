#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#     - Serial LCD Component -
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
# * Message buffer 
#  * Walking through messages (Ring, Pendulum etc)
#  * Message timeout
# * Write function
# * Who handles writing of sensor data?


import Axon

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from ..Messages import Message
from ..Primitives import Frequency

from time import time
from math import fsum


class SerialLCD(Axon.Component.component):
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this LCD"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this LCD"}
    verbosity = 1

    def __init__(self, verbosity=1):
        super(SerialLCD, self).__init__(self)
        self.verbosity = verbosity

    def write(self, args):
        # TODO: Call the maestro to actually sendout a message to the serial LCD
        # See here: http://www.sparkfun.com/datasheets/LCD/SerLCD_V2_5.PDF
        pass

    def main(self):
        while True:
            while not self.anyReady():
                # Thumb twiddling.
                self.pause()
                yield 1
            
            response = None
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if msg.recipient == "LCD":
                    if msg.func == "Write":
                        response = msg.response(arg=self.write(msg.arg))
                    elif msg.func == "SetVerbosity":
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

