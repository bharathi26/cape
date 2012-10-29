#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      Simple Thrust Control Virtual Component (SRCVC)
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

from RAIN.System import Registry
from RAIN.System import RPCComponent
from RAIN.Messages import Message

import time

class Timer(RPCComponent.RPCComponent):
    events = []

    def __init__(self):
        self.MR['rpc_addTimer'] = {'usec': [float, "Unix timestamp of event"],
                                   'message': [Message, "Message to transmit on event"]
                                  }
        self.MR['rpc_addCountdown'] = {'usec': [float, "Seconds to count down"],
                                       'message': [Message, "Message to transmit on countdown"]
                                      }
        self.MR['rpc_listTimers'] = {}
        super(Timer, self).__init__()

    def rpc_addTimer(self, usec, message):
        """
        Stores a timed message.
        """
        if time.time() > usec:
            return (False, "Past events can't be handled")
        else:
            event = (usec, message)
            for ev in self.events:
                if ev[0] > usec:
                    self.events.insert(self.events.index(ev), event)
                    break
            if event not in self.events:
                self.events.append(event)
            self.loginfo("New event logged. Eventtime: %s" % usec)
            return True

    def rpc_addCountdown(self, usec, message):
        """
        Calculates the time, when a given countdown runs out and stores a message.
        """
        now = time.time()
        return self.rpc_addTimer(usec, message)

    def rpc_delTimer(self, usec):
        """
        NOT IMPLEMENTED!
        Deletes a specified event.
        """
        args = {'usec': [float, 'Time of to be deleted event.']}

        if usec in self.events:
            return True
        else:
            return (False)

    def rpc_listTimers(self):
        """
        Returns the list of currently listed timers.
        """
        return self.events

    def main(self):
        """
        Check for listed events to happen and execute them.
        """
        while True:
            while not self.anyReady():
                currenttime = time.time()
                if len(self.events) > 0:
                    if currenttime > self.events[0][0]:
                        self.send(self.events[0][1])
                        del self.events[0]
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


Registry.ComponentTemplates['Timer'] = [Timer, "Simple Timer Component"]
