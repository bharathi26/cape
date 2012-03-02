#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software - CLI Classes
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

from ..Primitives import Frequency

from time import sleep

class Idler(Axon.Component.component):
    def __init__(self, frequency=Frequency("IdlerFreq", 200)):
        super(Idler, self).__init__(self)
        self.frequency = frequency

    def main(self):
        running = True
        while running:
            response = None
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if msg.recipient == "Idler":
                    if msg.func == "SetFreq": # and type(msg.arg) == type(Frequency):
                        self.frequency = msg.arg
                        response = msg.response(True)
                    else:
                        response = msg.response(False)

            if response:
                self.send(response, "outbox")
            sleep(self.frequency.Period())
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

