#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - Crypto Components
#    2013-03-14 14:54:45
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

from RAIN.System import Registry
from RAIN.System.BaseComponent import BaseComponent

import zlib, gpgme

class Packer(BaseComponent):
    # Probably not needed, gnupg compresses data itself
    def __init__(self):
        super(Packer, self).__init__()

    def handleData(self, data):
        return zlib.compress(data) 

    def main(self):
        self.loginfo("Entering main loop.")
        while True:
            while not self.anyReady():
                yield 1

            response = None

            if self.dataReady("inbox"):
                self.logdebug("Handling incoming data.")
                msg = self.recv("inbox")
                response = self.handleData(msg)
            if response:
                self.logdebug("Sending response to outbox.")
                self.send(response, "outbox")
            yield 1

class Unpacker(BaseComponent):
    # See Packer
    def __init__(self):
        super(Unpacker, self).__init__()

    def handleData(self, data):
        return zlib.decompress(data) 

    def main(self):
        self.loginfo("Entering main loop.")
        while True:
            while not self.anyReady():
                yield 1

            response = None

            if self.dataReady("inbox"):
                self.logdebug("Handling incoming data.")
                msg = self.recv("inbox")
                response = self.handleData(msg)
            if response:
                self.logdebug("Sending response to outbox.")
                self.send(response, "outbox")
            yield 1
        

class Encryptor(BaseComponent):
    def __init__(self):
        super(Encryptor, self).__init__()
        #self.key = ""
        #self.method =

    def _handleData(self, data):
        pass # data-dead-end (not encrypting, so not delivering)

    def main(self):
        self.loginfo("Entering main loop.")
        while True:
            while not self.anyReady():
                yield 1

            response = None

            if self.dataReady("inbox"):
                self.logdebug("Handling incoming data.")
                msg = self.recv("inbox")
                response = self._handleData(msg)
            if response:
                self.logdebug("Sending response to outbox.")
                self.send(response, "outbox")
            yield 1

class Decryptor(BaseComponent):
    def __init__(self):
        super(Decryptor, self).__init__()

    def _handleData(self, data):
        pass # data-dead-end (not decrypting, so not delivering)


    def main(self):
        self.loginfo("Entering main loop.")
        while True:
            while not self.anyReady():
                yield 1

            response = None

            if self.dataReady("inbox"):
                self.logdebug("Handling incoming data.")
                msg = self.recv("inbox")
                response = self._handleData(msg)
            if response:
                self.logdebug("Sending response to outbox.")
                self.send(response, "outbox")
            yield 1


Registry.ComponentTemplates["Packer"] = [Packer, "Packer Description"]
Registry.ComponentTemplates["Unpacker"] = [Unpacker, "Unpacker Description"]
Registry.ComponentTemplates["Encryptor"] = [Encryptor, "GnuPG Encryption component"]
Registry.ComponentTemplates["Decryptor"] = [Decryptor, "GnuPG Decryption component"]