#!/usr/bin/python3



import sys, getopt

opts = []
config = ""
debug = 10
port = 55555
introspector = False

# parse command line options
try:
    opts, args = getopt.getopt(sys.argv[1:], "hc:d:p:", ["help", "config", "debug", "port"])
except getopt.error as msg: 
    print "OptParseFail"
    fail = True
    sys.exit(23)


# process options
for o, a in opts:
    if o in ("-h", "--help"):
        print "-h help -c configfile -d debuglevel(0-50) -p port"
        sys.exit(1)
    if o in ("-c", "--config"):
        config = a
    if o in ("-d", "--debug"):
        debug = int(a)
    if o in ("-p", "--port"):
        port = int(a)

from RAIN.System import Logging
Logging.setupLogger(debug)

Logging.systeminfo("-"*42)
Logging.systeminfo("ScaffoldServer booting.")

from RAIN.System import Configuration
Logging.systeminfo("Loading Configuration.")
Configuration.setupConfig(config)

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.ConnectedServer import FastRestartServer as ServerCore
from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Introspector import Introspector

from RAIN import Version

from RAIN.System import *
from RAIN.Interface import *
from RAIN.Controls import *
from RAIN.Sensors import *
from RAIN.Communication import *
from RAIN.Autonomy import *


# STATIC PREPARATION

def main():
    if 'SERVER' in Configuration.Configuration.sections:
        ServerConfig = Configuration.Configuration['SERVER']
    else:
        Logging.systemcritical("No Server Configuration found. Copy the sample or create one.")
        sys.exit(23)

    if introspector:
        Logging.systeminfo("Connecting to introspector.")
        Pipeline(
            Introspector(),
            TCPClient("localhost", 55556),
        ).activate()

    Logging.systeminfo("Instantiating Dispatcher")
    dispatcher = Dispatcher.Dispatcher()
    Registry.Dispatcher = dispatcher
    dispatcher.activate()

    Logging.systeminfo("Instantiating Registry")
    registrycomponent = RegistryComponent.RegistryComponent(dispatcher)
    dispatcher.RegisterComponent(registrycomponent)

    Registry.Components[dispatcher.name] = dispatcher
    Registry.Components[registrycomponent.name] = registrycomponent

    registrycomponent.activate()
    registrycomponent.initFromConfig()

    Logging.systeminfo("Setting up JSONServer on port %i" % port)
    jsonserver = ServerCore(protocol=JSONServer.JSONProtocol, port=port)
    jsonserver.activate()
    dispatcher.RegisterComponent(jsonserver)

    if ServerConfig['runserver']:
        Logging.systeminfo("Starting all threads")
        scheduler.run.runThreads()
    else:
        Logging.systeminfo("Thats it. Terminating.")
        sys.exit(0)

if __name__ == "__main__":
    Logging.systeminfo("Booting up server scaffold. SystemName: %s" % Identity.SystemName)

    main()
