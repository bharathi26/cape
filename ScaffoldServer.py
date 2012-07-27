#!/usr/bin/python3

from ANRV.System import Logging
Logging.setupLogger()

Logging.systeminfo("-"*42)
Logging.systeminfo("ScaffoldServer booting.")

import sys

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.ConnectedServer import FastRestartServer as ServerCore
#from Kamaelia.Internet.TCPClient import TCPClient
#from Kamaelia.Chassis.Pipeline import Pipeline
#from Kamaelia.Util.Introspector import Introspector

from ANRV import Version
from ANRV.System import Identity
from ANRV.System import Configuration
from ANRV.System import Registry
from ANRV.System import Dispatcher
from ANRV.System import Idler
from ANRV.System import RegistryComponent
from ANRV.System import ConfigurableComponent
from ANRV.System import RPCComponent

from ANRV.Communication import JSONServer
from ANRV.Communication import WSGIGateway
from ANRV.Communication import Echo

from ANRV.Controls import Engine
from ANRV.Controls import Rudder
from ANRV.Controls import Timer

from ANRV.Interface import TkAdmin2

# STATIC PREPARATION

def main(args):
    if 'SERVER' in Configuration.Configuration.sections:
        ServerConfig = Configuration.Configuration['SERVER']
    else:
        Logging.systemcritical("No Server Configuration found. Copy the sample or create one.")
        sys.exit(23)

    introspector = False

    if introspector:
        Pipeline(
            Introspector(),
            TCPClient(55556),
        ).activate()

    Logging.systeminfo("Instantiating Dispatcher")
    dispatcher = Dispatcher.Dispatcher()
    Registry.Components['Dispatcher'] = dispatcher

    dispatcher.activate()

    Logging.systeminfo("Instantiating Registry")
    registrycomponent = RegistryComponent.RegistryComponent()
    dispatcher.RegisterComponent(registrycomponent)

    registrycomponent.activate()


    Logging.systeminfo("Requesting creation of Idler")
    registrycomponent.rpc_createComponent("Idler")

    Logging.systeminfo("Requesting creation of SimpleEngine")
    registrycomponent.rpc_createComponent("SimpleEngine")

    Logging.systeminfo("Requesting creation of Timer")
    registrycomponent.rpc_createComponent("Timer")

    Logging.systeminfo("Requesting creation of TkAdmin")
    registrycomponent.rpc_createComponent("TkAdmin2")

    Logging.systeminfo("Requesting creation of WSGIGateway")
    registrycomponent.rpc_createComponent("WSGIGateway")

    Logging.systeminfo("Setting up JSONServer on port 55555")
    jsonserver = ServerCore(protocol=JSONServer.JSONProtocol, port=55555)
    jsonserver.activate()

    if ServerConfig['runserver']:
        Logging.systeminfo("Starting all threads")
        scheduler.run.runThreads()
    else:
        Logging.systeminfo("Thats it. Terminating.")
        sys.exit(0)

if __name__ == "__main__":
    Logging.systeminfo("Booting up server scaffold. SystemName: %s" % Identity.SystemName)

    main(sys.argv)
