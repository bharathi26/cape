#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#    Simple Position & Course Tracker 
#    Copyright (C) 2012 Martin Ling <martin@earth.li>
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
from ANRV.Messages import Message
from time import time

class Tracker(RPCComponent):

    def __init__(self):
        self.MR['rpc_gpsinput'] = {'args': [tuple, "Tuple of (sentence type, NMEA object)"]}
        super(Tracker, self).__init__()

    def main_prepare(self):
        self.latitude = float('nan')
        self.longitude = float('nan')
        self.track = float('nan')
        self.speed = float('nan')
        self.loginfo("Subscribing to NMEA data")
        request = Message(sender=self.name, recipient=self.Configuration['gps'],
            func="subscribe", arg={'function': 'gpsinput', 'name': self.name})
        self.send(request, "outbox")

    def rpc_gpsinput(self, args):
        sen_type, sen = args
        if sen_type == 'GPGGA':
            self.latitude = self._decode(sen.latitude, sen.lat_direction)
            self.longitude = self._decode(sen.longitude, sen.lon_direction)
        elif sen_type == 'GPGLL':
            self.latitude = self._decode(sen.lat, sen.lat_direction)
            self.longitude = self._decode(sen.lon, sen.lon_direction)
        elif sen_type == 'GPRMC':
            self.latitude = self._decode(sen.lat, sen.lat_dir)
            self.longitude = self._decode(sen.lon, sen.lon_dir)
            self.track = float(sen.true_course)
            self.speed = float(sen.spd_over_grnd)
        elif sen_type == 'GPVTG':
            self.track = float(sen.true_track)
            self.speed = float(sen.spd_over_grnd_kts)
        else:
            return

        for subscriber, function in self.subscribers.items():
            self.loginfo("Sending tracker data to subscriber %s" % subscriber)
            message = Message(sender=self.name, recipient=subscriber,
                func=function, arg={'latitude': self.latitude, 'longitude': self.longitude,
                    'track': self.track, 'speed': self.speed})
            self.send(message, "outbox")

    def _decode(self, value, direction):
        deg_length = 3 if direction[0] in 'EW' else 2
        degrees = int(value[:deg_length])
        minutes = float(value[deg_length:])
        return (degrees + minutes / 60) * (1 if direction[0] in 'NE' else -1)

Registry.ComponentTemplates['Tracker'] = [Tracker, "Position & Course Tracker"]
