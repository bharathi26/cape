#!/usr/bin/python3
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      - Dispatcher Component
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
from Axon.AdaptiveCommsComponent import AdaptiveCommsComponent

from RAIN.System.LoggableComponent import LoggableComponent
from RAIN.System import Registry
from RAIN.Messages import Message

class Dispatcher(AdaptiveCommsComponent, LoggableComponent):
    inboxes = {'inbox': 'Dispatcher Inbox',
               'control': 'Not used yet.'}
    outboxes = {'outbox': 'Dispatcher Outbox',
                'signal': 'Not used yet.'}
    Components = []

    def __init__(self):
        AdaptiveCommsComponent.__init__(self)
        LoggableComponent.__init__(self)

    def RegisterComponent(self, thecomponent):
        self.logdebug("Trying to register new component")
        self.addChildren(thecomponent)

        newIn = self.addInbox(thecomponent.name)
        newOut = self.addOutbox(thecomponent.name)

        newState = "WAITING"
        linkToComponent = self.link((self, newOut), (thecomponent, "inbox"))
        linkFromComponent = self.link((thecomponent, "outbox"), (self, "inbox"))

        resource = thecomponent

        inboxes = [newIn]
        outboxes = [newOut]
        info = (newState, linkToComponent, linkFromComponent)
        self.trackResourceInformation(resource, inboxes, outboxes, info)

        self.trackResource(resource, newIn)

        thecomponent.activate()
        if isinstance(thecomponent, Axon.ThreadedComponent.threadedcomponent):
            pass

        self.Components.append(thecomponent)

        self.loginfo("Registered new component '%s'" % thecomponent.name)

        return True

    def main(self):
        while True:
            while not self.anyReady():
                yield 1 # Twiddle thumbs.

            msg = self.recv()
            # Input! We have to act.

            if isinstance(msg, Message):
                response = None
                self.loginfo("Received message from '%s' for '%s'" % (msg.sender, msg.recipient))
                if msg.recipient in self.inboxes:
                    self.send(msg, msg.recipient)
                elif msg.recipient == self.name:
                    self.logcritical('A MESSAGE FOR ME. NOW WHAT, SMARTIEPANTS?')
                    #response = msg.response((False, "Not available."))
                else:
                    self.logwarn('MESSAGE WITH ERRONEOUS RECIPIENT RECIEVED: %s\n%s\n' % (msg, self.inboxes))
                    #response = Message(sender=self.name, recipient=msg.sender, func=msg.func, arg=(False,
                    # "Recipient not found."))
                    # TODO: maybe we should include the original timestamp, look in RAIN/Messages.py for more on that
                    # topic.
                if response:
                    if response.recipient in self.inboxes:
                        self.logdebug("Responding to '%s'" % response.recipient)
                        self.send(response, response.recipient)
                    else:
                        self.logerror("Response to '%s' can't be sent, not available." % response.recipient)
            else:
                self.logerror("Received something weird non-message: '%s'" % msg)

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

Registry.ComponentTemplates['Dispatcher'] = [Dispatcher, "Basic Dispatcher"]
