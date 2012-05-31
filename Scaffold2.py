#!/usr/bin/python3

from pprint import pprint

from ANRV.System import Registry
from ANRV.System import Dispatcher
from ANRV.System import RegistryComponent
from ANRV.System import ConfigurableComponent
from ANRV.System import RPCComponent
from ANRV.Controls import Engine
from ANRV.Controls import Rudder

print("Registered Component templates:\n")
pprint(Registry.ComponentTemplates)

print("Instantiating Dispatcher.\n")
dispatcher = Dispatcher.Dispatcher()
Registry.Components['Dispatcher'] = dispatcher

print("Instantiating Registry.\n")
registrycomponent = RegistryComponent.RegistryComponent()

print("Registered Components:\n")
pprint(Registry.Components)

print("Requesting creation of SimpleEngine.\n")
registrycomponent.rpc_createComponent("SimpleEngine")

print("Registered Components:\n")
pprint(Registry.Components)


