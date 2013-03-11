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

from RAIN.System.Identity import SystemUUID
from RAIN.System.Registry import ComponentTemplates
from RAIN.System.RPCComponent import RPCComponent

Database = Connection()

#class MongoMixin(object):
#    def __init__(self):
#        print "#" * 23
#        self.loginfo("Database opened for '%s'" % self.name)
#        self.database = database[self.name]
        

class MongoComponent(RPCComponent):
    """
    Mongo Component

    Brings in mongodb connectivity.

    """

    unique = True

    directory_name = 'database'

    mongodb = Connection()

    def __init__(self, **kwargs):
        self.MR['rpc_getStatus'] = {}
        self.MR['rpc_getDatabases'] = {}
        self.MR['rpc_getCollection'] = {'name': [str, "Name of collection"],
                                        'create': [bool, "Wether to create a non existing collection (default: no)"]
                                        }

        super(MongoComponent, self).__init__()

        self.initDatabase()

    def initDatabase(self, createdb=False):
        """Initializes a single database for use with per component collections."""
        self.loginfo("Initializing Database.")
        self.database = self.mongodb['rain_%s' % SystemUUID]


    def rpc_getStatus(self):
        """Returns the current global mongodb connection status."""
        return (True, {'serverinfo': MongoComponent.mongodb.server_info(),
                       'hostname': MongoComponent.mongodb.host,
                       'port': MongoComponent.mongodb.port,
                       'db': self.database
                       }
                )

    def rpc_getDatabases(self):
        """Returns a list of mongodb's stored databases."""
        return (True, MongoComponent.mongodb.database_names())
    
    
    
    def rpc_getCollection(self, name, create=False):
        """Returns a specified collection for access"""
        self.loginfo("Got a collection request for '%s'" % name)
        if name in self.database.collection_names() or create:
            return (True, self.database[name])
        else:
            return (False, "Collection '%s' not found." % name)


ComponentTemplates["MongoComponent"] = [MongoComponent, "Mongo Component"]
