#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#    Prototype of the RAIN Operating Software
#    Copyright (C) 2011-2012 riot <riot@hackerfleet.org>
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

"""
Preliminary testing ZMQ gateway component.

The intention of this component is to integrate ZMQ as node-to-node communication protocol
into RAIN.
"""

from RAIN.Messages import Message
from RAIN.System import Identity
from RAIN.System import Registry
from RAIN.System.RPCComponent import RPCComponentThreaded

from time import sleep

import zmq

class DTNGate(RPCComponentThreaded):
    
    def __init__(self):
        self.MR['rpc_transmit'] = {'msg': [Message, 'Message to transmit via ZMQ.']}
        super(ZMQGate, self).__init__()
        
        # Schema:
        # {NodeUUID: ['IP-Address', ZMQ-Socket]}
        self.nodes = {Identity.SystemUUID: {'ip': '127.0.0.1', 'socket': None}}
                
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.bind("tcp://*:55555")
        
    def rpc_transmit(self, msg):
        if msg.recipientNode == Identity.SystemUUID:
            errmsg = "(Unsent) message to ourself received for distribution: '%s'" % msg
            self.logerror(errmsg)
            return (False, errmsg)
        
        if not self.nodes.has_key(msg.recipientNode):
            errmsg = "Node '%s' unknown."
            self.logwarning(errmsg)
            return (False, errmsg)
        
        socket = self.nodes[msg.recipientNode]['socket']
        
        if not socket:
            # Connection not already established, so connect and store for later
            return (False, "Node not connected. Why?")
            
        socket.send(msg)
        return True
    
    def _discoverNode(self, ip):
        socket = self.context.socket(zmq.REP)
        socket.connect('tcp://%s:55555' % ip)
        msg = Message(sendernode=Identity.SystemUUID, sender=self.name, recipient='DTNGate', func="discover", arg=str(self.systemregistry))
        socket.send(json.dumps(msg))
        
        self.nodes[msg.node]['socket'] = socket
        
    def _discoverNeighbours(self):
        """Should read in olsr's connected-nodes list. Fakes until we have such a thing."""
        self.neighbours = []
    
    
    def mainthread(self):
        msg = None
        msg = self.socket.recv(zmq.NOBLOCK)
        try:
            msg = json.loads(msg)
        except Exception as e:
            self.logerror("JSON decoding failed: '%s'" % e)
            
        if msg:
            self.logcritical(msg)
            if msg.recipient == "ZMQGate":
                if msg.func == "discover":
                    if msg.sendernode in self.nodes:
                        # Dual way sockets connected
                        self.loginfo("Node already connected: '%s'" % msg.sendernode)
                        msg = msg.response(True)
                    else:
                        msg = msg.response(str(self.systemregistry))
        else:
            self.logcritical("nothing. sleeping.")
            sleep(0.1)
            
Registry.ComponentTemplates['DTNGate'] = [DTNGate, "Node-to-node ØMQ Gateway"]