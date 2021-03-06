#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#      - Basic RPC Component Class
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

#import Axon
#from cape.system.registry import ComponentTemplates
#from cape.system.configuration import Configuration as configurationDB
#from configobj import ConfigObj

#from pprint import pprint

class ConfigurableComponent(object):
    """Basic configurable Component.

    TODO:
    * Documentation
    * ConfigObj!!
    * Finding of local config attributes
    * Validation of said attributes
    * Handling of attribute calls
    * RPC related stuff, later in the tree
    """


    def __init__(self):
        """Initializes this Configurable Component.
        Don't forget to call
            super(ConfigurableComponent, self).__init__()
        if you overwrite this.
        """
        self.Configuration = {}

    def HasConfiguration(self):
        # TODO: This one should probably validate an integrated configuration automatically
        # We need a defined configuration set per component, to enable that.
        # So, for now we just check for our basecomponent's attributes.. which is kind of lame

        # TODO: Sort these everywhere
        uuid = name = sysuuid = template = hname = hdesc = "Not found"
        try:
            c = self.Configuration['identity']
            uuid = c['uuid']
            name = c['name']
            sysuuid = c['systemuuid']
            template = c['template']
            hname = c['hname']
            hdesc = c['hdesc']
        except KeyError as err:
            errmsg = "%s '%s@%s (%s of %s)': '%s' '%s'" % (err, name, sysuuid, uuid, template, hname, hdesc)
            self.logerror(errmsg)
            return (False, errmsg)
        self.logdebug("Configuration found.")
        return True

    def GetConfiguration(self):
        """Returns the local Configuration Dictionary"""
        return self.Configuration

    def SetConfiguration(self, NewConfiguration):
        """Sets the local Configuration to a new Dictionary"""
        # TODO: Validation, Backup?
        self.Configuration.update(NewConfiguration)

    def WriteConfiguration(self):
        from cape.system.configuration import Configuration as ConfigurationDB

        """Stores this components configuration back in to the System's configuration database"""
        self.logdebug("Generating new configuration.")
        c = self.Configuration
        identity = {'uuid': str(self.uuid),
                    'name': self.name,
                    'systemuuid': self.systemuuid,
                    'template': self.template,
                    'hname': self.hname,
                    'hdesc': self.hdesc
                   }
        c['id'] = identity
        self.logdebug("Writing config.")
        ConfigurationDB[self.name] = c
        return True

    def ReadConfiguration(self):
        """Tries to obtain a configuration from the System's configuration database"""
        from cape.system.configuration import Configuration as ConfigurationDB

        try:
            self.Configuration = ConfigurationDB[self.name]

            return True
        except KeyError as e:
            errormsg = "No configuration found for '%s'" % self.name
            self.logwarn(errormsg)
            return (False, errormsg)

#ComponentTemplates["ConfigurableComponent"] = [ConfigurableComponent, "Configurable Component"]
