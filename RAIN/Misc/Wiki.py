#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - Wiki
#    2013-03-04 23:28:47
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

from RAIN.System import Registry
from RAIN.System.RPCComponent import RPCComponent
from RAIN.Messages import Message

class Wiki(RPCComponent):
    
    directory_name = "Wiki"
    
    def __init__(self):
        self.MR['rpc_getPage'] = {'pagename': [str, 'Name of Page to get']}
        self.MR['rpc_storePage'] = {'pagename': [str, 'Name of Page to store'],
                                    'content': [str, 'New Pagecontent']}
        self.MR['rpc_getCollection'] = {'collection': [object, 'Mongo Collection returnable']}
        super(Wiki, self).__init__()

        self.collection = None

    def rpc_getCollection(self, collection):
        self.loginfo("Got database access.")
        self.collection = collection

    def rpc_storePage(self, pagename, content):
        pass

    def rpc_getPage(self, pagename):
        if self.collection:
            return self.collection[pagename]
        else:
            return (False, "No database access.")

    def main_prepare(self):
        """
        Method that is executed prior entering mainloop.
        Overwrite if necessary.
        """
        msg = Message(recipient="RAIN.System.MongoComponent", func="getCollection", arg={'name': "wiki", 'create': True})
        self.send(msg, "outbox")

Registry.ComponentTemplates["Wiki"] = [Wiki, "Wiki Component"]