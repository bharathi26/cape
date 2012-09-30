#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
#     - Maestro Serial Controller -
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

import serial

class Maestro(RPCComponent):
    verbosity = 1
    protocol = "SSC"
    device = "/dev/ttyACM0"
    autodetect = True
    maestro = None

    def _connect(self):
        try:
            self.maestro = serial.Serial(self.device)
            if self.autodetect:
                self.maestro.write(chr(0xAA))
                self.maestro.flush()
        except Exception as error:
            self.logerror("Failed to open device: %s" % error)
            self.maestro = None

    def rpc_write(self, args):
        self.logdebug("Writing to Maestro '%s'" % args)
        try:
            for byte in args:
                self.maestro.write(chr(byte))
            return True
        except Exception as error:
            self.logerror("Failed to write '%s'" % error)
            return (False, str(error))

    def __init__(self):
        self.MR['rpc_write'] = {'args': [str, "Message to send"]}
        super(Maestro, self).__init__()
        self.Configuration.update({
            'device': "/dev/ttyACM0",
            'autodetect': True,
            'protocol': "SSC",
            'verbosity': 0
        })
        self._connect()

ComponentTemplates["Maestro"] = [Maestro, "Violated copy of a SerialPort."]
