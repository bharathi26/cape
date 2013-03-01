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
Preliminary testing ZMQ-based DTN gateway component.

The intention of this component is to integrate ZMQ as node-to-node communication protocol
into RAIN.
"""

from RAIN.Messages import Message
from RAIN.System import Identity
from RAIN.System import Registry
from RAIN.System.RPCComponent import RPCComponentThreaded
from RAIN.System.NodeConnector import NodeConnector

from time import sleep, time

import jsonpickle
import zmq

from collections import deque

class DTNGate(RPCComponentThreaded, NodeConnector):
    """Exemplary and experimental ZMQ node interconnector class."""

    separator = b"\r\n"

    def __init__(self):
        self.loginfo('DTNGate initializing')
        self.MR['rpc_transmit'] = {'msg':
                                   [Message, 'Message to transmit via ZMQ.']}
        self.MR['rpc_discoverNode'] = {'ip': [str, 'IP to discover']}
        self.MR['rpc_listconnectedNodes'] = {}
        self.MR['rpc_disconnectNode'] = {'node':
                                         [str, 'Node UUID to disconnect.']}
        self.MR['rpc_disconnectNodes'] = {}
        self.MR['rpc_test'] = {}

        super(DTNGate, self).__init__()
        self.logdebug('DTNGate configuring')

        self.Configuration.update({
                                   'routeraddress': '127.0.0.1',
                                  })

        self.listening = False
        self.buflist = deque()

        # Schema:
        # {'ip': ZMQ-Socket}
        self.probednodes = {}
        # {'ip': Probedata}
        self.probes = {}

        self.nodes = {}  # Identity.SystemUUID: {'ip': '127.0.0.1', 'registry': '', 'dispatcher': '', 'socket': None, 'timeout': int, 'lastping': int}}

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)

        self.logdebug("Init complete!")

    def rpc_test(self):
        return self._discoverNode("192.168.1.185")


    def main_prepare(self):
        """Opens the listener socket."""

        # TODO: Maybe make this a function call thats available via RPC, too
        # Since we might want to change the socket after e.g. reconfiguration
        self.url = "tcp://%s:55555" % self.Configuration['routeraddress']

        self.loginfo("Setting up socket '%s'" % self.url)
        try:
            self.socket.bind(self.url)
            self.listening = True
            self.loginfo("Socket bound")
        except zmq.core.error.ZMQError:
            self.logcritical("Couldn't bind socket: Already in use!")

    def mainthread(self):
        # TODO: Check if incoming packets are coming from a stale connection
        #   If so: we have to await rediscovery before transmitting back our packets
        msg = jsonmsg = None

        # If listening, collect incoming buffer
        if self.listening:
            try:
                senderid = self.socket.recv(zmq.NOBLOCK)
                # self.logdebug("Received '%s'" % incoming)
                jsonmsg = self.socket.recv(zmq.NOBLOCK)

            except zmq.core.error.ZMQError as e:
                if not "Resource temporarily unavailable" in str(e):
                    self.logerror(e)

            # Split buffer, if we have some
            # TODO: This all is probably not very necessary and should be kicked out
            #if incoming:
            #    # new piece of a message arrived
            #    parts = incoming.split(DTNGate.separator)

            # If there are messages, decode and process them
            if jsonmsg:
                try:
                    msg = jsonpickle.decode(jsonmsg)
                except Exception as e:
                    self.logdebug(jsonmsg)
                    self.logerror("JSON decoding failed: '%s'" % e)    

                self.logdebug('Received a message')

                # Check if we have to forward or process the message locally
                if msg.recipient in ("DTNGate", self.name):
                    self._handleMessage(msg)
                elif msg.recipientnode == str(Identity.SystemUUID):
                    # Oh, nothing for us, but someone else on this node.
                    # TODO: Now, we'd better check for security and auth.
                    # TODO: We need to check wether the socket really is associated with the stored Identity
                    # This is really important to make sure nobody injects messages with wrong sender id
                    # This can be done using the ZMQ.Identity, which gets sent first by the ZMQ Socket
                    self.loginfo("Publishing Message from '%s': '%s'" % (msg.sendernode, msg))
                    self.send(msg, "outbox")
                else:
                    self.logwarning("Message for another node received - WTF?!")

            self._pingNodes()
        else:
            self.logdebug("Sleeping.")
            sleep(0.1)

    def _handleMessage(self, msg):
        """
        Handle messages for this DTNGate component.
        """

        sendernode = msg.sendernode

        if sendernode in self.nodes:
            # Any message from a node resets the ping interval 
            self.nodes[sendernode]['lastping'] = time()

        self.logdebug("Analysing input: '%s'" % msg)

        if msg.func == "ping":
            if msg.type == "request":
                self.loginfo("Got a ping from '%s'." % sendernode)

                response = msg.response(time())
                if sendernode in self.nodes: 
                    self.loginfo("Replying to ping request.")
                    self.nodes[sendernode]['pingcount'] = 0
                    self.nodes[sendernode]['socket'].send(jsonpickle.encode(response))
                else:
                    self.logerror("Can't respond to ping request, no socket!")
            if msg.type == "response":
                self.loginfo("Got a pong from '%s'." % sendernode)
                if sendernode in self.nodes:
                    self.nodes[sendernode]['pingcount'] = 0


        if msg.func == "disconnect":
            if sendernode in self.nodes:
                self.loginfo("Disconnect announcement received from '%s'@'%s'" % (sendernode,
                                                                                  self.nodes[sendernode]['ip']))
                self._disconnectNode(sendernode)
            else:
                self.logwarning("Disconnect announcement from unconnected node received '%s', args: '%s'" % (sendernode,
                                                                                                             msg.arg))
        if msg.func == "discover":
            node = msg.arg
            ip = node['ip']

            if msg.type == 'request':
                self.loginfo("Probe request received from '%s' " % node['ip'])
                # We're being probed! Store request details.

                self.probes[ip] = {'uuid': sendernode,
                                   'registry': node['registry'],
                                   'dispatcher': node['dispatcher'],
                                   'lastping': time(),
                                   'pingcount': 0,
                                   'interval': 15  # TODO: Automate the interval with smart info (like movement speed)
                                   }

                if ip in self.probednodes:
                    self.loginfo("Probe returned storing socket for '%s'" % (ip))

                    self.nodes[sendernode] = self.probes[ip]
                    self.nodes[sendernode]['socket'] = self.probednodes[ip]

                    reply = msg.response({'ip': self.Configuration['routeraddress']})

                    self.nodes[sendernode]['socket'].send(jsonpickle.encode(reply))

                    route = Message(sender=self.name,
                                    recipient=self.systemdispatcher,
                                    func="addgateway",
                                    arg={'remotenode': sendernode,
                                         'connector': self.name},
                                    )

                    self.send(route, "outbox")

                    del(self.probednodes[ip])
                    del(self.probes[ip])
                else:
                    self.loginfo("Uninitiated probe by '%s' - discovering in reverse." % ip)
                    self._discoverNode(ip)

            else:
                # Hm, a response! This is the last packet in our discovery chain.
                self.loginfo("'%s' has successfully connected to us." % ip)
                # if ip in self.probes:
                probe = self.probes[ip]
                self.nodes[probe['uuid']] = probe
                self.nodes[probe['uuid']]['socket'] = self.probednodes[ip]
                self.nodes[probe['uuid']]['lastping'] = time()
                self.nodes[probe['uuid']]['pingcount'] = 0
                self.nodes[probe['uuid']]['interval'] = 15

                route = Message(sender=self.name,
                                recipient=self.systemdispatcher,
                                func="addgateway",
                                arg={'remotenode': probe['uuid'],
                                     'connector': self.name},
                                )

                self.send(route, "outbox")

                del(self.probednodes[ip])
                del(self.probes[ip])

            self.loginfo("Connected nodes after discovery action: '%s'" % self.nodes.keys())


    def _disconnectNode(self, node, announce=True):
        if node not in self.nodes:
            return (False, "Node not connected.")

        socket = self.nodes[node]['socket']
        if announce:
            msg = Message(sendernode=str(Identity.SystemUUID),
                          sender=self.name,
                          recipient='DTNGate',
                          func='disconnect')
            socket.send(jsonpickle.encode(msg))

        socket.close()
        del(self.nodes[node])

        return True

    def _discoverNode(self, ip):
        self.loginfo("Discovering node '%s'" % ip)
        socket = self.context.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, str(Identity.SystemUUID))
        socket.connect('tcp://%s:55555' % ip)
        # TODO: Is this smart, sending discovery data upon first message?
        # Maybe better in the reply...
        msg = Message(sendernode=str(Identity.SystemUUID),
                      sender=self.name,
                      recipient='DTNGate',
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

    def _pingNodes(self):
        disconnectednodes = []
        for node in self.nodes:
            if self.nodes[node]['lastping'] + self.nodes[node]['interval'] <= time():
                if self.nodes[node]['pingcount'] >= 3:
                    self.loginfo("Node '%s' hasn't reacted for three pings, disconnecting." % node)
                    disconnectednodes.append(node)
                else:
                    self.loginfo("Pinging '%s'." % node)
                    self.nodes[node]['pingcount'] += 1
                    self.nodes[node]['lastping'] = time()
                    ping = Message(sender=self.name,
                                   sendernode=Identity.SystemUUID,
                                   recipientnode=node,
                                   recipient='DTNGate',
                                   func='ping',
                                   arg={})
                    self.nodes[node]['socket'].send(jsonpickle.encode(ping))
            else:
                pass
                #self.logdebug("Not pinging '%s' - interval not yet reached." % node)

        for node in disconnectednodes:
            self._disconnectNode(node, announce=False)


    def rpc_listconnectedNodes(self):
        return str(self.nodes.keys())

    def rpc_transmit(self, msg):
        if msg.recipientnode == str(Identity.SystemUUID):
            errmsg = "(Unsent) message to ourself received for distribution: '%s'" % msg
            self.logerror(errmsg)
            return (False, errmsg)

        if not msg.recipientnode in self.nodes:
            errmsg = "Node '%s' unknown." % msg.recipientnode
            self.logwarning(errmsg)
            return (False, errmsg)

        msg.sendernode = str(Identity.SystemUUID)

        self.logdebug("Getting socket.")

        socket = self.nodes[msg.recipientnode]['socket']

        if not socket:
            # Connection not already established, so connect and store for later
            return (False, "Node not connected. Why?")

        self.loginfo("Transmitting message to '%s'." % msg.recipientnode)

        socket.send(jsonpickle.encode(msg))
        return True

    def rpc_discoverNode(self, ip):
        """Discovers a Node at a given IP."""

        #if ip not in self.probednodes:
        msg = "Probing new node: '%s'" % ip
        self.logdebug(msg)
        self._discoverNode(ip)
        return True, msg
        #else:
        #    self.logerror("Node has already been discovered: '%s'" % ip)
        #    return False

    def rpc_disconnectNode(self, node):
        """Disconnects a given Node including announcement of its disconnection."""

        return self._disconnectNode(node)

    def rpc_disconnectNodes(self):
        """Disconnects from all nodes after sending an announcement to each."""

        result = True

        for node in self.nodes:
            result = result and self._disconnectNode(node)

        return result




Registry.ComponentTemplates['DTNGate'] = [DTNGate, "Node-to-node ØMQ Connector"]
