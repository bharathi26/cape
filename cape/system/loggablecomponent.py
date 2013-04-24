#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#      - Mixin with logger capabilities
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

from cape.system import logger
#from cape.system.registry import ComponentTemplates

class LoggableComponent(object):
    """Basic loggable Component.

    TODO:
    * Central logger facility component
    * Documentation
    * Handling of attribute calls
    * RPC related stuff? later in the tree
    """

    def __init__(self):
        try:
            self.logdebug("Beginning component logger.")
        except AttributeError:
            self.name = "STUPIDLOGGABLE"
            self.logdebug("DON'T HAVE A NAME, ME SIMPLE LOGGABLE MIXIN.")

    def _formMessage(self, msg):
        try:
            return logger.formMessage(self.name[self.name.rindex(".") + 1:], msg)
        except AttributeError:
            return logger.formMessage("UNNAMED", msg)

    def log(self, lvl, msg):
        logger.log(lvl, self._formMessage(msg))

    def logdebug(self, msg):
        logger.debug(self._formMessage(msg))

    def loginfo(self, msg):
        logger.info(self._formMessage(msg))

    def logwarn(self, msg):
        logger.warn(self._formMessage(msg))

    def logwarning(self, msg):
        logger.warn(self._formMessage(msg))

    def logerror(self, msg):
        logger.error(self._formMessage(msg))

    def logcritical(self, msg):
        logger.critical(self._formMessage(msg))

#ComponentTemplates["LoggableComponent"] = [LoggableComponent, "Loggable Component"]
