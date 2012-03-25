#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software - Useless Ping Component
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

import serial

class Maestro(Axon.Component.component):
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol"}
    verbosity = 1
    protocol = "SSC"
    device = "/dev/ttyACM0"
    autodetect = True
    maestro = None

    def _connect(self):
        try:
            self.maestro = serial.Serial(self.device)
            if self.autodetect:
                self.maestro.write(chr(0xAA))
                self.maestro.flush()
        except Exception as error:
            print "DEBUG.MAESTRO._connect: Failed to open device: %s" % error
            self.maestro = None

    def __init__(self, device="/dev/ttyACM0", autodetect=True, protocol="SSC", verbosity=1):
        super(Maestro, self).__init__(self)
        self.device = device
        self.autodetect = autodetect
        self.protocol = protocol
        self.verbosity = verbosity

        self._connect()

    def write(self, args):
        print "DEBUG.MAESTRO.Write: Writing to Maestro: %s" % args
        try:
            for byte in args:
                self.maestro.write(chr(byte))
            return True
        except Exception as error:
            print "DEBUG.MAESTRO.Write: Failed to write: %s" % error
            return False, error 
            # TODO: Maybe not a good idea to return the exception itself. Traceback might help

    def main(self):
        while True:
            while not self.anyReady():
                # Thumb twiddling.
                self.pause()
                yield 1
            
            response = None
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if msg.recipient == "MAESTRO":
                    if msg.func == "Write":
                        response = msg.response(arg=self.write(msg.arg))
                    elif msg.func == "SetVerbosity":
                        self.verbosity = int(msg.arg)
                        response = msg.response(True)
                    #elif msg.func == "SetFreq": # and type(msg.arg) == type(Frequency):
                    #    response = msg.response(True)
            if response:
                self.send(response, "outbox")
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

