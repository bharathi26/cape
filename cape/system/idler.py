#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software - CLI Classes
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
from cape.system.rpccomponent import RPCComponent
from cape.primitives import Frequency

from time import sleep

class Idler(RPCComponent):
    def __init__(self, frequency=200, realtime=False):
        self.MR['rpc_setFreq'] = {'frequency': [float, 'Frequency to run with (Hz)']}
        self.MR['rpc_setRealtime'] = {'realtime': [bool, 'If on, run as fast as possible (Idler deactivated).']}

        super(Idler, self).__init__()
        self.Configuration.update({
            'frequency': frequency,
            'realtime': realtime})

    def rpc_setFreq(self, frequency):
        self.Configuration['frequency'] = frequency
        return True

    def rpc_setRealtime(self, realtime):
        self.Configuration['realtime'] = realtime
        return True

    def main(self):
        """Mainloop copied over from RPCComponent, since we need to wait here to achieve our idletime.
        """
        while True:
            while not self.anyReady():
                if not self.Configuration['realtime']:
                    sleep(1.0 / self.Configuration['frequency'])
                yield 1
            msg = None
            response = None

            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                response = self.handleRPC(msg)
            if response:
                self.send(response, "outbox")
            yield 1
