#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software - CLI Classes
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

from ANRV.System import Registry
from ANRV.System.RPCComponent import RPCComponent
from ANRV.Primitives import Frequency

from time import sleep

class Idler(RPCComponent):
    def __init__(self, frequency=Frequency("IdlerFreq", 200), realtime=False):
        args = {'frequency':[Frequency, 'Period to wait'],
                'realtime' :[bool, 'Initial realtime setting.']}
        super(Idler, self).__init__()
        self.frequency = frequency
        self.realtime = realtime

    def rpc_setFreq(self, arg):
        if isinstance(arg, Frequency):
            self.frequency = arg
            return True
        else: return (False, "Wrong Argument")

    def rpc_setRealtime(self, arg):
        args = {'arg': [bool, 'Set to true to run system in Realtime']}
        if isinstance(arg, bool):
            self.realtime = arg
            return True
        else: return (False, "Wrong Argument")

    def main(self):
        """Mainloop copied over from RPCComponent, since we need to wait here to achieve our idletime.
        """
        while True:
            while not self.anyReady():
                if not self.realtime:
                    sleep(self.frequency.Period())
                yield 1
            msg = None
            response = None

            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                response = self.handleRPC(msg)
            if response:
                self.send(response, "outbox")
            yield 1

Registry.ComponentTemplates['Idler'] = (Idler, 'System idle time component')
