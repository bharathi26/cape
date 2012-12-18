#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - Basic messages and primitives -
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

import jsonpickle
from time import time

from copy import deepcopy

from RAIN.System import Identity

class Message(object):
    """
    Basic Message Class

    Stores
        * Sender
        * Recipient
        * Timestamp
        * Function Name
        * Function Arguments

    The timestamp is currently set upon init to the current time but can be changed later.
    """

    # TODO:
    # * Clean up
    # * Better JSON pickling, maybe
    # * Validation?
    # * Include reference timestamp?
    # * optimize
    #  * so any rpc can work with these
    #  * more serialization to other protocols like yaml or even XML (yuk!)
    # We might need '__weakref__' here..

    __slots__ = ['sendernode', 'sender', 'recipientnode', 'recipient', 'timestamp', 'msg_type', 'func', 'arg', 'error']

    def __init__(self, sendernode="", sender="", recipientnode="", recipient="", func="", arg="", error="", msg_type="request"):
        """Initializes a new message with the current timestamp and given arguments.
        Default message type is "request"
        
        Address pattern for sender and recipient:
        [str(node):]str(component.name)
        """
        self.timestamp = time()
        
        self.sender = sender
        self.recipient = recipient
        
        self.sendernode = sendernode
        self.recipientnode = recipientnode
        
        self.msg_type = msg_type
        self.func = func
        self.arg = arg
        self.error = error

    def localRecipient():
        def fget(self):
            return self.recipientnode == Identity.SystemUUID
        
        return locals()
    
    localRecipient = property(**localRecipient())
        
    def localSender():
        def fget(self):
            return self.sendernode == Identity.SystemUUID
        
        return locals()
        
    localSender = property(**localSender())    

#    def recipientNode():
#        """Returns and sets the recipient node."""
#       
#        def fget(self):
#            if ":" in self.recipient:
#                # Message recipient has a node, return only that part
#                return self.recipient.split(":")[0]
#            else:
#                # No node, systemwide only message
#                return Identity.SystemUUID
#        
#        def fset(self, value):
#            if value in ("", Identity.SystemUUID):
#                # No node means local message - delete node
#                del(self.recipientNode)
#            else:
#                if ":" in self.recipient:
#                    self.recipient = "%s:%s" % (value, self.recipient.split(":")[1])
#                else:
#                    self.recipient = "%s:%s" % (value, self.recipient)  
#                
#        def fdel(self):
#            if ":" in self.recipient:
#                # Message recipient has a node, delete that
#                self.recipient = self.recipient.split(":")[1]            
#              
#        return locals()
#       
#    recipientNode = property(**recipientNode())
#
#    def senderNode():
#        """Returns and sets the sender node."""
#        # TODO: This is a bulky copy of the recipientNode property
#       
#        def fget(self):
#            if ":" in self.sender:
#                # Message sender has a node, return only that part
#                return self.sender.split(":")[0]
#            else:
#                # No node, systemwide only message
#                return Identity.SystemUUID
#        
#        def fset(self, value):
#            if value in ("", Identity.SystemUUID):
#                # No node means local message
#                self.sender = self.sender.split(":")[1]
#                # TODO: essentially this is the same as .fdel()
#            else:
#                self.sender = "%s:%s" % (value, self.sender.split(":")[1])
#                
#        def fdel(self):
#            if ":" in self.sender:
#                # Message sender has a node, delete that
#                self.sender = self.sender.split(":")[1]            
#              
#        return locals()
#       
#    senderNode = property(**senderNode())


    def __str__(self):
        # TODO:
        # * check who calls this. Message apparently gets converted to string WAY too offen.
        try:
            argstring = str(self.arg)
            errstring = str(self.error)
        except AttributeError:
            return "Corrupted Message. Not all relevant parts were contained."

        if len(argstring) > 1024:
            argstring = "Too large to display (%i bytes)" % len(argstring)

        result = "%f - [%10s] -> [%10s] %s %15s (%s)" % (self.timestamp, self.sender, self.recipient,
                                                         self.msg_type, self.func,
                                                         argstring if not self.error else str(self.error))
        return result

    def response(self, args):
        response = deepcopy(self)
        response.sender, response.recipient = response.recipient, response.sender
        response.msg_type = "response"
        if isinstance(args, tuple):
            success, result = args
        elif isinstance(args, bool):
            success = args
            result = ""
        else:
            success = True
            result = args
        if success:
            response.arg = result
        else:
            response.error = result
        return response

    def jsondecode(self, jsonstring):
    # TODO: Clean up this mess
    #        print "Trying to parse json"
    #        try:
        from pprint import pprint

        pprint(jsonstring)
        test = jsonpickle.decode(jsonstring)
        if type(test) == type(self):
            self = test
            return True
        else:
            if test['timestamp']:
                self.timestamp = test['timestamp']
            else:
                print("No timestamp. Correcting.")
                self.timestamp = time()
            if test['sender']:
                self.sender = test['sender']
            else:
                print("No sender")
            if test['recipient']:
                self.recipient = test['recipient']
            else:
                print("No recipient")
            if test['func']:
                self.func = test['func']
            else:
                print("No func")
            if test['arg']:
                self.arg = test['arg']
            else:
                print("No args")

            return (self.sender and self.recipient and self.func and self.arg)
            #        except:
            #            return False

    def jsonencode(self, unpicklable=True):
        return jsonpickle.encode(self, unpicklable=unpicklable)


def test():
    # TODO: This class IS rather easy to test. Add some doctests here, now!
    print "No testing yet :/"

if __name__ == "__main__":
    test()
