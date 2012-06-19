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


import ANRV.System.Registry as Registry
from ANRV.System.RPCComponent import RPCComponent

class RegistryComponent(RPCComponent):
    """
    The RegistryComponent allows for dealing with registry services.
    Among them are:
    * Creation of new components
    * Listing of available components and templates

    More (like finding all available but not loaded components) will follow.
    """

    def rpc_createComponent(self, newcomponentname: [str, 'Name of new component template']):
        """Creates a new component and registers it with a dispatcher."""
        if "Dispatcher" in Registry.Components:
            if newcomponentname in Registry.ComponentTemplates:
                # TODO: Better addressing without too much added trouble
                # TODO: Initialize parameters correctly (How?)
                newcomponent = Registry.ComponentTemplates[newcomponentname][0]()

                Registry.Components[newcomponentname] = newcomponent

                Dispatcher = Registry.Components["Dispatcher"]
                Dispatcher.RegisterComponent(newcomponent)
                return True
            else:
                self.logwarning("Cannot instantiate component %s. It is not registered as template." % newcomponentname)
                return (False, "Component not found in templates")
        else:
            self.logerror("No dispatcher found! I can't run standalone")
            return (False, "No Dispatcher found to register component")

    def rpc_listRegisteredComponents(self, arg):
        """Returns the current list of registered (running!) components."""
        return list(Registry.Components.keys()) # TODO: Watch out, this is dangerous, when someone else writes here

    def rpc_listRegisteredTemplates(self, arg):
        """Returns the current list of available (producible via createComponent) components."""
        return list(Registry.ComponentTemplates.keys()) # TODO: See above

    # TODO:
    # * Destruction of components

Registry.ComponentTemplates['RegistryComponent'] = [RegistryComponent, "Registry Component"]
