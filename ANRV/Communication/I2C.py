#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software - I2C Adaptor
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
#


import Axon
from Axon.Scheduler import scheduler

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from Messages import I2CMessage

class I2CAdaptor(Axon.Component.component):
    # TODO: This is standard wiring. Either do something nonstandard (why?) or kick this out.
    Inboxes = {"inbox": "i2c bus commands",
               "control": "Signaling to this Adaptor"}
    Outboxes = {"outbox": "i2c bus responses",
                "signal": "Signaling from this Protocol"}
    def main(self):
        print "DEBUG.I2CAdaptor: Firing up i2c. (NOT REALLY)"
        # TODO: Open i2c bus somehow. (See tickets #78 and #79)

        i2c_running = True
        while i2c_running: # TODO: Can't be shut down.
            while not self.dataReady():
                self.pause()
                # Thumb twiddling.
                yield 1
            print "DEBUG.I2CAdaptor: Receiving Message."
            data = None
            if self.dataReady("inbox"):
                print "DEBUG.I2CAdaptor: Processing Message"
                data = self.recv("inbox")
                if not isinstance(data, I2CMessage):
                    print "ERROR.I2CAdaptor:  WRONG MESSAGE FORMAT ON I2C BACKPLANE!"
                else:
                    if data.origin != "ADAPTOR":
                        from pprint import pprint
                        pprint(data)
                        # TODO:
                        # * Actually evaluate the message and decide what to do
                        # * Usually that boils down to either transmitting a command and
                        #  * either wait for a result
                        #  * or a Ok
                        # * What to do, if something goes wrong?
                        response = I2CMessage(data.content, "ADAPTOR", "ANSWER")
                        self.send(response, "outbox")
                    else:
                        print "DEBUG.I2CAdaptor: Message from ourself - ignored."
            if self.dataReady("control"):
                data = self.recv("control")
                print "DEBUG.I2CAdaptor: Received control signal: %s" % data
            yield 1
