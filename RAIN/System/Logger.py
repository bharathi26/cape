#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#      Logging Tools and Components
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

import logging as _logging

logger = _logging.getLogger('rain')

import sys

class ConsoleHandler(_logging.StreamHandler):
    """A handler that logs to console in the sensible way.

    StreamHandler can log to *one of* sys.stdout or sys.stderr.

    It is more sensible to log to sys.stdout by default with only error
    (logging.ERROR and above) messages going to sys.stderr. This is how
    ConsoleHandler behaves.
    """

    def __init__(self):
        _logging.StreamHandler.__init__(self)
        self.stream = None # reset it; we are not going to use it anyway

    def emit(self, record):
        if record.levelno >= _logging.ERROR:
            self.__emit(record, sys.stderr)
        else:
            self.__emit(record, sys.stdout)

    def __emit(self, record, strm):
        self.stream = strm
        _logging.StreamHandler.emit(self, record)

    def flush(self):
        # Workaround a bug in logging module
        # See:
        #   http://bugs.python.org/issue6333
        if self.stream and hasattr(self.stream, 'flush') and not self.stream.closed:
            _logging.StreamHandler.flush(self)

def setupLogger(lvl=_logging.DEBUG):
    logger = _logging.getLogger('rain')
    from RAIN.System.Configuration import Configuration as ConfigurationDB

    if 'LOGGING' in ConfigurationDB.sections:
        logconfig = ConfigurationDB['LOGGING']

        logger.setLevel(logconfig['level'])

        if logconfig.has_key('format'):
            globalFormatter = _logging.Formatter(logconfig['format'])
        else:
            globalFormatter = _logging.Formatter('%(asctime)s [%(levelname)8s]:%(message)s')

        for handlername, handler  in logconfig['handlers'].items():
            #logger.debug("Adding Handler '%s'" % handler)

            if handler['type'] == 'file':
                newhandler = _logging.FileHandler(handler['filename'])
            elif handler['type'] == 'console':
                newhandler = ConsoleHandler()
            if handler.has_key('level'):
                newhandler.setLevel(handler['level'])
            if handler.has_key('format'):
                newFormatter = _logging.Formatter(handler['format'])
                newhandler.setFormatter(newFormatter)
            else:
                newhandler.setFormatter(globalFormatter)
            logger.addHandler(newhandler)

        systeminfo('Configured logging from configuration.')

    else:
        filehandler = _logging.FileHandler('/tmp/rain.log')
        #consolehandler = _logging.StreamHandler()
        logger.addHandler(filehandler)
        #logger.addHandler(consolehandler) # WTF, we get them twice, if that one's added

        logger.setLevel(_logging.DEBUG)
        systeminfo("Configuring logging by default")
        #_logging.basicConfig(format='%(asctime)s [%(levelname)8s]:%(message)s',
        #                     level=lvl)

    #logger.captureWarnings(True)
    systeminfo("Logging started.")

def formMessage(component, msg):
    return "[%20s] %s" % (component, msg)

def log(lvl, msg):
    global logger
    return logger.log(lvl, msg)

def systemcritical(msg, facility="SYSTEM"):
    global logger
    return logger.critical(formMessage(facility, msg))

def systemerror(msg, facility="SYSTEM"):
    global logger
    return logger.error(formMessage(facility, msg))

def systemwarn(msg, facility="SYSTEM"):
    global logger
    return logger.warn(formMessage(facility, msg))

def systeminfo(msg, facility="SYSTEM"):
    global logger
    return logger.info(formMessage(facility, msg))

def systemdebug(msg, facility="SYSTEM"):
    global logger
    return logger.debug(formMessage(facility, msg))

def debug(msg):
    global logger
    return logger.debug(msg)
def warn(msg):
    global logger
    return logger.warn(msg)
def warning(msg):
    global logger
    return logger.warning(msg)
def info(msg):
    global logger
    return logger.info(msg)
def error(msg):
    global logger
    return logger.error(msg)
def critical(msg):
    global logger
    return logger.critical(msg)
