#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software 
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

from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Chassis.Graphline import Graphline

from ANRV.System import Registry
from ANRV.Messages import Message

from pprint import pprint

class Dispatcher(Axon.AdaptiveCommsComponent.AdaptiveCommsComponent):
    Inboxes = {'inbox'   : 'Dispatcher Inbox',
               'control' : 'Not used yet.'}
    Outboxes = {'outbox' : 'Dispatcher Outbox',
                'signal' : 'Not used yet.'}
    Components = []

    def __init__(self):
        super(Dispatcher, self).__init__(self)


    def RegisterComponent(self, thecomponent):
        newIn  = self.addInbox(thecomponent.name)
        newOut = self.addOutbox(thecomponent.name)

        newState = "WAITING"
        linkToComponent   = self.link((self, newOut), (thecomponent, "inbox"))
        linkFromComponent = self.link((thecomponent, "outbox"), (self, newIn))

        resource = thecomponent

        inboxes = [newIn]
        outboxes = [newOut]
        info = (newState, linkToComponent, linkFromComponent)
        self.trackResourceInformation(resource, inboxes, outboxes, info)

        self.trackResource(resource, newIn)

        return True

#    def main(self):

    def shutdown(self):
        # TODO: Handle correct shutdown
        if self.dataReady("control"):
            msg = self.recv("control")
            return isinstance(msg, Axon.Ipc.producerFinished)

Registry.ComponentTemplates['Dispatcher'] = [Dispatcher, "Basic Dispatcher"]
