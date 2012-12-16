#!/usr/bin/python2.7

import sys

#
# First: Load Configuration
#

import RAIN.System.Configuration as Configuration
Configuration.setupConfig()

#
# Second: Setup the Logger
#

from RAIN.System import Logger as Logger
Logger.setupLogger()

#
# Third: The node's Identity
#

from RAIN.System import Identity as Identity
Identity.setupIdentity()

#
# Fourth: Initialize and inspect all components
#
Logger.systeminfo("-"*42)
Logger.systeminfo("RAIN booting.")

from RAIN.System import *
from RAIN.Communication import *
from RAIN.Interface import *
from RAIN.Controls import *
from RAIN.Sensors import *
from RAIN.Autonomy import *
from RAIN.Test import *

#
# Fifth: Construct a base system and instantiate the Node
#

import RAIN.System.Dispatcher as Dispatcher
import RAIN.System.Registry as Registry
import RAIN.System.RegistryComponent as RegistryComponent

from RAIN.Communication.JSONServer import JSONProtocol

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.ConnectedServer import FastRestartServer as ServerCore
from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Introspector import Introspector

# Kamaelia-style introspection; Due to change.
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

Logger.systeminfo("Initializing Node from Configuration.")
registrycomponent.initFromConfig()

# JSON gateway; Due to change in favour of AMQP node2node communication
Logger.systeminfo("Setting up JSONServer on port %i" % port)
jsonserver = ServerCore(protocol=JSONProtocol, port=port)
jsonserver.activate()
dispatcher.RegisterComponent(jsonserver)

#
# Sixth: Run the assembled RAIN Node
#

if ServerConfig['runserver']:
    Logger.systeminfo("Starting all threads")
    scheduler.run.runThreads()
else:
    Logger.systeminfo("Thats it. Terminating.")
    sys.exit(0)

#
# Fin
#
