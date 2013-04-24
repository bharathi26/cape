#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#     - WebGetter
#    2013-03-13 19:33:05
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
from cape.messages import Message
from cape.system.rpccomponent import RPCComponentThreaded

import time, urllib

class WebGetter(RPCComponentThreaded):
    def __init__(self):
        #self.MR= {}
        super(WebGetter, self).__init__()
        self.Configuration['interval'] = 5
        self.Configuration['url'] = 'http://localhost'

    def _fetch(self):
        self.loginfo("Fetching resource '%s'" % self.url)
        self.resource = urllib.urlopen(self.url).read()
        

    def _feedSubscribers(self):
        self.loginfo("Feeding subscribers.")
        for subscriber, method in self.subscribers.iteritems():
            self.logdebug("Transmitting resource to subscriber function '%s'@'%s'." % (subscriber, method))
            msg = Message(sender=self.name,
                          recipient=subscriber,
                          func=method,
                          arg={'resource': self.resource})
            self.send(msg, "outbox")


    def main_prepare(self):
        """
        Method that is executed prior entering mainloop.
        Overwrite if necessary.
        """
        self.interval = self.Configuration['interval']
        self.url = self.Configuration['url']
        self.timer = time.time()

    def mainthread(self):
        """
        Overwrite this method with your blocking instructions.

        The call chain is thus:
        * Sync (if self.runsynchronized)
        * Your mainthread
        * RPC handling
         * In
         * Out
        * Rinse, repeat
        """
        if time.time() > self.timer + self.interval:
            self.timer = time.time()
            
            if self.url:
                self._fetch()
                if len(self.subscribers) > 0:
                    self._feedSubscribers()


Registry.ComponentTemplates["WebGetter"] = [WebGetter, "WebGetter to fetch a web resource in intervals"]