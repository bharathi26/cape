#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - SerialPort Serial Controller -
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
from RAIN.System.RPCComponent import RPCComponentThreaded, RPCComponent

from RAIN.Messages import Message

import serial, string

class SerialPort(RPCComponentThreaded):
    Port = None

    def _connect(self):
        self.loginfo("Connecting SerialPort '%s'" % self.Configuration['device'])
        if self.Port and self.Port.isOpen():
            return (False, "Already connected.")
        try:
            self.Port = serial.Serial(self.Configuration['device'])
            self.Port.flush()
            return True
        except Exception as error:
            msg = "Failed to open device: %s" % error
            self.logerror(msg)
            self.Port = None
            return (False, msg)

    def _disconnect(self, flush=False):
        if isinstance(self.Port, serial.Serial):
            if self.Port.isOpen() and flush:
                # This may need exception catching
                self.Port.flush()
            self.Port.close()
            return True
        else:
            return (False, "Port not connected.")

    def mainthread(self):
        if self.Port and self.Port.isOpen() and self.listening:
            self.buf = self.buf + self.Port.read(self.Port.inWaiting())
            if self.Configuration['readline']:
                if '\n' in self.buf:
                    lines = self.buf.split('\n') # Guaranteed to have at least 2 entries
                    line = lines[-2]
                    self.buf = lines[-1]
                    self.logdebug(line)
                    for recipient in self.subscribers:
                        msg = Message(sender=self.name, recipient=recipient, func=self.subscribers[recipient], arg={'line': line})
                        self.send(msg, "outbox")
            else:
                for recipient in self.subscribers:
                    msg = Message(sender=self.name, recipient=recipient, func=self.subscribers[recipient], arg=self.buf)
                    self.send(msg, "outbox")
                self.buf = ""


    def __init__(self, device="/dev/ttyACM0", autodetect=True, verbosity=1):
        self.MR['rpc_connect'] = {}
        self.MR['rpc_disconnect'] = {}
        self.MR['rpc_write'] = {'args': [str, "String to send."]} # TODO: Strings are BAD HERE.
        super(SerialPort, self).__init__()
        self.Configuration.update({'verbosity': 1, # TODO: Make use of all these...
                          'device': "/dev/ttyACM0",
                          'speed': 9600,
                          'bytesize': 8,
                          'parity': 'N',
                          'stopbits': 1,
                          'timeout': None, # Hmmm.
                          'xonxoff': 0,
                          'buffersize': 100,
                          'readline': True
                         })

        self.logdebug(self.Configuration)
        self.device = device
        self.listening = True
        self.buf = ""

        if self.Configuration.has_key('autoconnect') and self.Configuration['autoconnect']:
            self._connect()

    def _write(self, args):
        self.loginfo("Writing to SerialPort: '%s'" % args)
        if not self.Port:
            return (False, "Not connected.")
        try:
            if len(args) > 0:
                for byte in args:
                    self.Port.write(byte)
                if self.Configuration["readline"] == True and args[-1] != "\n":
                    self.logdebug("Appending newline.")
                    self.Port.write("\n")
            elif self.Configuration["readline"]:
                self.Port.write("\n")
            return True
        except Exception as error:
            msg = "Failed to write: %s" % error
            self.logerror(msg)
            return (False, msg)
            # TODO: Maybe not a good idea to return the exception itself. Traceback might help

    def rpc_connect(self):
        """
        Tries to connect to the serial device.

        You have to set parameters before calling connect.
        """

        self.loginfo("RPC Connect called.")
        return self._connect()

    def rpc_disconnect(self):
        """
        Disconnects the serial device.
        """

        self.loginfo("RPC Disconnect called.")
        return self._disconnect()

    def rpc_subscribe(self, name, function):
        """
        Adds sender to the subscription list of our incoming data.
        """
        self.loginfo("New subscription: '%s'@'%s'" % (function, name))
        self.subscribers[name] = function
        return

    def rpc_write(self, args):
        self.loginfo("RPC Write called with '%s'." % args)
        return self._write(args)

ComponentTemplates['SerialPort'] = [SerialPort, "Serial Port Driver"]
