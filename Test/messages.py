#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
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

from primitives import Angle, Waypoint, WaypointList

class Message():
    # We might need '__weakref__' here..
    __slots__ = ['sender', 'recipient', 'timestamp', 'func', 'arg']
    def __init__(self, sender="", recipient="", func="", arg=""):
        self.timestamp = time()
        self.sender = sender
        self.recipient = recipient
        self.func = func
        self.arg = arg

    def __str__(self):
        result = "%f - [%10s] -> [%10s] %15s (%s)" %(self.timestamp, self.sender, self.recipient, self.func, self.arg)
        return result

if __name__ == "__main__":
    course = Angle("heading", 223)
    foo = Message('rudder', 'messagetester', func="dataresponse", arg=course)

    print "First test simple string representation:"
    print foo

    print "\n#########################################################################\n"
    print "Now, on to the json en/decoding:"
    spam = jsonpickle.encode(foo)
    ham = jsonpickle.decode(spam)
    print spam
    print ham

    print "\n#########################################################################\n"
    print "Now we decode something we snapped up:"
    eggs = jsonpickle.encode(foo, unpicklable=False)
    print eggs
    qux = jsonpickle.decode(eggs)
    print qux['sender']

    print "\n#########################################################################\n"
    print "And again, with something old:"
    spam = '{"py/object": "__main__.Message", "sender": "rudder", "timestamp": 1330118209.340174, "func": "dataresponse", "arg": {"py/object": "__main__.Angle", "name": "heading", "value": 223}, "recipient": "__main__"}'
    ham = jsonpickle.decode(spam)
    print ham

    print "\n#########################################################################\n"
    print "Generating wild Berlin based Waypoints:"
    ham = WaypointList("TestWaypointlist")
    for count, foo in enumerate(range(10)):
        bar = Waypoint("Point %i" % count, "52,30.2N", "13,23.56E")
        print bar
        ham.append(bar)

    print ham

    print "\n#########################################################################\n"
    print "Testing Messages with a WaypointList"
    spam = Message(__name__, "WaypointController", "SetList", ham)
    print spam

    print "\n#########################################################################\n"
    print "Trying to jsonize WPC-Testmessage:"
    eggs = jsonpickle.encode(spam)
    print eggs

    spam = jsonpickle.decode(eggs)
    ham = spam.arg
    print ham.name
    print ham.points
    for point in ham.points:
        print point
