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

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from ..Messages import Message

from collections import deque

import jsonpickle

class JSONServer(Axon.Component.component):
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol",
               "i2cin": "Incoming i2c traffic",
               "sensorsin": "Incoming sensors traffic",
               "controlsin": "Incoming controls traffic"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol",
                "i2cout": "Outgoing i2c traffic",
                "sensorsout": "Outgoing sensors traffic",
                "controlsout": "Outgoing controls traffic"}

    msgfilter = {'recipients': ['ALL'], 'sender': []}
    def main(self):
        protocol_running = True
        while protocol_running:
            while not self.anyReady():
                self.pause()
                # Thumb twiddling.
                yield 1
            response = None
            if self.dataReady("controlsin"):
                print "DEBUG.JSONServer: Running inbox (control)"
                msg = self.recv("controlsin")
                print msg
                if ("ALL" in self.msgfilter['recipients']) or (not self.msgfilter['recipients']) or msg.recipient in self.msgfilter['recipients']:
                    response = msg.jsonencode()
                    self.send(response, "outbox")
                    yield 1
                else:
                    print "DEBUG.JSONServer.Filtered: %s" % msg
            if self.dataReady("inbox"):
                print "DEBUG.JSONServer: Running inbox (inbox)"
                data = self.recv("inbox").rstrip("\r\n")
                if len(data) == 0:
                    response = "\n"
                else:
                    try:
                        msg = jsonpickle.decode(data)
                        # TODO: This is somewhat stupid:
                        self.send(msg, "controlsout")
                        self.send(msg, "sensorsout")
                    except Exception as error:
                        print "%s:MALFORMED INPUT: %s\n%s:%s" % (self.name, data, type(error), error.args)
                        response = "MALFORMED INPUT: %s" % data
                    print msg
                    if msg and isinstance(msg, Message):
                        if msg.recipient == "JSONServer":
                            if msg.func == "SetFilter":
                                self.msgfilter = msg.arg
                                #response = msg.response(True)
                                print "Filter has been changed to %s" % msg.arg
                            if msg.func == "AddRecipient":
                                self.msgfilter['recipients'].append(msg.arg)
                                #response = msg.response(True)
                                print "Filter has been changed to %s" % msg.arg
                if response:
                    self.send(response, "outbox")
                yield 1


            if self.dataReady("control"):
                data = self.recv("control")
                if isinstance(data, Kamaelia.IPC.socketShutdown):
                    print "DEBUG.JSONServer: Protocol shutting down."
                    protocolRunning = False
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)


class JSONSplitter(Axon.Component.component):
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol"}

    buflist = deque()
    maxlength = 20
    separator = "\r\n"

    def main(self):
        while True:
            while not self.anyReady() and len(self.buflist) == 0:
                # Thumb twiddling.
                self.pause()
                yield 1
            response = None

            if self.dataReady("inbox"):
                msgs = self.recv("inbox")
#                if buflist.count() >= maxlength:
#                    response = Message(self.name, "JSONServer", "WarnQueueFull")
                for msg in msgs.split(self.separator):
                    self.buflist.append(msg)
            if len(self.buflist) > 0:
                response = self.buflist.popleft()
                self.send(response, "outbox")
                print "DEBUG.JSONSplitter.Queuelength: %i" % len(self.buflist)
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

