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

import jsonpickle
import zmq

from collections import deque

class ZMQConnector(RPCComponentThreaded, NodeConnector):
    """Exemplary and experimental ZMQ node interconnector class."""

    routeraddress = "192.168.1.42" # Fixed for testing purposes.
    separator = b"\r\n"

    def __init__(self):
        self.loginfo('ZMQConnector initializing')
        self.MR['rpc_transmit'] = {'msg':
                                   [Message, 'Message to transmit via ZMQ.']}
        self.MR['rpc_discoverNode'] = {'ip': [str, 'IP to discover']}
        self.MR['rpc_listconnectedNodes'] = {}
        self.MR['rpc_disconnectNode'] = {'node':
                                         [str, 'Node UUID to disconnect.']}
        self.MR['rpc_disconnectNodes'] = {}
        super(ZMQConnector, self).__init__()
        self.logdebug('ZMQConnector configuring')
        self.Configuration.update({
                                   'routeraddress': '127.0.0.1',
                                  })

        self.buflist = deque()

        # Schema:
        # {'ip': ZMQ-Socket}}
        self.probednodes = {}
        
        self.nodes = {} #Identity.SystemUUID: {'ip': '127.0.0.1', 'registry': '', 'dispatcher': '', 'socket': None}}
        
        self.url = "tcp://%s:55555" % self.Configuration['routeraddress']

        self.listening = False

        self.loginfo("Setting up socket '%s'" % self.url)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        try:
            self.socket.bind(self.url)
            self.listening = True
            self.loginfo("Socket bound")
        except zmq.core.error.ZMQError:
            self.logcritical("Couldn't bind socket: Already in use!")
        self.logdebug("Init complete!")

    def rpc_transmit(self, msg):
        if msg.recipientNode == str(Identity.SystemUUID):
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
        """Discovers a Node at a given IP."""
        
        if ip not in self.probednodes:
            msg = "Probing new node: '%s'" % ip
            self.logdebug(msg)
            self._discoverNode(ip)
            return True, msg
        else:
            self.logerror("Node has already been discovered: '%s'" % ip)
            return False
        
    def rpc_disconnectNode(self, node):
        """Disconnects a given Node including announcement of its disconnection."""
        
        return self._disconnectNode(node)    
    
    def rpc_disconnectNodes(self):
        """Disconnects from all nodes after sending an announcement to each."""
        
        result = True
        
        for node in self.nodes:
            result = result and self._disconnectNode(node)

        return result

    def _disconnectNode(self, node, announce=True):
        if node not in self.nodes:
            return (False, "Node not connected.")
        
        socket = self.nodes[node]['socket']
        if announce:
            msg = Message(sendernode=str(Identity.SystemUUID),
                          sender=self.name,
                          recipient='ZMQConnector',
                          func='disconnect')
            socket.send(jsonpickle.encode(msg))
        
        socket.close()
        del(self.nodes[node])
        
        return True               

    def _discoverNode(self, ip):
        self.loginfo("Discovering node '%s'" % ip)
        socket = self.context.socket(zmq.DEALER)
        socket.connect('tcp://%s:55555' % ip)
        # TODO: Is this smart, sending discovery data upon first message?
        # Maybe better in the reply...
        msg = Message(sendernode=str(Identity.SystemUUID),
                      sender=self.name,
                      recipient='ZMQConnector',
                      func="discover",
                      arg={'ip': self.Configuration['routeraddress'],
                           'registry': str(self.systemregistry),
                           'dispatcher': str(self.systemdispatcher),
                           }
                      )
        self.logdebug("Discovery message: '%s'" % msg)
        socket.send(jsonpickle.encode(msg))
        
        self.probednodes[ip] = socket
        
        self.logdebug("Discovery sent to '%s'" % ip)

    def rpc_listconnectedNodes(self):
        return str(self.nodes.keys())

    def mainthread(self):
        msg = incoming = None        
        
        # If listening, collect incoming buffer
        if self.listening:
            try:
                incoming = self.socket.recv(zmq.NOBLOCK)
                self.logdebug("Received '%s'" % incoming)
            except zmq.core.error.ZMQError as e:
                if not "Resource temporarily unavailable" in str(e):
                    self.logerror(e)
                    
        # Split buffer, if we have some
        if incoming:
            # new piece of a message arrived
            parts = incoming.split(ZMQConnector.separator)
            
            self.logdebug("Length of incoming: %i" % len(parts))
            
            for part in parts:
                self.logdebug(part)
                if len(part) > 0:
                    self.buflist.append(part.rstrip(ZMQConnector.separator))
        
        # If there are messages, decode and process them
        if len(self.buflist) > 0:
            jsonmsg = self.buflist.popleft()
            try:
                msg = jsonpickle.decode(jsonmsg)
            except Exception as e:
                self.logdebug(jsonmsg)
                self.logerror("JSON decoding failed: '%s'" % e)

            if msg:
                self.loginfo("Analysing input: '%s'" % msg )

                if msg.recipient in ("ZMQConnector", self.name):
                    if msg.func == "disconnect":
                        if msg.sendernode in self.nodes:
                            self.loginfo("Disconnect announcement received from '%s'@'%s'" % (msg.sendernode, 
                                                                                              self.nodes[msg.sendernode]['ip']))
                            self._disconnectNode(msg.sendernode)
                        else:
                            self.logwarning("Disconnect announcement from unconnected node received '%s', args: '%s'" % (msg.sendernode,
                                                                                                                         msg.arg))
                    if msg.func == "discover":
                        node = msg.arg
                        
                        if msg.type == 'request':
                            self.loginfo("Probe request received from '%s' " % node['ip'])
                            # We're being probed! Store request details.
                            
                            self.nodes[msg.sendernode] = {'ip': node['ip'],
                                                      'registry': node['registry'],
                                                      'dispatcher': node['dispatcher'],
                                                      }
                            if node['ip'] not in self.probednodes:
                                self.loginfo("Uninitiated probe by '%s' - discovering in reverse." % (node['ip']))
                                self._discoverNode(node['ip'])
                            else:
                                self.loginfo("Probe returned storing socket for '%s'" % (node['ip']))
                                print "Assigning socket"
                                self.nodes[msg.sendernode]['socket'] = self.probednodes[node['ip']]
                                print "Generating reply."
                                reply = msg.response({'ip': self.Configuration['routeraddress']})
                                print "Sending reply"
                                self.nodes[msg.sendernode]['socket'].send(jsonpickle.encode(reply))
                                
                        else:
                            # Hm, a response! This is the last packet in our discovery chain.
                            self.loginfo("Connected to '%s'" % (node['ip']))
                            self.nodes[msg.sendernode]['connected'] = True
                                
                # Oh, nothing for us, but someone else.
                # TODO: Now, we'd better check for security and auth.
                elif msg.recipientnode == Identity.SystemUUID:
                    self.loginfo("Publishing Message from '%s': '%s'" % (msg.sendernode, msg))
                    self.send(msg, "outbox")
                else:
                    self.logwarning("Message for another node received - WTF?!")
        else:
            sleep(0.1)

Registry.ComponentTemplates['ZMQConnector'] = [ZMQConnector, "Node-to-node ØMQ Connector"]
