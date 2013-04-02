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
from RAIN.Messages import Message
from RAIN.System.BaseComponent import BaseComponent
from RAIN.System.RPCComponent import RPCComponent

from RAIN.System.Identity import SystemUUID

from io import BytesIO

import zlib, gpgme, jsonpickle

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

class KeyManager(RPCComponent):
    def __init__(self):
        self.MR = {'rpc_generateKey':{},
                   'rpc_exportKey': {},
                   'rpc_importKey': {},
                   'rpc_checkKeys': {}
                   }
        super(KeyManager, self).__init__()
        self.keyconfig = {'type': 'RSA',
                          'length': 2048}
        
        self.context = gpgme.Context()
        self.context.armor = False
        
    def rpc_exportKey(self):
        if self._hasKey():
            return self.context.get_key(self.Configuration['KeyID'])
        else:
            return (False, "Don't have a key.")
    
    def rpc_generateKey(self):
        if not self._hasKey():
            self._genKey()
            return True
        else:
            return (False, "Already have a key.")
        
    def _hasKey(self):
        try:
            self.context.get_key(self.Configuration['KeyID'])
        except KeyError:
            self.loginfo("Key not configured.")
        except gpgme.GpgmeError:
            self.loginfo("Key not generated.")
        else:
            return True
        return False
        
    def _genKey(self):
        self.loginfo("Generating new Key.")
        passphrase = "secret"
        expiry = 0
        key_params = """
<GnupgKeyParms format="internal">
Key-Type: %s
Key-Length: %i
Name-Real: %s
Name-Email: %s@openseadata.org
Expire-Date: %i
Passphrase: %s
</GnupgKeyParms>
""" % (self.keyconfig['type'], self.keyconfig['length'], SystemUUID, SystemUUID, expiry, passphrase)
        result = self.context.genkey(key_params)
        #key = self.context.get_key(result.fpr, True)
        self.Configuration['KeyID'] = result.fpr
        self.loginfo("Key successfully generated, fingerprint: '%s'" % result.fpr)

class Encryptor(BaseComponent):
    def __init__(self):
        super(Encryptor, self).__init__()
        self.context = gpgme.Context()

    def _handleData(self, data):
        if isinstance(data, Message):
            node = data.recipientnode
            key = self.context.get_key(node)
            plaintext = BytesIO(jsonpickle.encode(data))
            ciphertext = BytesIO()
            self.loginfo("Encrypting message: '%s'" % str(data))
            self.context.encrypt([key], gpgme.ENCRYPT_ALWAYS_TRUST, plaintext, ciphertext)
            return ciphertext
        else:
            self.logcritical("Got a non-message to encrypt! '%s'" % data)

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
Registry.ComponentTemplates["KeyManager"] = [KeyManager, "GnuPG Key management component"]