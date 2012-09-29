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

from ANRV.System import *
from ANRV.Interface import *
from ANRV.Controls import *
from ANRV.Sensors import *
from ANRV.Communication import *
from ANRV.Autonomy import *


# STATIC PREPARATION

def main(args):
    print(Configuration.Configuration)
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
    dispatcher.activate()

    Logging.systeminfo("Instantiating Registry")
    registrycomponent = RegistryComponent.RegistryComponent(dispatcher)
    dispatcher.RegisterComponent(registrycomponent)

    Registry.Components[dispatcher.name] = dispatcher
    Registry.Components[registrycomponent.name] = registrycomponent

    registrycomponent.activate()
    registrycomponent.initFromConfig()

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
