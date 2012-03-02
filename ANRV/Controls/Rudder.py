#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software - Rudder Class
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

# DO NOT USE!
# THIS IS WIP!

import Axon

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from Messages import I2CMessage

class Rudder(Axon.Component.component):
    # TODO: Uaah.
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
        while True:
            while not self.anyReady():
                # Thumb twiddling.
                self.pause()
                yield 1
            if self.dataReady("i2cin"):
                # TODO: How to correctly handle incoming traffic?
                # - Discard stuff thats not meant for us
                # - Decide what to do with the rest
                # For now, just give it to the user:
                msg = self.recv("i2cin")
                # TODO: What? I2CMessages are out of date.
                if not isinstance(msg, I2CMessage):
                    print "ERROR: WRONG MESSAGE FORMAT ON I2C BACKPLANE!"
                # TODO: Act upon received i2c message
            # Likewise for the other two backplanes:
            if self.dataReady("sensorsin"):
                self.send("Backplane.SENSORS: " + self.recv("sensorsin") + "\n", "outbox")
            if self.dataReady("controlsin"):
                self.send("Backplane.CONTROLS: " + self.recv("controlsin") + "\n", "outbox")
            if self.dataReady("inbox"):
                data = self.recv("inbox").rstrip('\r\n')

            if response:
                self.send(response, "outbox")
                response = None
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

