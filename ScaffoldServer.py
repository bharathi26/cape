#!/usr/bin/python3

import sys
import logging
logging.basicConfig(format='%(asctime)s [%(levelname)5s]%(message)s', level=logging.DEBUG)
logging.info("Logging started")

from pprint import pprint

from Axon.Scheduler import scheduler
from Kamaelia.Chassis.ConnectedServer import FastRestartServer as ServerCore

from ANRV import Version
from ANRV.System import Identity
from ANRV.System import Registry
from ANRV.System import Dispatcher
from ANRV.System import Idler
from ANRV.System import RegistryComponent
from ANRV.System import ConfigurableComponent
from ANRV.System import RPCComponent

from ANRV.Communication import JSONServer
from ANRV.Communication import Echo

from ANRV.Controls import Engine
from ANRV.Controls import Rudder


# STATIC PREPARATION

def main(args):

    logging.info("Instantiating Dispatcher")
    dispatcher = Dispatcher.Dispatcher()
    Registry.Components['Dispatcher'] = dispatcher

    dispatcher.activate()

    logging.info("Instantiating Registry")
    registrycomponent = RegistryComponent.RegistryComponent()
    dispatcher.RegisterComponent(registrycomponent)

    registrycomponent.activate()


    logging.info("Requesting creation of Idler")
    registrycomponent.rpc_createComponent("Idler")

    logging.info("Requesting creation of SimpleEngine")
    registrycomponent.rpc_createComponent("SimpleEngine")

    logging.info("Setting up JSONServer on port 55555")
    jsonserver = ServerCore(protocol=JSONServer.JSONProtocol, port=55555)
    jsonserver.activate()

    logging.info("DEBUG.Server: Starting all threads")
    scheduler.run.runThreads()

if __name__ == "__main__":
    logging.info("Booting up server scaffold. SystemName: %s" % Identity.SystemName)

    main(sys.argv)
