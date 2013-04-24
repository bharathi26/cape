#!/usr/bin/env python

import sys

#
# First: Load configuration
#

import cape.system.configuration as configuration
configuration.setupConfig()

#
# Second: Setup the logger
#

from cape.system import logger as logger
logger.setuplogger()

#
# Third: The node's identity
#

from cape.system import identity as identity
identity.setupidentity()

if 'NODE' in configuration.Configuration.sections:
    NodeConfig = configuration.Configuration['NODE']
else:
    logger.systemcritical("No Node configuration found. Copy the sample or create one.")
    sys.exit(23)

#
# Fourth: Initialize and inspect all components
#

from cape.system import registry

logger.systeminfo("-"*42)
logger.systeminfo("cape ('%s') booting." % identity.SystemUUID)

registry.findModules()

logger.systeminfo("All modules loaded.")
#
# Fifth: Construct a base system and instantiate the Node
#

from cape.system.dispatcher import Dispatcher
from cape.system.registrycomponent import RegistryComponent

#from cape.Communication.JSONServer import JSONProtocol

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.ConnectedServer import FastRestartServer as ServerCore
from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Introspector import Introspector

# Kamaelia-style introspection; Due to change.
#port = 55555
#introspector = False
#
#if introspector:
#    logger.systeminfo("Connecting to introspector.")
#    Pipeline(
#        Introspector(),
#        TCPClient("localhost", 55556),
#        ).activate()

logger.systeminfo("Instantiating Dispatcher Component")
dispatcher = Dispatcher()
registry.Dispatcher = dispatcher

dispatcher.activate()

logger.systeminfo("Instantiating registry Component")
registrycomponent = RegistryComponent(dispatcher)
dispatcher.RegisterComponent(registrycomponent)

registry.Components.append(registrycomponent.name)

registry.Directory['dispatcher'] = dispatcher.name
registry.Directory['registry'] = registrycomponent.name

logger.systeminfo("Initializing Node from configuration.")
registrycomponent.initFromConfig()

#if NodeConfig['run.jsongate']:
#    # JSON gateway; Due to change in favour of AMQP node2node communication
#    logger.systeminfo("Setting up JSONServer on port %i" % port)
#
#    jsonserver = ServerCore(protocol=JSONProtocol, port=port)
#    jsonserver.activate()
#    dispatcher.RegisterComponent(jsonserver)

#
# Sixth: Run the assembled cape Node
#

if NodeConfig['run.allthreads']:
    logger.systeminfo("Starting all threads")
    scheduler.run.runThreads()
else:
    logger.systeminfo("Thats it. Terminating.")
    sys.exit(0)

#
# Fin
#
