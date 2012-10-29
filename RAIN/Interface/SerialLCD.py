#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - Serial LCD Component -
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

# TODO:
# * Message buffer 
#  * Walking through messages (Ring, Pendulum etc)
#  * Message timeout
# * Write function
# * Who handles writing of sensor data?


import Axon

from Kamaelia.Util.Backplane import Backplane, PublishTo, SubscribeTo
from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from ..Messages import Message
from ..Primitives import Frequency

from time import time
from math import fsum

import serial

class SerialLCD(Axon.ThreadedComponent.threadedcomponent):
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this LCD"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this LCD"}
    verbosity = 1
    device = "/dev/ttyACM1"
    lcd = None
    rows = 2
    cols = 16

    def __init__(self, device="/dev/ttyACM1", verbosity=1):
        super(SerialLCD, self).__init__()
        self.device = device
        self.verbosity = verbosity
        self._connect()

    def _brightness(self, value):
        self.lcd.write("\x7C" + chr(int(29 * value) + 128))
        self.pause(0.01)
        return True

    def _clear(self):
        self.lcd.write("\xFE\x01")
        self.pause(0.01)
        self._pos(0,0)
        return True

    def _clearrow(self, row):
        self._pos(0,row)
        for i in range(self.cols):
            self.lcd.write(" ")
            self.pause(0.01)
        self._pos(0,row)

    def _setsize(self, cols=16, rows=2):
        self.cols = cols
        self.rows = rows
        if cols == 16:
            self.lcd.write("\x7C\x34")
        elif cols == 20:
            self.lcd.write("\x7C\x33")
        if rows == 2:
            self.lcd.write("\x7C\x36")
        elif rows == 4:
            self.lcd.write("\x7C\x35")

    def _pos(self, col, row):
        if row == 0:
            count = col
        elif row == 1:
            count = 64 + col
        elif row == 2:
            count = 16 + col
        elif row == 3:
            if self.cols == 20:
                count = 84 + col
            else:
                count = 80 + col
        self.lcd.write("\xFE" + chr(128 + count))
        self.pause(0.01)

    def _text(self, text):
        self._clear()
        for letter in text:
            self.lcd.write(letter)
            self.pause(0.01)
        return True

    def _connect(self):
        try:
            self.lcd = serial.Serial(self.device,)
            self._brightness(0.5)
            self._text("RAIN Booting up - Please wait -")
        except Exception as error:
            print("DEBUG.LCD._connect: Failed to open device: %s" % error)
            self.lcd = None


    def write(self, args):
        # TODO: Call the maestro to actually sendout a message to the serial LCD
        # See here: http://www.sparkfun.com/datasheets/LCD/SerLCD_V2_5.PDF
        try:
            udata=args.decode("utf-8")
        except:
            udata=args
        asciidata=udata.encode("ascii","replace")

        cursor = 0
        firstpass = True # test whether this is the first 16 characters
        lcd = self.lcd

        self._pos(0,0)

        for letter in asciidata:
            lcd.write(letter)
            cursor += 1

            if cursor == 16:
                self._clearrow(1)
            elif cursor == 32:
                self._clearrow(0)
                cursor = 0
            self.pause(0.075) # adjust this to a comfortable value
        if cursor < 16:
            self._clearrow(1)
        return True


    def main(self):
        while True:
            while not self.anyReady():
                # Thumb twiddling.
                self.pause(0.01)

            response = None
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                if msg.recipient == "LCD":
                    if msg.func == "Text":
                        response = msg.response(self._text(msg.arg))
                    elif msg.func == "Write":
                        response = msg.response(self.write(msg.arg))
                    elif msg.func == "Clear":
                        response = msg.response(self._clear())
                    elif msg.func == "Brightness":
                        response = msg.response(self._brightness(msg.arg))
                    elif msg.func == "SetVerbosity":
                        self.verbosity = int(msg.arg)
                        response = msg.response(True)

            if response:
                self.send(response, "outbox")

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

