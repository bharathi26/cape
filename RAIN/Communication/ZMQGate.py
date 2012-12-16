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

__doc__ = """
Preliminary testing ZMQ gateway component.

The intention of this component is to integrate ZMQ as node-to-node communication protocol
into RAIN.
"""

from RAIN.System import Registry
from RAIN.System.RPCComponent import RPCComponent

import sys
print sys.path
import zmq

class ZMQGate(RPCComponent):
    def __init__(self):
        super(ZMQGate, self).__init__()
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind("ipc://*:55555")
    
Registry.ComponentTemplates['ZMQGate'] = [ZMQGate, "Node-to-node ØMQ Gateway"]