#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      The counterpart to the useless ping component
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

from RAIN.System import Registry
from RAIN.System.RPCComponent import RPCComponent

from time import time

class Pong(RPCComponent):
    """
    Classic Pong component.
    
    Returns Ping requests, no more.
    """
    
    def __init__(self):
        self.MR['rpc_ping'] = {}
        super(Pong, self).__init__()
    
    def rpc_ping(self):
        self.logdebug("Got a ping.")
        return time()


Registry.ComponentTemplates['Pong'] = [Pong, "Pong component (see also: Ping)"]