#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - NMEABaseSensor Serial Controller -
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

from RAIN.System.Registry import ComponentTemplates
from RAIN.System.RPCComponent import RPCComponent

from RAIN.Messages import Message

import serial, string
from pynmea.streamer import NMEAStream

from time import time

class NMEABaseSensor(RPCComponent):
    """
    Basic NMEA capable sensor component

    Inherited components have an understanding of nmea data and can handle
    an attached SerialPort component's ouutgoing NMEA traffic.
    """


    def __init__(self):
        self.MR['rpc_connect'] = {}
        self.MR['rpc_disconnect'] = {}
        self.MR['rpc_nmeainput'] = {'line': [str, "NMEA raw data"]}
        self.MR['rpc_getNMEADeltaLog'] = {'oldest': [float, "Begin of data collection."],
                                          'newest': [float, "End of data collection. (0 = now)", 0]}
        self.MR['rpc_getNMEATimeLog'] = {'eventtime': [float, "Begin of data collection."],
                                         'maxdeviation': [float, "Maximum time deviation in seconds.", 10]}

        super(NMEABaseSensor, self).__init__()
        self.Configuration.update({'SerialPort': 'RAIN.Communication.SerialPort.SerialPort_15'})

        self.nmeaLog = {}
        self.streamer = NMEAStream()

    def main_prepare(self):
        self.loginfo("Subscribing to configured SerialPort")
        request = Message(sender=self.name, recipient=self.Configuration['SerialPort'], func="subscribe", arg={'function': 'nmeainput', 'name': self.name})
        self.send(request, "outbox")

    def rpc_nmeainput(self, line):
        """
        Called when a publisher sends a new nmea sentence to this sensor.

        The nmea data is parsed and further handling can happen.
        """
        sen_time = time() # TODO: This is late due to message traversal etc.
        for sentence in self.streamer.get_objects(line):
            self.nmeaLog[sen_time] = {'raw': line,
                                      'type': sentence.sen_type,
                                      'obj': sentence}
            for recipient, func in self.subscribers.items():
                msg = Message(sender=self.name, recipient=recipient, func=func,
                        arg={'args': (sentence.sen_type, sentence)})
                self.send(msg, "outbox")

    def rpc_getNMEATimeLog(self, eventtime, maxdeviation=10):
        if eventtime < 0:
            eventtime = time() - eventtime
        minimum, maximum = eventtime - maxdeviation, eventtime + maxdeviation
        #print((minimum, maximum))
        reqdict = {}
        for key in self.nmeaLog.keys():
            #print(key)
            if minimum < key < maximum:
                reqdict[key] = self.nmeaLog[key]
        return True, reqdict

    def rpc_getNMEADeltaLog(self, oldest, newest=0):
        if newest == 0:
            newest = time()
        if oldest < 0:
            oldest += newest
        reqdict = {}
        reqkeys = self.nmeaLog.keys()

        self.loginfo("Looking for nmea data in time '%f'-'%f'." % (oldest, newest))

        for key in reqkeys:
            if oldest < key < newest:
                reqdict[key] = self.nmeaLog[key]
        return True, reqdict

    def rpc_connect(self):
        """
        Tries to connect to the serial device.

        You have to set parameters before calling connect.
        """

        self.loginfo("RPC Connect called.")
        pass

    def rpc_disconnect(self):
        """
        Disconnects the serial device.
        """

        self.loginfo("RPC Disconnect called.")
        pass

ComponentTemplates['NMEABaseSensor'] = [NMEABaseSensor, "NMEA capable base sensor"]
