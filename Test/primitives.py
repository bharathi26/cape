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



class Waypoint():
    __slots__ = ['name', 'lat', 'lon']
    def __init__(self, name="", lat="", lon=""):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __str__(self):
        result = "%s[%s, %s]" % (self.name, self.lat, self.lon)
        return result

class WaypointList():
    __slots__ = ['name', 'points']

    def __init__(self, name="", points=[]):
        self.name = name
        self.points = points

    def __str__(self):
        result = "%s[" % self.name
        for point in self.points:
            result += str(point) + ", "
        result += "]"
        return result

    def append(self, point):
        self.points.append(point)

class Angle():
    __slots__ = ['name', 'value']
    def __init__(self, name="", val=""):
        self.name = name
        self.value = val

    def __str__(self):
        result = "%s: %f° DEG" % (self.name, self.value)
        return result
