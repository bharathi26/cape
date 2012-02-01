#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
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

# TODO:
# - BUG.Server: System doesn't quit when asked to, probably because signals are wired strangely
#        Which keeps the socket from resetting correctly. Currently VERY ANNOYING.
# - I'd rather have a single component interacting with the user, that sends on user input
#   to another component which in turn handles distribution/communication with the backplanes.
# - The whole stuff doesn't idle loop correctly - it eats all cpu it can get. 
#   And apparently it is doing that in a non-multicore compatible way. GIL in the way?
# - Input sanitization
# - Good command parser
#  - Sensible (future ready) yet easy command set
#  - Useful argument handling
#  - History and interactivity would be nice, yet this is rather client related
#  - Documentation (builtin)
# - i2c communicator listening in on the backplane

from re import escape

import Axon
from Axon.Scheduler import scheduler

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.ConnectedServer import ServerCore
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.Util.Introspector import Introspector
from Kamaelia.Util.Console import ConsoleEchoer

from ANRV.Communication.I2C import I2CAdaptor
from ANRV.Communication.CLI import CLIProtocol

print "DEBUG.Server: Setting up Introspection Client."
Pipeline(
    Introspector(),
    TCPClient("127.0.0.1",55556)
).activate()

print "DEBUG.Server: Setting up Backplanes."
Backplane("I2C").activate()
Backplane("SENSORS").activate()
Backplane("CONTROLS").activate()

print "DEBUG.Server: Activating ConsoleEchoer for I2C, CONTROLS and SENSORS."
Pipeline(
    SubscribeTo("I2C"),
    SubscribeTo("CONTROLS"),
    SubscribeTo("SENSORS"),
    ConsoleEchoer()
).activate()

print "DEBUG.Server: Activating I2CAdaptor."
Pipeline(
    SubscribeTo("I2C"),
    I2CAdaptor(),
    PublishTo("I2C")
).activate()

print "DEBUG.Server: Preparing CLI protocol."
def CLI(*argv, **argd):
    # TODO: This is an ugly CRUFT thats probably not supposed to live long.
    # The linkages and messageboxes could be optimized, i don't yet know how. 
    return Graphline(
        CP = CLIProtocol(),
        I2CP = PublishTo("I2C"),
        I2CS = SubscribeTo("I2C"),
        SENSORSP = PublishTo("SENSORS"),
        SENSORSS = SubscribeTo("SENSORS"),
        CONTROLSP = PublishTo("CONTROLS"),
        CONTROLSS = SubscribeTo("CONTROLS"),

        linkages = {("self", "inbox"): ("CP", "inbox"),
                    ("CP", "outbox"): ("self", "outbox"),
                    ("self", "signal"): ("CP", "control"),
                    ("CP", "signal"): ("self", "control"),
                    ("CP", "i2cout"): ("I2CP", "inbox"),
                    ("I2CS", "outbox"): ("CP", "i2cin"),
                    ("CP", "sensorsout"): ("SENSORSP", "inbox"),
                    ("SENSORSP", "outbox"): ("CP", "sensorsin"),
                    ("CP", "controlsout"): ("CONTROLSP", "inbox"),
                    ("CONTROLSS", "outbox"): ("CP", "controlsin")}
    )

print "DEBUG.Server: Setting up CLI server on port 55555."
ServerCore(protocol = CLI, port=55555).activate()

print "DEBUG.Server: Starting all threads."
scheduler.run.runThreads()
