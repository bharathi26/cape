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
from ANRV.System.Registry import ComponentTemplates

from pprint import pprint

class ConfigurableComponent(Axon.Component.component):
    """Basic configurable Component.

    TODO:
    * Documentation
    * ConfigObj!!
    * Finding of local config attributes
    * Validation of said attributes
    * Handling of attribute calls
    * RPC related stuff, later in the tree
    """

    Configuration = {}

    def __init__(self):
        """Initializes this Configurable Component.
        Don't forget to call
            super(ConfigurableComponent, self).__init__()
        if you overwrite this.
        """
        super(ConfigurableComponent, self).__init__()

    def GetConfiguration(self):
        """Returns the local Configuration Dictionary"""
        return self.Configuration

    def SetConfiguration(self, NewConfiguration):
        """Sets the local Configuration to a new Dictionary"""
        self.Configuration = NewConfiguration

    def WriteConfiguration(self):
        """TODO: Should write the local configuration to the default location"""
        pass

ComponentTemplates["ConfigurableComponent"] = [ConfigurableComponent, "Configurable Component"]
