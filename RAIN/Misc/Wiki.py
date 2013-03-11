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
    
    directory_name = "wiki"
    
    def __init__(self):
        self.MR['rpc_getPage'] = {'pagename': [unicode, 'Name of Page to get']}
        self.MR['rpc_storePage'] = {'pagename': [unicode, 'Name of Page to store'],
                                    'content': [unicode, 'New Pagecontent']}
        self.MR['rpc_getCollection'] = {'collection': [object, 'Mongo Collection returnable']}
        super(Wiki, self).__init__()

    def handleResponse(self, msg):
        if msg.func == 'getCollection':
            self.logdebug("Database request returned.")

            if not msg.error:
                self.loginfo("Got database access.")
                self.collection = msg.arg
            else:
                self.logcritical("Database access request failed.")

    def rpc_storePage(self, pagename, content):
        if self.collection:
            page = {'pagename': pagename,
                    'content': content}
            self.collection.insert(page)
        else:
            return (False, "No database access.")

    def rpc_getPage(self, pagename):
        self.logdebug("Page requested: '%s'" % pagename)
        if self.collection:
            
            page = self.collection.find_one({'pagename': pagename})
            if page:
                self.loginfo("Returned page: '%s'." % pagename)
                return page['content']
            else:
                self.loginfo("Not yet existing page requested: '%s'." % pagename)
                return "EMPTY"
        else:
            return (False, "No database access.")

    def main_prepare(self):
        """
        Method that is executed prior entering mainloop.
        Overwrite if necessary.
        """
        self.logdebug("Requesting database access.")
        
        if "database" in self.directory:
            recipient = self.directory['database']
            self.logdebug("Database found: '%s'" % recipient)
            msg = Message(sender=self.name,
                          recipient=recipient,
                          func="getCollection",
                          arg={'name': "wiki", 'create': True})
            self.send(msg, "outbox")
            self.loginfo("Database access requested.")
        else:
            self.logerror("No db access.")
        

Registry.ComponentTemplates["Wiki"] = [Wiki, "Wiki Component"]