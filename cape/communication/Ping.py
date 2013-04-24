#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software - Useless Ping Component
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

from cape.system import registry
from cape.messages import Message
from cape.Primitives import Frequency
from cape.system.rpccomponent import RPCComponent

from time import time
from math import fsum

class Ping(RPCComponent):

    def __init__(self):
        self.MR['rpc_setinterval'] = {'interval': [float, "Interval of pings in seconds."]}
        self.MR['rpc_getlastpings'] = {}
        self.MR['rpc_getmeanrtt'] = {}
        self.MR['rpc_settarget'] = {'target': [str, "Name of new target component (must be a Pong component or something else implementing function 'ping')"],
                                    'node': [str, "Target node UUID"]}
                                            
        super(Ping, self).__init__()
        
        self.Configuration.update({'interval': 60.0,
                                   'target': None,
                                   'targetnode': None,
                                   'rttsize': 30,                                   
                                   }
                                  )
        self.lastping = 0
        self.count = 0
        self.rttlist = [0] * self.Configuration['rttsize'] # TODO: This has to be reflected in getmeanrtt
        self.verbosity = 1


    def rpc_setinterval(self, interval):
        self.Configuration['interval'] = float(interval)
        return True 
    
    def handleResponse(self, msg):     
        if msg.func == "ping":
            roundtrip = time() - float(msg.arg)
            self.loginfo("Pong from '%s' received. Roundtrip time: '%f'" % (msg.senderid, roundtrip))
            del(self.rttlist[0])
            self.rttlist.append(roundtrip)
        else:
            self.logwarning("Strange response received: '%s'" % msg)
    
    def rpc_getlastpings(self):
        """
        Returns the last 30 Pings
        """
        
        return self.rttlist
        
    def rpc_getmeanrtt(self):
        """
        Returns the median round trip time over the last 30 Pings.
        """
        
        meanrtt = fsum(self.rttlist[-10:]) / 10, fsum(self.rttlist[-20:]) / 20, fsum(self.rttlist) / 30
        return (True, meanrtt)        

    def rpc_settarget(self, target, node):
        """
        Sets this ping components target.
        """
        
        self.Configuration['target'] = str(target)
        self.Configuration['targetnode'] = str(node)
        return True

    def main_loop(self):
        """
        Loops and pings the configured pong component every configured interval.
        """
        if self.Configuration['target'] and (self.lastping + self.Configuration['interval'] < time()):
            self.logdebug("Pinging '%s'." % (self.Configuration['target']))
            self.lastping = time()
            # Time to act: Send a ping message to our pong counterpart
            self.count += 1
            
            pingmsg = Message(sender=self.name, 
                              recipient=self.Configuration['target'],
                              recipientnode=self.Configuration['targetnode'], 
                              func="ping", 
                              arg=None)
            self.send(pingmsg, "outbox")
            
            
Registry.ComponentTemplates['Ping'] = [Ping, "Ping component (see also: Pong)"]
