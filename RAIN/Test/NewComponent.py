#!/usr/bin/python3
# -*- coding: utf-8 -*-

# WARNING!
# This is a demo of "how it would look" in python 3.x
# As you can see, the RPC definitions and its Methodregister
# can be built very dynamically with this annotated
# structure.
#
# Since we have very many dependencies,
# that cannot be resolved with 3.x Python,
# we choose to implement a rather ugly way
# to implement Methodregister annotations.

#    Prototype of the MS0x00 RAIN Operating Software - Useless NewComponent Component
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

import Axon

import inspect

from pprint import pprint

from ..Messages import Message

class NewComponent(Axon.Component.component):
    """Simple newstyle demo component
    Has no real function but:
    * Automated Method register via
     * Method annotations
     * Docstrings
     * Only registers methods beginning with "rpc_"
    * realized by _buildMethodRegister
    """
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol"}
    Methods = {'default': [{}, 'Increments an internal integer'],
               'reset':   [{}, 'Resets the internal integer to zero.'],
               'set':     [{'val': [int, 'New value']}, 'Sets the internal integer'],
               'init':    [{'verbosity': [int, 'Verbosity of component',3], 'i': [int, 'Internal reset value', 0]},'Init']
               }
    MethodRegister = {}

    verbosity = 1
    value = 0
    i = 0

    def rpc_default(self):
        """Increments the internal integer"""
        self.value += 1

    def rpc_set(self, val: [int, 'New integer value']):
        """Sets the internal integer to a given value."""
        self.value = val

    def rpc_complex(self, summandA: [int, 'Primary summand'], summandB: [int, 'Secondary summand']):
        """Adds to given integer summands together to the stored value."""
        self.value += summandA + summandB

    def rpc_reset(self):
        """Resets the internal integer to the specified reset value."""
        self._reset()

    def _reset(self):
        self.value = self.i

    def _getComponentInfo(self):
        return [self.name, self.__doc__, self.MethodRegister]

    def _buildMethodRegister(self):
        self.MethodRegister = {}
        for method in inspect.getmembers(self):
            if method[0].startswith("rpc_") or method[0] == "__init__":
                if method[0] == "__init__":
                    name = "initialization"
                else:
                    name = method[0][4:]
                params = inspect.getfullargspec(method[1]).annotations
                doc = inspect.getdoc(method[1])
                self.MethodRegister[name] = [params, doc]

    def __init__(self, verbosity:[int, 'Sets the initial verbosity.']=3, i:[int, 'Sets the initial reset value']=0):
        """Initializes the NewComponent Component that just demonstrates component side registry facilities"""
        super(NewComponent, self).__init__(self)
        self._buildMethodRegister()
        print("Output of this component's info:")
        pprint(self._getComponentInfo())
        self.verbosity = verbosity
        self.i = i
        self._reset

    def main(self):
        while True:
            while not self.anyReady():
                # Thumb twiddling.
                yield 1
            msg = None
            response = None
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if msg.recipient == self.name:
                    if msg.func == "ComponentInfo":
                        response = msg.response(self._getComponentInfo())
            if response:
                self.send(response, "outbox")
            yield 1

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

