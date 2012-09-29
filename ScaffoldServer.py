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

    # CRUFT CRUFT CRUFT CRUFT CRUFT 
    TransducerPort = SerialPort.SerialPort()
    TransducerPort.Configuration.update({'device':'/dev/ttyUSB0', 'speed': 4800, 'readline': False})
    dispatcher.RegisterComponent(TransducerPort)
    Registry.Components[TransducerPort.name] = TransducerPort
    # CRUFT CRUFT CRUFT CRUFT CRUFT 

    Logging.systeminfo("Requesting creation of SerialPort")
    registrycomponent.rpc_createComponent("SerialPort")

    Logging.systeminfo("Requesting creation of Idler")
    registrycomponent.rpc_createComponent("Idler")

    Logging.systeminfo("Requesting creation of SimpleEngine")
    registrycomponent.rpc_createComponent("SimpleEngine")

    Logging.systeminfo("Requesting creation of Timer")
    registrycomponent.rpc_createComponent("Timer")

    Logging.systeminfo("Requesting creation of TkAdmin")
    registrycomponent.rpc_createComponent("TkAdmin")

    Logging.systeminfo("Requesting creation of WSGIGateway")
    registrycomponent.rpc_createComponent("WSGIGateway")


    Logging.systeminfo("Requesting creation of NMEABaseSensor")
    registrycomponent.rpc_createComponent("NMEABaseSensor")

    Logging.systeminfo("Requesting creation of MapRenderer")
    registrycomponent.rpc_createComponent("MapRenderer")

    Logging.systeminfo("Requesting creation of MSPTop")
    registrycomponent.rpc_createComponent("MSPTop")

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
