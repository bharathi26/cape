#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software - CLI Classes
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

class CLIProtocol(Axon.Component.component):
    Inboxes = {"inbox": "Command line commands",
               "control": "Signaling to this Protocol",
               "i2cin": "Incoming i2c traffic",
               "sensorsin": "Incoming sensors traffic",
               "controlsin": "Incoming controls traffic"}
    Outboxes = {"outbox": "Command line responses",
                "signal": "Signaling from this Protocol",
                "i2cout": "Outgoing i2c traffic",
                "sensorsout": "Outgoing sensors traffic",
                "controlsout": "Outgoing controls traffic"}
    def main(self):
        protocol_running = True
        while protocol_running:
            while not self.anyReady():
                self.pause()
                # Thumb twiddling.
                yield 1
            if self.dataReady("i2cin"):
                # TODO: How to correctly handle incoming traffic?
                # - Discard stuff thats not meant for us
                # - Decide what to do with the rest
                # For now, just give it to the user:
                msg = self.recv("i2cin")
                if not isinstance(msg, I2CMessage):
                    print("ERROR: WRONG MESSAGE FORMAT ON I2C BACKPLANE!")
                self.send("Backplane.I2C.%s: %s (%s)\n" % (str(msg.origin), str(msg.content), str(msg.msgtype)), "outbox")
            # Likewise for the other two backplanes:
            if self.dataReady("sensorsin"):
                self.send("Backplane.SENSORS: " + self.recv("sensorsin") + "\n", "outbox")
            if self.dataReady("controlsin"):
                self.send("Backplane.CONTROLS: " + self.recv("controlsin") + "\n", "outbox")
            if self.dataReady("inbox"):
                print("DEBUG.CLI: Processing CLI Data.")
                data = None
                data = self.recv("inbox").rstrip('\r\n')

                if len(data) > 0 and data[0] == "/":
                    # TODO: This CLI parser sucks balls.
                    # Let's get a good one as soon as we know what we want ;)
                    data = data.split(" ")
                    cmd = data[0][1:]
                    response = "Interpreting command '%s'" % cmd
                    if cmd.upper() == "DISCONNECT":
                        print("DEBUG.CLI: Shutting down.")
                        response += "\nOk.\n"
                        self.send(Axon.Ipc.shutdownMicroprocess(), "signal")
                    elif cmd.upper() == "QUIT":
                        # TODO: Bad way to exit. Servers won't be taken down etc.
                        print("DEBUG.CLI: Quitting upon user request.")

                        from Axon.Scheduler import scheduler
                        import sys, time

                        scheduler.run.stop()
                        time.sleep(5)
                        sys.exit(0)
                    else:
                        response += "\nError: Unknown command.\n"
                elif len(data) > 0:
                    response = "Processing as i2c command...\n"
                    # TODO: Interpret command and act accordingly.
                    # For now, all stuff gets sent to the i2c component via backplane I2C directly
                    msg = I2CMessage(data, "CLI", "REQ")
                    self.send(msg, "i2cout")
            if self.dataReady("control"):
                data = self.recv("control")
                if isinstance(data, Kamaelia.IPC.socketShutdown):
                    print("DEBUG.CLI: Protocol shutting down.")
                    protocolRunning = False
            if response:
                self.send(response, "outbox")
                response = None
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

