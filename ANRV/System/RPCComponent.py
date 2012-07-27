#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
#      - Basic RPC Component Class
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

import inspect

from pprint import pprint

from ANRV.System.Registry import ComponentTemplates
from ANRV.System.ConfigurableComponent import ConfigurableComponent

from ANRV.Messages import Message

class RPCComponent(ConfigurableComponent):
    """Basic RPC Component.

    Has no real function but:
    * Automated Method register via
     * Method annotations
     * Docstrings
     * Only registers methods beginning with "rpc_"
    * realized by _buildMethodRegister

    See these examples about the annotations necessary to complete this:
    
    def rpc_set(self, val: [int, 'New integer value to set']):
        "Sets the internal integer to a given value."
        self.value = val

    def rpc_complex(self, summandA: [int, 'Primary summand'], summandB: [int, 'Secondary summand']):
        "Adds to given integer summands together to the stored value."
        self.value += summandA + summandB

    def rpc_reset(self):
        "Resets the internal integer to the specified reset value."
        self._reset()

    TODO: 
    * Correct documentation
    * Automate RPC calling somehow, somewhere (smart)
    * RPC Variables? (With automatic getters and setters - by config?)
    * Security! (Here?)
    """
    Inboxes = {"inbox": "RPC commands",
               "control": "Signaling to this Protocol"}
    Outboxes = {"outbox": "RPC Responses",
                "signal": "Signaling from this Protocol"}
    MethodRegister = {}
    MR = {}

#    def rpc_default(self, arg):
#       """Default Method"""
#        # TODO: Do we need a default rpc method? Why? What could we do with it?
#        pass

    def rpc_updateComponentInfo(self):
        """RPC Function '''updateComponentInfo'''

        Updates this RPCComponent's methodregister.

        Returns True upon completion.
        """

        return self._buildMethodRegister()

    def rpc_getComponentInfo(self):
        """RPC Function '''getComponentInfo'''

        Returns this RPCComponent's methodregister.
        """

        return self._getComponentInfo()

    def rpc_getConfiguration(self):
        """RPC wrapper for ConfigurableComponent"""
        return self.GetConfiguration()

    def rpc_writeConfiguration(self):
        """RPC wrapper for ConfigurableComponent"""
        return self.WriteConfiguration()

    def rpc_readConfiguration(self):
        """RPC wrapper for ConfigurableComponent"""
        return self.ReadConfiguration()

    def rpc_hasConfiguration(self):
        """RPC wrapper for ConfigurableComponent"""
        return self.HasConfiguration()

    def _callMethod(self, method, msg):
        argspeclist = self.MethodRegister[msg.func]['args']
        if len(argspeclist) > 1:
            return method(**msg.arg)
        elif len(argspeclist) == 1:
            return method(msg.arg)
        else:
            return method()

    def _checkArgs(self, msg):
        # TODO:
        # * This needs reverse testing. Supplying superfluous args isn't healthy.
        # * Better checking and error reporting
        # * Needs moar secure handling and logical checking of args etc.

        argspeclist = self.MethodRegister[msg.func]['args']
        self.logdebug("SPECIFICATION: '%s'" % argspeclist)


        if len(argspeclist) == 0: # Method has no arguments
            self.loginfo("Method '%s' (no args) called." % msg.func)
            return True, 'No args.'
        elif isinstance(msg.arg, dict): # Sender sent more than one argument
            # TODO: Checking the args isn't doing good here. We'd better check the specs ;)
            args = msg.arg
            self.loginfo("Method '%s' (multiple args) called. Checking parameters." % msg.func)

            # TODO: with this, specified args HAVE to be supplied
            # Consider optional and required args as possibly better alternative
            # But how to best specify that in an unobscured way?

            for param in args:
                self.logdebug("Being checked: %s" % param)
                try:
                    argspec = argspeclist[param]
                    self.logdebug(argspec)
                    if type(args[param]) != argspec[0]:
                        warning = "Argument type error: %s is %s - expected %s" % (param, type(args[param]), argspec)
                        self.logwarn(warning)
                        return False, warning
                except Exception as e:
                    self.logerror(e)
                    return False, "Unknown Error %s" % e
            return True, "All args valid."
        else: # Sender sent only one "default" parameter
            self.loginfo("Method '%s' (default parameter) called. Checking default parameter." % msg.func)
            argspec = list(argspeclist.values())[0]
            self.logdebug("Spec: %s Arg: %s" % (argspec, msg.arg))

            if type(msg.arg) != argspec[0]:
                warning = "Argument type error: %s expected." % (argspec[0])
                self.logwarn(warning)
                return False, warning
            else:
                return True, "Default arg valid."

    def handleRPC(self, msg):
        """Handles RPC requests by
        * first checking for the correct recipient
        * looking up wether the RPC method actually exists
        * trying to get a hold on to the actual method
        * checking the delivered arguments against the method's specification
        * calling it
        * returning the methods result as RPC response

        = Important Requirement =
        For every component that intends to do RPC and react to requests,
        the function 'main' has to call '''handleRPC(msg)''' upon message
        reception.
        """
        # TODO: Grand unified error responses everywhere, needs a well documented standard.

        if msg.recipient == self.name:
            self.logdebug("Checking RPC request")
            pprint(self.MethodRegister)
            if "rpc"+msg.func in self.MethodRegister:
                self.logdebug("Request for method %s" % msg.func)
                # TODO: Better get the method from self.MR
                method = getattr(self, "rpc_" + msg.func)

                if method:
                    argtestresult, log = self._checkArgs(msg)
                    if argtestresult:
                        self.logdebug("Calling method after successful ArgSpecTest: %s" % log)
                        # Deliver the final result
                        return msg.response(self._callMethod(method, msg))
                    else:
                        self.logwarning("Supplied args were invalid: '%s'" % log)
                        return msg.response((False, log))
                else:
                    self.logerror("Requested Method in register, but not implemented/found.")
                    return msg.response((False, "Method not found."))
            else:
                # Clients should look up the requested method at least once, but may use e.g. caching
                self.logwarning("Requested Method not found: %s" % msg.func)
                return msg.response((False, "Method not found."))
        else:
            self.logerror("Received a message without being the recipient!")

    def _getComponentInfo(self):
        """Returns this component's metadescription including its MethodRegister"""

        return [self.name, self.__doc__, self.MethodRegister]

    def __buildArgSpec3(self, method):
        return inspect.getfullargspec(method[1]).annotations

    def __buildArgSpec2(self, method):
        if self.MR.has_key(method[0]):
            return self.MR[method[0]]
        else:
            self.logerror("Argspec for method '%s' not found." % method[0])
            return False

    def _buildMethodRegister(self):
        """Builds the RPC register by analyzing all methods beginning with "rpc_".
        Every found method will be added to the register together with its annotations.
        """
        # TODO: This has to be thrown out in a higher subclass of Axon.Component, it is not only relevant to RPC
        # TODO: Consider a tiny datastructure to store the data in a conveniently addressable way. (50% ;)

        self.MethodRegister = {}
        self.logdebug("Building method register.")

        try:
            unicode
            ArgSpecBuilder = self.__buildArgSpec2
        except NameError:
            ArgSpecBuilder = self.__buildArgSpec3

        for method in inspect.getmembers(self):
            if method[0].startswith("rpc_") or method[0] == "__init__":
                if method[0] == "__init__":
                    name = "initialization"
                else:
                    name = method[0][4:]

                params = ArgSpecBuilder(method)
                self.logdebug("Parameters for '%s': '%s'" % (method[0], params))

                # TODO: Check for other stuff and log it accurately.
                if params: # This might become more complex
                    doc = inspect.getdoc(method[1])
                    self.MethodRegister[name] = {"args": params, "doc": doc}
                else:
                    self.logerror("Not exporting undocumented RPC function: '%s'" % method[0])

        return True

    def __init__(self):
        """Initializes this RPC Component. Don't forget to call super(RPCComponent, self).__init__()"""
        super(RPCComponent, self).__init__()

        # Python 2.x Methodregister
        self.MR['__init__'] = [None]
        self.MR['rpc_updateComponentInfo'] = [None]
        self.MR['rpc_getComponentInfo'] = [None]
        self.MR['rpc_getConfiguration'] = [None]
        self.MR['rpc_writeConfiguration'] = [None]
        self.MR['rpc_readConfiguration'] = [None]
        self.MR['rpc_hasConfiguration'] = [None]

        self._buildMethodRegister()


    def main(self):
        """Start the already initialized component and wait for messages.
        Manually (currently) process each RPC request and call the appropriate function.
        Send back the response of the function call as RPC answer.
        """
        while True:
            while not self.anyReady():
                yield 1
            msg = None
            response = None

            if self.dataReady("inbox"):
                self.logdebug("Handling incoming rpc messages.")
                msg = self.recv("inbox")
                response = self.handleRPC(msg)
            if response:
                self.logdebug("Sending response to '%s'" % response.recipient)
                self.send(response, "outbox")
            yield 1

    def shutdown(self):
        """Shutdown of RPC Components is heavy WiP!"""
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

# TODO: These (and other baseclass components) shouldn't be listed unless being tested
# * ConfigurableComponent
# * Dispatcher
ComponentTemplates["RPCComponent"] = [RPCComponent, "RPC capable Component"]
