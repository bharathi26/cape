#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#    Magnetometer
#    Copyright (C) 2012 Martin Ling <martin-hf@earth.li>
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

from RAIN.System.Registry import ComponentTemplates
from RAIN.System.RPCComponent import RPCComponentThreaded
from RAIN.Messages import Message

try: # DEPENDENCYBUG
    from smbus import SMBus
except ImportError:
    print "smbus missing!"
    
from time import sleep

class Magnetometer(RPCComponentThreaded):
    """
    HMC5883L I2C magnetometer
    """

    def main_prepare(self):
        self.bus = SMBus(self.Configuration['bus'])
        self.address = self.Configuration['address']
        self.bus.write_byte_data(self.address, 2, 0)
        self.values = [0, 0, 0]

    def mainthread(self):
        for i, offset in enumerate(range(3, 8, 2)):
            msb = self.bus.read_byte_data(self.address, offset)
            lsb = self.bus.read_byte_data(self.address, offset + 1)
            value = (msb << 8) + lsb
            if value >= 32768:
                value -= 65536
            self.values[i] = value
        for subscriber, func in self.subscribers.items():
            self.send(Message(sender=self.name, recipient=subscriber, func=func,
                              arg={'x': self.values[0], 'y': self.values[2], 'z': self.values[1]}),
                      "outbox")
        sleep(0.1)

ComponentTemplates['Magnetometer'] = [Magnetometer, "Magnetometer"]
