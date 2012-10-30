#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software - Message Objects
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

class BaseMessage(object):
    """Base Message class.
    Contains Origin, Type and Content of a basic message.
    """
    content = ""
    origin = ""
    msgtype = ""

    def __init__(self, content, origin, msgtype):
        self.content = content
        self.origin = origin
        self.msgtype = msgtype

    def __str__(self):
        return str(self.content)

class I2CMessage(BaseMessage):
    pass

class NMEAMessage(BaseMessage):
    # TODO: Evaluate and/or integrate http://code.google.com/p/pynmea/
    _content = ""
    def __str__(self):
        return str(self.content)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

