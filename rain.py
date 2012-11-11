#!/usr/bin/python2.7

import sys

import RAIN.System.Configuration as Configuration
Configuration.setupConfig()
from RAIN.System import Logger as Logger
Logger.setupLogger()

from RAIN.System import Identity as Identity
print "FOO"
Identity.setupIdentity()
print "BAR"

Logger.systeminfo("-"*42)
Logger.systeminfo("RAIN booting.")

from RAIN.Communication import *
from RAIN.Interface import *
from RAIN.Controls import *
from RAIN.Sensors import *
from RAIN.Autonomy import *


import RAIN.System.Dispatcher as Dispatcher
import RAIN.System.Registry as Registry
import RAIN.System.RegistryComponent as RegistryComponent

from RAIN.Communication.JSONServer import JSONProtocol

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.ConnectedServer import FastRestartServer as ServerCore
from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Introspector import Introspector

port = 55555
introspector = False

if 'SERVER' in Configuration.Configuration.sections:
    ServerConfig = Configuration.Configuration['SERVER']
else:
    Logger.systemcritical("No Server Configuration found. Copy the sample or create one.")
    sys.exit(23)

if introspector:
    Logger.systeminfo("Connecting to introspector.")
    Pipeline(
        Introspector(),
        TCPClient("localhost", 55556),
        ).activate()

Logger.systeminfo("Instantiating Dispatcher")
dispatcher = Dispatcher.Dispatcher()
Registry.Dispatcher = dispatcher

dispatcher.activate()

Logger.systeminfo("Instantiating Registry")
registrycomponent = RegistryComponent.RegistryComponent(dispatcher)
dispatcher.RegisterComponent(registrycomponent)

Registry.Components[dispatcher.name] = dispatcher
Registry.Components[registrycomponent.name] = registrycomponent

registrycomponent.initFromConfig()

Logger.systeminfo("Setting up JSONServer on port %i" % port)
jsonserver = ServerCore(protocol=JSONProtocol, port=port)
jsonserver.activate()
dispatcher.RegisterComponent(jsonserver)

if ServerConfig['runserver']:
    Logger.systeminfo("Starting all threads")
    scheduler.run.runThreads()
else:
    Logger.systeminfo("Thats it. Terminating.")
    sys.exit(0)
