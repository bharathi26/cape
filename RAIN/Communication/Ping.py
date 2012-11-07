#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software - Useless Ping Component
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
from ..Primitives import Frequency

from time import time
from math import fsum

class Ping(Axon.Component.component):
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol"}
    lastping = 0
    count = 0
    rttlist = [0] * 30
    verbosity = 1

    def __init__(self, frequency=Frequency("PingFreq", period=60), verbosity=3):
        super(Ping, self).__init__(self)
        self.frequency = frequency
        self.verbosity = verbosity

    def main(self):
        self.lastping = time()
        while True:
            while (self.lastping + self.frequency.Period() > time()) and (not self.anyReady()):
                # Thumb twiddling.
                yield 1
            now = time()
            response = None
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if msg.sender == "Pong":
                    roundtrip = now - msg.arg['time']
                    del(self.rttlist[0])
                    self.rttlist.append(roundtrip)

                    arg = {}
                    arg['rtt'] = roundtrip
                    if self.verbosity > 0:
                        arg['count'] = self.count
                    if self.verbosity > 1:
                        arg['lastping'] = self.lastping
                    if self.verbosity > 2:
                        meanrtt = (
                        fsum(self.rttlist[-10:]) / 10, fsum(self.rttlist[-20:]) / 20, fsum(self.rttlist) / 30)
                        arg['meanrtt'] = meanrtt
                    response = Message(sender=self.name, recipient="ALL", arg=arg)
                if msg.recipient == "Ping":
                    response = msg.response(None)
                    if msg.func == "SetVerbosity":
                        self.verbosity = int(msg.arg)
                        response = msg.response(True)
                    if msg.func == "SetFreq": # and type(msg.arg) == type(Frequency):
                        self.frequency = msg.arg
                        response = msg.response(True)
            elif not response and (self.lastping + self.frequency.Period() < now):
                self.count += 1
                arg = {}
                arg['time'] = time()
                response = Message(sender=self.name, recipient="Pong", func="PING", arg=arg)
                self.lastping = time()
            if response:
                self.send(response, "outbox")
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

