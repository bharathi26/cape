#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      - Mixin with logging capabilities
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

from RAIN.System import Logging
#from RAIN.System.Registry import ComponentTemplates

class LoggableComponent(object):
    """Basic loggable Component.

    TODO:
    * Central logging facility component
    * Documentation
    * Handling of attribute calls
    * RPC related stuff? later in the tree
    """

    def __init__(self):
        try:
            self.logdebug("Beginning component logging.")
        except AttributeError:
            self.name = "STUPIDLOGGABLE"
            self.logdebug("DON'T HAVE A NAME, ME SIMPLE LOGGABLE MIXIN.")

    def _formMessage(self, msg):
        try:
            return Logging.formMessage(self.name[self.name.rindex(".") + 1:], msg)
        except AttributeError:
            return Logging.formMessage("UNNAMED", msg)

    def logdebug(self, msg):
        Logging.debug(self._formMessage(msg))

    def loginfo(self, msg):
        Logging.info(self._formMessage(msg))

    def logwarn(self, msg):
        Logging.warn(self._formMessage(msg))

    def logwarning(self, msg):
        Logging.warn(self._formMessage(msg))

    def logerror(self, msg):
        Logging.error(self._formMessage(msg))

    def logcritical(self, msg):
        Logging.critical(self._formMessage(msg))

#ComponentTemplates["LoggableComponent"] = [LoggableComponent, "Loggable Component"]
