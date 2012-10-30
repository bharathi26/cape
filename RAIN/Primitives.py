#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - Basic and advanced primitives -
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

# TODO: Use some smart OOP to capsule common stuff
# TODO: Implement more primitives
# * Geocoordinates
# * Atmospheric parameters
#  * Temperatures
#  * Pressure
#  * Humidity
#  * (Gas) concentration (ppm?)
# * Flow vectors?
# * (Fluid)-depth
# * Speeds?
# * Primitives for 9dof usage
# * Primitives for GPS usage

class Waypoint(object):
    """A Waypoint consists of a geographical location (latitude and longitude) and a name."""
    __slots__ = ['name', 'lat', 'lon']

    def __init__(self, name="", lat="", lon=""):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __str__(self):
        result = "%s[%s, %s]" % (self.name, self.lat, self.lon)
        return result


class WaypointList(object):
    """A waypointlist consists of several Waypoints and a name."""
    __slots__ = ['name', 'points']

    def __init__(self, name="", points=None):
        if not points: points = []
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


class Angle(object):
    """Contains a named angle in degrees."""
    __slots__ = ['name', 'value']

    def __init__(self, name="", val=""):
        self.name = name
        self.value = val

    def __str__(self):
        result = "%s: %f° DEG" % (self.name, self.value)
        return result


class Frequency(object):
    """Contains a frequency and methods to ease usage.
    See http://en.wikipedia.org/wiki/Frequency
    """
    # TODO: I'd like this one to be transparent about setting/getting either Periods or Frequencies
    # Internally this object always stores frequencies, hence the name.
    __slots__ = ['name', 'value']

    def __init__(self, name="", val=0, period=0):
        self.name = name
        self.value = val
        if period != 0:
            self.value = 1.0 / period

    def __str__(self):
        """Type: string
        Returns a descriptive string containing name, frequency and the label Hz."""
        result = "%s: %f Hz" % (self.name, self.value)
        return result

    def Period(self):
        """Type: float
        Returns the period of this frequency (1/f)."""
        if self.value == 0:
            return 0
        else:
            return 1.0 / self.value
