#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
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

import Axon
#from ANRV.System.Registry import ComponentTemplates
from ANRV.System.Configuration import Configuration
from configobj import ConfigObj

from pprint import pprint

class ConfigurableComponent():
    """Basic configurable Component.

    TODO:
    * Documentation
    * ConfigObj!!
    * Finding of local config attributes
    * Validation of said attributes
    * Handling of attribute calls
    * RPC related stuff, later in the tree
    """

    Configuration = ConfigObj()

    def __init__(self):
        """Initializes this Configurable Component.
        Don't forget to call
            super(ConfigurableComponent, self).__init__()
        if you overwrite this.
        """

    def HasConfiguration(self):
        # TODO: This one should probably validate an integrated configuration automatically
        # We need a defined configuration set per component, to enable that.
        # So, for now we just check for our BaseComponent's attributes.. which is kind of lame
        uuid = sysname = hname = hdesc = "Not found"
        try:
            c = self.Configuration
            uuid = c['uuid']
            name = c['name']
            sysname = c['systemname']
            hname = c['hname']
            hdesc = c['hdesc']
        except KeyError as err:
            errmsg = "%s '%s@%s (%s)': '%s' '%s'" % (err, name, sysname, uuid, hname, hdesc)
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
        self.Configuration = NewConfiguration

    def WriteConfiguration(self):
        """Stores this components configuration back in to the System's configuration database"""
        self.logdebug("Generating new configuration.")
        c = self.Configuration
        c['uuid'] = self.uuid
        c['name'] = self.name
        c['hname'] = self.hname
        c['hdesc'] = self.hdesc
        c['systemname'] = self.systemname
        self.logdebug("Writing config.")
        Configuration[self.name] = c
        return True

    def ReadConfiguration(self):
        """Tries to obtain a configuration from the System's configuration database"""
        try:
            self.Configuration = Configuration[self.name]
            return True
        except KeyError as e:
            errormsg = "No configuration found for '%s'" % self.name
            self.logwarn(errormsg)
            return (False, errormsg)

#ComponentTemplates["ConfigurableComponent"] = [ConfigurableComponent, "Configurable Component"]
