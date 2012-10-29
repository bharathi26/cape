#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      - Mongo capable class
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

from pymongo import Connection

from RAIN.System.Registry import ComponentTemplates
from RAIN.System.RPCComponent import RPCComponent, RPCComponentThreaded

class MongoMixin():
    """
    Mongo Component

    Brings in mongodb connectivity.

    """

    mongodb = Connection()

    def __init__(self, **kwargs):
        """Initializes this Configurable Component.
        Don't forget to call
            super(ConfigurableComponent, self).__init__()
        if you overwrite this.
        """
        self.MR['rpc_getStatus'] = {}
        self.MR['rpc_getDatabases'] = {}

    def rpc_getStatus(self):
        """Returns the current global mongodb connection status."""
        return (True, {'serverinfo': MongoMixin.mongodb.server_info(),
                       'hostname': MongoMixin.mongodb.host,
                       'port': MongoMixin.mongodb.port
                      }
               )

    def rpc_getDatabases(self):
        """Returns a list of mongodb's stored databases."""
        return (True, MongoMixin.mongodb.database_names())

class MongoComponent(RPCComponent, MongoMixin):
    def __init__(self, **kwargs):
        MongoMixin.__init__(self)
        RPCComponent.__init__(self)

class MongoComponentThreaded(RPCComponentThreaded, MongoMixin):
    def __init__(self, **kwargs):
        MongoMixin.__init__(self)
        RPCComponentThreaded.__init__(self)

ComponentTemplates["MongoComponent"] = [MongoComponent, "Mongo Component"]
