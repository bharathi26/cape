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

from Kamaelia.Chassis.Graphline import Graphline
import Kamaelia.IPC

from ANRV.Messages import Message
from ANRV.System import Registry

from collections import deque

import jsonpickle

from pprint import pprint


class JSONServer(Axon.Component.component):
    Inboxes = {"inbox": "RPC commands",
               "protocolin": "Incoming JSON",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "protocolout": "Outgoing JSON",
                "signal": "Signaling from this Protocol"}

    msgfilter = {'recipients': ['ALL'], 'sender': []}

    def __init__(self):
        super(JSONServer, self).__init__()

    def main(self):
        Dispatcher = Registry.Components["Dispatcher"]
        Dispatcher.RegisterComponent(self)

        protocol_running = True
        print("DEBUG.JSONServer: Client connected. I am %s" % (self.name))
        while protocol_running:
            while not self.anyReady():
                self.pause()
                # Thumb twiddling.
                yield 1

            response = None

            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if ("ALL" in self.msgfilter['recipients']) or (not self.msgfilter['recipients']) or msg.recipient in self.msgfilter['recipients']:
                    self.send(msg.jsonencode().encode("utf-8"), "protocolout")
                    yield 1
                else:
                    print(("DEBUG.JSONServer.Filtered: %s" % msg))
            if self.dataReady("protocolin"):
                response = None
                msg = None
                data = None
#                print("DEBUG.JSONServer: Running inbox (inbox)")
                data = self.recv("protocolin")
#                print("Accepted Input:", data)
                if len(data) == 0:
                    response = "\n"
                else:
                    try:
                        msg = jsonpickle.decode(data.decode("utf-8"))
                        if type(msg) == Message:
                            # TODO: Message validation!
                            msg.sender = self.name
                            self.send(msg, "outbox")
                    except ValueError as error:
                        print("%s:MALFORMED INPUT: %s" % (self.name, data))
                        response = Message(sender=self.name, recipient="CLIENT", func="Error", arg=[error.args[0], data.decode("UTF-8", errors="ignore")])
                        print(response)
                        response = response.jsonencode()
                        response = response.encode("utf-8")

#                    if msg and isinstance(msg, Message):
#                        if msg.recipient == "JSONServer":
#                            if msg.func == "SetFilter":
#                                self.msgfilter = msg.arg
#                                #response = msg.response(True)
#                                print(("Filter has been changed to %s" % msg.arg))
#                            if msg.func == "AddRecipient":
#                                self.msgfilter['recipients'].append(msg.arg)
#                                #response = msg.response(True
#                                print(("Recipient %s has been added to filter." % msg.arg))
                if response:
                    self.send(response, "protocolout")
                yield 1


            if self.dataReady("control"):
                data = self.recv("control")
                if isinstance(data, Kamaelia.IPC.socketShutdown):
                    print("DEBUG.JSONServer: Protocol shutting down.")
                    protocolRunning = False
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            print("DEBUG.JSONServer: Shutdown finished.")
            return isinstance(msg, Axon.Ipc.producerFinished)


class JSONSplitter(Axon.Component.component):
    Inboxes = {"inbox": "Unsplit JSON",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "Linesplit JSON",
                "signal": "Signaling from this Protocol"}

    buflist = deque()
    maxlength = 20
    separator = b"\r\n"

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
                    if len(msg) > 0:
#                        print("Appending:", msg)
                        self.buflist.append(msg.rstrip(self.separator))
            if len(self.buflist) > 0:
                response = self.buflist.popleft()
                self.send(response, "outbox")
#                print(("DEBUG.JSONSplitter.Queuelength: %i" % len(self.buflist)))
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

def JSONProtocol(*argv, **argd):
    return Graphline(
        SPLITTER = JSONSplitter(),
        #CE = ConsoleEchoer(),
        SERVER = JSONServer(),

        linkages = {("self", "inbox"): ("SPLITTER", "inbox"),
                    ("SPLITTER", "outbox"): ("SERVER", "protocolin"),
                    ("SERVER", "protocolout"): ("self", "outbox")}

    )
