#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#     - Test.DTNTest
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
from cape.system.rpccomponent import RPCComponent

from cape.Communication.DTNGate import DTNGate

from cape.messages import Message

import jsonpickle

import zmq

class DTNTest(RPCComponent):
    def __init__(self):
        self.MR['rpc_test_dispatcher_node'] = {}
        self.MR['rpc_test_local_discovery'] = {}
        self.MR['rpc_test_remote_transmit'] = {}
        super(DTNTest, self).__init__()

    def rpc_test_local_discovery(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        socket.connect("tcp://%s:55555" % (DTNConnector.routeraddress))
        msg = Message(sendernode="FOOBAR", func="discovery", arg={'ip': 'bazqux'})
        package = jsonpickle.encode(msg)
        self.logdebug("Transmitting '%s' to local node discovery " % package)
        socket.send(package)
        return True

    def rpc_test_remote_transmit(self):
        msg = Message(sender=self.name, 
                      recipient="cape.system.RegistryComponent.RegistryComponent_7", 
                      recipientnode='3508dac4-1b23-4134-81f9-29cd10e02181',
                      func="listRegisteredComponents",
                      arg=None)
        self.send(msg, "outbox")

    def rpc_test_dispatcher_node(self):
        msg = Message(sender="", recipient="cape.", func="ping", arg="HELLO?", sendernode='FOOBAR')
        self.send(msg, "outbox")
        return True

    def main_prepare(self):
        """
        Method that is executed prior entering mainloop.
        Overwrite if necessary.
        """
        pass

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
        pass


Registry.ComponentTemplates['DTNTest'] = [DTNTest, "DTN test component"]
