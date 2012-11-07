#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - Basic messages and primitives -
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

import jsonpickle
from time import time

from .Primitives import Angle, Waypoint, WaypointList

from copy import deepcopy

class Message(object):
    """
    Basic Message Class

    Stores
        * Sender
        * Recipient
        * Timestamp
        * Function Name
        * Function Arguments

    The timestamp is currently set upon init to the current time but can be changed later.
    """

    # TODO:
    # * Clean up
    # * Better JSON pickling, maybe
    # * Validation?
    # * Include reference timestamp?
    # * optimize
    #  * so any rpc can work with these
    #  * more serialization to other protocols like yaml or even XML (yuk!)
    # We might need '__weakref__' here..

    __slots__ = ['sender', 'recipient', 'timestamp', 'msg_type', 'func', 'arg', 'error']

    def __init__(self, sender="", recipient="", func="", arg="", error="", msg_type="request"):
        self.timestamp = time()
        self.sender = sender
        self.recipient = recipient
        self.msg_type = msg_type
        self.func = func
        self.arg = arg
        self.error = error

    def __str__(self):
        # TODO:
        # * check who calls this. Message apparently gets converted to string WAY too offen.
        try:
            argstring = str(self.arg)
            errstring = str(self.error)
        except AttributeError:
            return "Corrupted Message. Not all relevant parts were contained."

        if len(argstring) > 1024:
            argstring = "Too large to display (%i bytes)" % len(argstring)

        result = "%f - [%10s] -> [%10s] %s %15s (%s)" % (self.timestamp, self.sender, self.recipient,
                                                         self.msg_type, self.func,
                                                         argstring if not self.error else str(self.error))
        return result

    def response(self, args):
        response = deepcopy(self)
        response.sender, response.recipient = response.recipient, response.sender
        response.msg_type = "response"
        if isinstance(args, tuple):
            success, result = args
        elif isinstance(args, bool):
            success = args
            result = ""
        else:
            success = True
            result = args
        if success:
            response.arg = result
        else:
            response.error = result
        return response

    def jsondecode(self, jsonstring):
    # TODO: Clean up this mess
    #        print "Trying to parse json"
    #        try:
        from pprint import pprint

        pprint(jsonstring)
        test = jsonpickle.decode(jsonstring)
        if type(test) == type(self):
            self = test
            return True
        else:
            if test['timestamp']:
                self.timestamp = test['timestamp']
            else:
                print("No timestamp. Correcting.")
                self.timestamp = time()
            if test['sender']:
                self.sender = test['sender']
            else:
                print("No sender")
            if test['recipient']:
                self.recipient = test['recipient']
            else:
                print("No recipient")
            if test['func']:
                self.func = test['func']
            else:
                print("No func")
            if test['arg']:
                self.arg = test['arg']
            else:
                print("No args")

            return (self.sender and self.recipient and self.func and self.arg)
            #        except:
            #            return False

    def jsonencode(self, unpicklable=True):
        return jsonpickle.encode(self, unpicklable=unpicklable)


def test():
    # TODO: This class IS rather easy to test. Add some doctests here, now!
    print "No testing yet :/"

if __name__ == "__main__":
    test()
