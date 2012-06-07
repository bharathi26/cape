#!/usr/bin/python3

from pprint import pprint

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.ConnectedServer import FastRestartServer as ServerCore

from ANRV.System import Registry
from ANRV.System import Dispatcher
from ANRV.System import RegistryComponent
from ANRV.System import ConfigurableComponent
from ANRV.System import RPCComponent
from ANRV.Communication import JSONServer
from ANRV.Controls import Engine
from ANRV.Controls import Rudder


# METHS

def printComponents():
    print("Registered Templates:")
    pprint(Registry.ComponentTemplates)
    print("Registered Components:")
    pprint(Registry.Components)


def printRunning():
    print("Connected Components:\n")
    pprint(dispatcher.Components)

# STATIC PREPARATION

printComponents()

print("Instantiating Dispatcher.\n")
dispatcher = Dispatcher.Dispatcher()
Registry.Components['Dispatcher'] = dispatcher

dispatcher.activate()

printComponents()

print("Instantiating Registry.\n")
registrycomponent = RegistryComponent.RegistryComponent()
dispatcher.RegisterComponent(registrycomponent)

registrycomponent.activate()

printComponents()

print("Requesting creation of SimpleEngine.\n")
registrycomponent.rpc_createComponent("SimpleEngine")

printRunning()

print("Setting up JSONServer on port 55555.")
jsonserver = ServerCore(protocol=JSONServer.JSONProtocol, port=55555)
jsonserver.activate()

print(dispatcher)

print("DEBUG.Server: Starting all threads.")
scheduler.run.runThreads()
