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

# This is a mess right now. It will probably stay that way for a few more months,
# until we're done with a good concept about the general structure.
# I'm thinking of something that will only start with a basic minimal component
# configuration and then read in a configuration to initially populate the system 
# with further components via a dynamic component loader.
#     -- riot


# TODO:
# * System doesn't quit when asked to, probably because signal/control boxes are wired
#   strangely - which keeps the socket from resetting correctly. Currently VERY ANNOYING.
# * I'd rather have a single component interacting with the user, that sends on user input
#   to another component which in turn handles distribution/communication with the backplanes.
# * The whole stuff doesn't idle loop correctly - it eats all cpu it can get. 
#   And apparently it is doing that in a non-multicore compatible way. GIL in the way?
#   POSSIBLY Fixed with System/Idler - we'll see if this works.

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
#from ANRV.Communication.CLI import CLIProtocol
from ANRV.Communication.JSONServer import JSONSplitter
from ANRV.Communication.JSONServer import JSONServer

from ANRV.System.Idler import Idler

from ANRV.Communication.Ping import Ping
from ANRV.Communication.Pong import Pong

from ANRV.Primitives import Frequency, Angle, WaypointList, Waypoint

from ANRV.Communication.Maestro import Maestro

from ANRV.Controls.Rudder import SimpleRudder as Rudder
from ANRV.Controls.Engine import SimpleEngine as Engine

config = {}
# Default settings:
config['idler.enable'] = True
config['idler.frequency'] = Frequency("IdlerFreq", 250)

config['ping.enable'] = True
config['ping.frequency'] = Frequency("Pingfreq", period=10)
config['pong.enable'] = True

config['console.echoer.enable'] = False

config['rudder.enable'] = True
config['engine.enable'] = True

config['maestro.enable'] = True

print "DEBUG.Server: Setting up Introspection Client."
Pipeline(
    Introspector(),
    TCPClient("127.0.0.1",55556)
).activate()


print "DEBUG.Server: Setting up Backplanes."
Backplane("I2C").activate()
Backplane("SENSORS").activate()
Backplane("CONTROLS").activate()

if config['console.echoer.enable']:
    print "DEBUG.Server: Activating ConsoleEchoer for I2C, CONTROLS and SENSORS."
    Pipeline(
        SubscribeTo("I2C"),
        SubscribeTo("CONTROLS"),
        SubscribeTo("SENSORS"),
        ConsoleEchoer(),
    ).activate()

if config['ping.enable']:
    print "DEBUG.Server: Adding Ping."
    Pipeline(
        SubscribeTo("CONTROLS"),
        Ping(frequency=config['ping.frequency']),
        PublishTo("CONTROLS")
    ).activate()

if config['pong.enable']:
    print "DEBUG.Server: Adding Pong."
    Pipeline(
        SubscribeTo("CONTROLS"),
        Pong(),
        PublishTo("CONTROLS")
    ).activate()

if config['idler.enable']:
    print "DEBUG.Server: Adding Idler."
    Pipeline(
        SubscribeTo("CONTROLS"),
        Idler(frequency=config['idler.frequency']),
        PublishTo("CONTROLS")
    ).activate()

if config['maestro.enable']:
    print "DEBUG.Server: Adding Maestro."
    Pipeline(
        SubscribeTo("CONTROLS"),
        Maestro(),
        ConsoleEchoer(),
        PublishTo("CONTROLS")
    ).activate()



if config['rudder.enable']:
    print "DEBUG.Server: Adding Simple Rudder Control Virtual Component (SRCVC)"
    Pipeline(
        SubscribeTo("CONTROLS"),
        Rudder(),
        PublishTo("CONTROLS")
    ).activate()

if config['engine.enable']:
    print "DEBUG.Server: Adding Simple Engine Control Virtual Component (SECVC)"
    Pipeline(
        SubscribeTo("CONTROLS"),
        Engine(),
        PublishTo("CONTROLS")
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
        SPLITTER = JSONSplitter(),
        #CE = ConsoleEchoer(),
        CP = JSONServer(),
        I2CP = PublishTo("I2C"),
        I2CS = SubscribeTo("I2C"),
        SENSORSP = PublishTo("SENSORS"),
        SENSORSS = SubscribeTo("SENSORS"),
        CONTROLSP = PublishTo("CONTROLS"),
        CONTROLSS = SubscribeTo("CONTROLS"),

        linkages = {("self", "inbox"): ("SPLITTER", "inbox"),
                    ("SPLITTER", "outbox"): ("CP", "inbox"),
                    ("CP", "outbox"): ("self", "outbox"),
                    ("self", "signal"): ("SPLITTER", "control"),
                    ("SPLITTER", "signal"): ("CP", "control"),
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
