#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      - Message Recorder -
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
from Kamaelia.File.Append import Append

class Recorder(Axon.Component.component):
    """\
    Recorder -> component that records every inbox message to a file

    Uses the following keyword argyments::

    * filename - File to append to (required)
    * hold_open - keep file open (default: True)
    """
    Inboxes = {
        "inbox"   : "data to append to the end of the file.",
        "control" : "Send any message here to shut this component down"
    }
    Outboxes = {
        "outbox"  : "a copy of the message is forwarded here",
        "signal"  : "passes on the message used to shutdown the component"
    }
    # Arguments

    filename = None
    hold_open = True

    def __init__(self, **argd):
        """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
        super(Recorder, self).__init__(**argd)

        if self.filename == None:
            raise ValueError("Expected a filename")
        self.F = None
        self.shutdown = Axon.Ipc.producerFinished()

    def writeChunk(self,chunk):
        if self.hold_open:
            if self.F == None:
                self.F = open(self.filename, "a")

            self.F.write(chunk)
            self.F.flush()
        else:
            F = open(self.filename, "a")
            F.write(chunk)
            F.flush()
            F.close()

    def main(self):
        while not self.dataReady("control"):
            for chunk in self.Inbox("inbox"):
                 self.writeChunk(chunk)
            if not self.anyReady():
                self.pause()
            yield 1
        self.shutdown = self.recv("control")
        self.stop()

    def stop(self):
        self.send(self.shutdown, "signal")
        if self.F != None:
            self.F.close()
            self.F = None
        super(Recorder, self).stop()

