#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
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

from cape.system import registry
from cape.system import configuration
from cape.system.rpccomponent import RPCComponent
from cape.system.basecomponent import basecomponent


class RegistryComponent(RPCComponent):
    """
    The RegistryComponent allows for dealing with registry services.
    Among them are:
    * Creation of new components
    * Listing of available components and templates
    * Directory services

    More (like finding all available but not loaded components) will follow.
    """

    def rpc_createAllComponents(self):
        """Debugging Function to create all known components."""

        self.loginfo("Creating all known components.")
        for template in registry.ComponentTemplates:
            self._createComponent(template)
        return True

    def rpc_getConfigDB(self):
        """Instructs the configuration system to return the current configuration.."""

        self.loginfo("Getting configuration database.")
        return configuration.Configuration

    def rpc_storeConfigDB(self):
        """Instructs the configuration system to write back its DB."""

        self.loginfo("Storing configuration database.")
        return configuration.writeConfig()

    def rpc_createComponent(self, templatename):
        "RPC Wrapper"

        result, newcomponent = self._createComponent(templatename)
        if result:
            return (True, newcomponent.name)
        else:
            #TODO: UAGH, this is then supposed to be an error message.
            # Sort out return types here...
            return (False, newcomponent)


    def rpc_directory(self):
        """Returns our built directory of unique components.

        Components making use of any directory services should cache this.
        """

        return (True, self.directory)

    def rpc_listRegisteredComponents(self):
        """Returns the current list of registered (running!) components."""

        self.logdebug("RPC: List of registered (running) components requested")
        self.logdebug(registry.Components)
        return (True, registry.Components)

    def rpc_listRegisteredTemplates(self):
        """Returns the current list of available (producible via createComponent) components."""

        self.logdebug("RPC: List of registered component templates requested")
        self.logdebug(list(registry.ComponentTemplates.keys()))
        return (True, list(registry.ComponentTemplates.keys()))  # TODO: See above

    def initFromConfig(self):
        "Generates all configured components from the global Configuration"

        config = configuration.Configuration
        for sectionitem in config:
            section = config[sectionitem]

            # TODO: Structure this! so we don't accidentally create a monster
            if "template" in section:
                result, newcomponent = self._createComponent(section["template"], sectionitem)
                if result:
                    newcomponent.ReadConfiguration()
                else:
                    self.logerror("Couldn't create component '%s'." % sectionitem)

    def _createComponent(self, templatename, name=None):
        """Creates a new component and registers it with a dispatcher."""

        if self.dispatcher:
            if templatename in registry.ComponentTemplates:
                self.logdebug(
                    "Trying to create '%s' (Template '%s')." %
                    (name if name is not None else "Unnamed", templatename))
                try:
                    # Add templating info

                    template = registry.ComponentTemplates[templatename][0]


                    newcomponent = template()
                    newcomponent.template = templatename

                    # Add essential system components
                    newcomponent.systemregistry = self.name
                    newcomponent.systemdispatcher = self.dispatcher.name

                    # TODO: Actually, we might consider setting up static
                    # system parameters, too, since we're at it.
                    # (like SystemUUID et al)

                    #realname = newcomponent.name

                    if name:  # given name overwrites automatic
                        newcomponent.name = name

                    # Directory Services

                    # Unique Component lookup table

                    if template.directory_name:
                        directory_name = template.directory_name

                        if directory_name in self.directory:
                            msg = "Cannot register another unique '%s' in directory." % directory_name
                            self.logerror(msg)
                            return (False, msg)

                        self.loginfo("Creating directory entry for '%s'" % directory_name)
                        self.directory[directory_name] = newcomponent.name

                    # Component name register

                    registry.Components.append(newcomponent.name)

                    self.loginfo("Instantiated '%s' successfully, handing over to dispatcher." % newcomponent.name)
                    self.dispatcher.RegisterComponent(newcomponent)

                    return (True, newcomponent)
                except TypeError as e:
                    msg = "Unsupported initialization found in component '%s' - error: '%s'." % (templatename, e)
                    self.logerror(msg)
                    return (False, msg)

            else:
                self.logwarning("Cannot instantiate component '%s'. It is not registered as template." % templatename)
                return (False, "Component not found in templates")
        else:
            self.logerror("No dispatcher found! I can't run standalone")
            return (False, "No Dispatcher found to register component")

    def __init__(self, dispatcher):
        """Initializes the registry Component.

        Sets up base directory services."""

        self.dispatcher = dispatcher

        self.MR['rpc_createComponent'] = {'templatename': [str, 'Name of new component template']}
        self.MR['rpc_listRegisteredComponents'] = {}
        self.MR['rpc_listRegisteredTemplates'] = {}
        self.MR['rpc_storeConfigDB'] = {}
        self.MR['rpc_getConfigDB'] = {}
        self.MR['rpc_createAllComponents'] = {}
        self.MR['rpc_directory'] = {}
        super(RegistryComponent, self).__init__()

        # Set up Directory with base components
        self.directory.update({'dispatcher': dispatcher.name, 'registry': self.name})

        # TODO:
        # * Destruction of components
        # * Removal of destroyed components

#registry.ComponentTemplates['RegistryComponent'] = [RegistryComponent, "registry Component"]
