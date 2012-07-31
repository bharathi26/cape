#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
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

from ANRV.System.Registry import ComponentTemplates
from ANRV.System.RPCComponent import RPCComponent

from ANRV.Messages import Message

import serial, string

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
        self.MR['rpc_nmeainput'] = {'default': [str, "NMEA raw data"]}
        self.MR['rpc_getNMEALog'] = {'oldest': [float, "Begin of data collection."],
                                     'newest': [float, "End of data collection. (0 = now)"]}
        super(NMEABaseSensor, self).__init__()
        self.Configuration.update({'SerialPort': 'ANRV.Communication.SerialPort.SerialPort_14',
                                  })

        self.nmeaLog = {}
        self.nmeaAcceptedSentences = ()

    def main_prepare(self):
        self.loginfo("Subscribing to configured SerialPort")
        request = Message(sender=self.name, recipient=self.Configuration['SerialPort'], func="subscribe", arg={'function': 'nmeainput', 'name': self.name})
        self.send(request, "outbox")

    def rpc_nmeainput(self, nmeasentence):
        """
        Called when a publisher sends a new nmea sentence to this sensor.

        The nmea data is parsed and further handling can happen.
        """
        if not "$G" in nmeasentence:
            err = "Non NMEA0183 data received!"
            self.logwarn(err)
            return False, err

        sen_time = time() # TODO: This is late due to message traversal etc.
        # We'd like to get our hands on the message's time, somehow
        sen_type = nmeasentence.split(',')[0].lstrip('$')
        if len(self.nmeaAcceptedSentences) == 0 or sen_type in self.nmeaAcceptedSentences:
            sen_mod = __import__('ANRV.Sensors.nmea', fromlist=[sen_type])
            nmeaobject = getattr(sen_mod, sen_type, None)
            self.nmeaLog[sen_time] = {'raw': nmeasentence,
                                      'type': sen_type,
                                      'obj': nmeaobject}

    def rpc_getNMEALog(self, oldest, newest=0):
        if newest == 0:
            newest = time()
        if oldest < 0:
            oldest = newest + oldest
        reqdict = {}
        reqkeys = self.nmeaLog.keys()

        self.loginfo("Looking for nmea data in time '%f'-'%f'." % (oldest, newest))

        for key in reqkeys:
            if key > oldest and key < newest:
                reqdict[key] = self.nmeaLog[key]
        return (True, reqdict)

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
