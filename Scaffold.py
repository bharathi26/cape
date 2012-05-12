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


import sys, os
import hashlib
from re import escape
from time import gmtime, strftime

import ANRV.Version as Version

import Axon
from Axon.Scheduler import scheduler

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.ConnectedServer import ServerCore
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.Util.Introspector import Introspector
from Kamaelia.Util.Console import ConsoleEchoer

from ANRV.System.Idler import Idler
from ANRV.System.Recorder import Recorder

#from ANRV.Communication.I2C import I2CAdaptor
#from ANRV.Communication.CLI import CLIProtocol
from ANRV.Communication.JSONServer import JSONSplitter
from ANRV.Communication.JSONServer import JSONServer
from ANRV.Communication.Ping import Ping
from ANRV.Communication.Pong import Pong
from ANRV.Communication.Maestro import Maestro
from ANRV.Communication.Functions import *

from ANRV.Primitives import Frequency, Angle, WaypointList, Waypoint

from ANRV.Controls.Rudder import SimpleRudder as Rudder
from ANRV.Controls.Engine import SimpleEngine as Engine

from ANRV.Interface.SerialLCD import SerialLCD as LCD

from ANRV.Test.NewComponent import NewComponent

global config
config = {}

# Default settings:

# System
config['sys.name'] = "ANRV Development Scaffold " # + get_ip_address("eth0")
config['sys.shortname'] = "anrv-ds"
config['sys.hash'] = hashlib.sha224(config['sys.name'].encode("ASCII")).hexdigest()
print("DEBUG.Server: Identity: %s (%s) aka %s" % (config['sys.name'], config['sys.hash'], config['sys.shortname']))

config['idler.enable'] = True
config['idler.frequency'] = Frequency("IdlerFreq", 250)

config['recorder.folder'] = "/tmp/"
config['recorder.unified'] = True
config['recorder.hold_open'] = True
config['recorder.filename'] = strftime("%Y-%m-%d_", gmtime()) + config['sys.shortname'] + ".log"
print(config['recorder.filename'])

config['ping.enable'] = True
config['ping.frequency'] = Frequency("Pingfreq", period=60)
config['pong.enable'] = True

config['console.echoer.enable'] = False

config['rudder.enable'] = False
config['engine.enable'] = False

config['maestro.enable'] = False
config['maestro.device'] = "/dev/ttyACM0" # TODO: Autoconfigure this

config['lcd.enable'] = True
config['lcd.device'] = "/dev/ttyUSB0"
config['lcd.scrollspeed'] = Frequency("Scrollspeed", val=42)

config['newcomponent.enable'] = True

print("DEBUG.Server: Setting up Introspection Client.")
Pipeline(
    Introspector(),
    TCPClient("127.0.0.1",55556)
).activate()

print("DEBUG.Server: Setting up Control ackplane.")
Backplane("CONTROLS").activate()

if config['console.echoer.enable']:
    print("DEBUG.Server: Activating ConsoleEchoer for I2C, CONTROLS and SENSORS.")
    Pipeline(
        SubscribeTo("CONTROLS"),
        ConsoleEchoer(),
    ).activate()

if config['ping.enable']:
    print("DEBUG.Server: Adding Ping.")
    Pipeline(
        SubscribeTo("CONTROLS"),
        Ping(frequency=config['ping.frequency']),
        PublishTo("CONTROLS")
    ).activate()

if config['pong.enable']:
    print("DEBUG.Server: Adding Pong.")
    Pipeline(
        SubscribeTo("CONTROLS"),
        Pong(),
        PublishTo("CONTROLS")
    ).activate()

if config['idler.enable']:
    print("DEBUG.Server: Adding Idler.")
    Pipeline(
        SubscribeTo("CONTROLS"),
        Idler(frequency=config['idler.frequency']),
        PublishTo("CONTROLS")
    ).activate()

if config['maestro.enable']:
    print("DEBUG.Server: Adding Maestro.")
    Pipeline(
        SubscribeTo("CONTROLS"),
        Maestro(config['maestro.device']),
        ConsoleEchoer(),
        PublishTo("CONTROLS")
    ).activate()

if config['rudder.enable']:
    print("DEBUG.Server: Adding Simple Rudder Control Virtual Component (SRCVC)")
    Pipeline(
        SubscribeTo("CONTROLS"),
        Rudder(),
        PublishTo("CONTROLS")
    ).activate()

if config['engine.enable']:
    print("DEBUG.Server: Adding Simple Engine Control Virtual Component (SECVC)")
    Pipeline(
        SubscribeTo("CONTROLS"),
        Engine(),
        PublishTo("CONTROLS")
    ).activate()

if config['lcd.enable']:
    print("DEBUG.Server: Adding LCD.")
    Pipeline(
        SubscribeTo("CONTROLS"),
        LCD(device=config['lcd.device'], scrollSpeed=config['lcd.scrollspeed']),
        PublishTo("CONTROLS")
    ).activate()

if config['newcomponent.enable']:
    print("DEBUG.Server: Adding new component.")
    Pipeline(
        SubscribeTo("CONTROLS"),
        NewComponent(),
        PublishTo("CONTROLS")
    ).activate()

print("DEBUG.Server: Preparing CLI protocol.")
def CLI(*argv, **argd):
    # TODO: This is an ugly CRUFT thats probably not supposed to live long.
    # The linkages and messageboxes could be optimized, i don't yet know how. 
    return Graphline(
        SPLITTER = JSONSplitter(),
        #CE = ConsoleEchoer(),
        CP = JSONServer(),
#        I2CP = PublishTo("I2C"),
#        I2CS = SubscribeTo("I2C"),
#        SENSORSP = PublishTo("SENSORS"),
#        SENSORSS = SubscribeTo("SENSORS"),
        CONTROLSP = PublishTo("CONTROLS"),
        CONTROLSS = SubscribeTo("CONTROLS"),

        linkages = {("self", "inbox"): ("SPLITTER", "inbox"),
                    ("SPLITTER", "outbox"): ("CP", "inbox"),
                    ("CP", "outbox"): ("self", "outbox"),
                    ("self", "signal"): ("SPLITTER", "control"),
                    ("SPLITTER", "signal"): ("CP", "control"),
                    ("CP", "signal"): ("self", "control"),
 #                   ("CP", "i2cout"): ("I2CP", "inbox"),
 #                   ("I2CS", "outbox"): ("CP", "i2cin"),
 #                   ("CP", "sensorsout"): ("SENSORSP", "inbox"),
 #                   ("SENSORSP", "outbox"): ("CP", "sensorsin"),
                    ("CP", "controlsout"): ("CONTROLSP", "inbox"),
                    ("CONTROLSS", "outbox"): ("CP", "controlsin")}
    )

print("DEBUG.Server: Setting up CLI server on port 55555.")
ServerCore(protocol = CLI, port=55555).activate()

print("DEBUG.Server: Starting all threads.")
scheduler.run.runThreads()
