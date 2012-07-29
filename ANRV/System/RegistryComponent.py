#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#     - RegistryComponent
#    Copyright (C) 2011-2012  riot <riot@hackerfleet.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from ANRV.System import Registry
from ANRV.System.RPCComponent import RPCComponent

class RegistryComponent(RPCComponent):
    """
    The RegistryComponent allows for dealing with registry services.
    Among them are:
    * Creation of new components
    * Listing of available components and templates

    More (like finding all available but not loaded components) will follow.
    """


    def rpc_createComponent(self, templatename):
        """Creates a new component and registers it with a dispatcher."""
        args = {'templatename': [str, 'Name of new component template']}

        # TODO: The next check is somewhat ugly.
        if "Dispatcher" in Registry.Components:
            if templatename in Registry.ComponentTemplates:
                # TODO: Better addressing without too much added trouble
                # TODO: Initialize parameters correctly (How?)
                newcomponent = Registry.ComponentTemplates[templatename][0]()
                newcomponent.systemregistry = self.name

                realname = newcomponent.name

                Registry.Components[realname] = newcomponent

                self.loginfo("Instantiated '%s' successfully, handing over to dispatcher." % newcomponent.name)
                Dispatcher = Registry.Components["Dispatcher"]
                Dispatcher.RegisterComponent(newcomponent)
                return True
            else:
                self.logwarning("Cannot instantiate component %s. It is not registered as template." % templatename)
                return (False, "Component not found in templates")
        else:
            self.logerror("No dispatcher found! I can't run standalone")
            return (False, "No Dispatcher found to register component")

    def rpc_listRegisteredComponents(self):
        """Returns the current list of registered (running!) components."""
        self.logdebug("RPC: List of registered (running) components requested")
        self.logdebug(Registry.Components)
        return (True, list(Registry.Components.keys())) # TODO: Watch out, this is dangerous, when someone else writes here

    def rpc_listRegisteredTemplates(self):
        """Returns the current list of available (producible via createComponent) components."""
        self.logdebug("RPC: List of registered component templates requested")
        self.logdebug(list(Registry.ComponentTemplates.keys()))
        return (True, list(Registry.ComponentTemplates.keys())) # TODO: See above

    def rpc_test(self, foo, bar):
        print(foo, bar)
        return (True, (bar, foo))

    def __init__(self):
        self.MR['rpc_createComponent'] = {'default': [str, 'Name of new component template']}
        self.MR['rpc_listRegisteredComponents'] = {}
        self.MR['rpc_listRegisteredTemplates'] = {}
        self.MR['rpc_test'] = {'foo': [int, 'foo int arg'],
                               'bar': [float, 'bar float arg']}
        super(RegistryComponent, self).__init__()


    # TODO:
    # * Destruction of components

Registry.ComponentTemplates['RegistryComponent'] = [RegistryComponent, "Registry Component"]
