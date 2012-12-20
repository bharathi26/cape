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
from RAIN.System.NodeConnector import NodeConnector

from time import sleep

import json
import zmq


class ZMQConnector(RPCComponentThreaded, NodeConnector):
    """Exemplary and experimental ZMQ node interconnector class."""

    routeraddress = "192.168.1.42" # Fixed for testing purposes.

    def __init__(self):
        self.MR['rpc_transmit'] = {'msg':
                                   [Message, 'Message to transmit via ZMQ.']}
        super(ZMQConnector, self).__init__()

        # Schema:
        # {NodeUUID: ['IP-Address', ZMQ-Socket]}
        self.probednodes = {}
        self.nodes = {Identity.SystemUUID: {'ip': '127.0.0.1', 'socket': None}}

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind("tcp://%s:55555" % ZMQConnector.routeraddress)

    def rpc_transmit(self, msg):
        if msg.recipientNode == Identity.SystemUUID:
            errmsg = "(Unsent) message to ourself received for distribution: '%s'" % msg
            self.logerror(errmsg)
            return (False, errmsg)

        if not msg.recipientNode in self.nodes:
            errmsg = "Node '%s' unknown."
            self.logwarning(errmsg)
            return (False, errmsg)

        socket = self.nodes[msg.recipientNode]['socket']

        if not socket:
            # Connection not already established, so connect and store for later
            return (False, "Node not connected. Why?")

        socket.send(msg)
        return True

    def rpc_discoverNode(self, ip):
        if ip not in self.probednodes:
            msg = "Probing new node: '%s'" % ip
            self.logdebug(msg)
            self._discoverNode(ip)
            return True, msg
        else:
            self.logerror("Node has already been discovered: '%s'" % ip)
            return False

    def _discoverNode(self, ip):
        socket = self.context.socket(zmq.DEALER)
        socket.connect('tcp://%s:55555' % ip)
        # TODO: Is this smart, sending discovery data upon first message?
        # Maybe better in the reply...
        msg = Message(sendernode=Identity.SystemUUID,
                      sender=self.name,
                      recipient='ZMQConnector',
                      func="discover",
                      arg={'ip': ZMQConnector.routeraddress,
                           'registry': str(self.systemregistry),
                           'dispatcher': str(self.systemdispatcher),
                           }
                      )
        socket.send(json.dumps(msg))

        self.probednodes[ip] = socket

    def mainthread(self):
        msg = None
        msg = self.socket.recv(zmq.NOBLOCK)
        try:
            msg = json.loads(msg)
        except Exception as e:
            self.logerror("JSON decoding failed: '%s'" % e)

        if msg:
            self.logcritical(msg)
            if (msg.recipient == "ZMQConnector" and msg.type == 'request'):
                if msg.func == "discover":
                    if msg.arg['ip'] in self.probednodes:
                        # Node is already known.
                        # This boils down to: We probed it, it now probes us
                        self.nodes[msg.sendernode] = {'ip': msg.arg['ip'], 
                                                      'socket': self.probednodes[msg.arg['ip']]}
                        
                        
                        
                        
                    if msg.sendernode in self.nodes:
                        self.loginfo("Node already connected: '%s'" % msg.sendernode)
                        #msg = msg.response(True)
                    else:
                        msg = msg.response(str(self.systemregistry))
                        self._discoverNode(msg.arg['ip'])
                        
                # Oh, nothing for us, but someone else.
                # TODO: Now, we'd better check for security and auth.
                self.loginfo("Publishing Message from '%s': '%s'" % (msg.sendernode, msg))
                self.send(msg, "outbox")
        else:
            self.logcritical("nothing. sleeping.")
            sleep(0.1)

Registry.ComponentTemplates['ZMQConnector'] = [ZMQConnector, "Node-to-node ØMQ Connector"]