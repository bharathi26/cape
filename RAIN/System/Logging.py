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

#import Axon

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING'  : YELLOW,
    'INFO'     : WHITE,
    'DEBUG'    : BLUE,
    'CRITICAL' : YELLOW,
    'ERROR'    : RED,
    'RED'      : RED,
    'GREEN'    : GREEN,
    'YELLOW'   : YELLOW,
    'BLUE'     : BLUE,
    'MAGENTA'  : MAGENTA,
    'CYAN'     : CYAN,
    'WHITE'    : WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ  = "\033[1m"

class ColorFormatter(_logging.Formatter):

    def __init__(self, *args, **kwargs):
        _logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color     = COLOR_SEQ % (30 + COLORS[levelname])
        message   = _logging.Formatter.format(self, record)
        message   = message.replace("$RESET", RESET_SEQ)

def setupLogger(lvl=_logging.DEBUG):
    _logging.basicConfig(format='%(asctime)s [%(levelname)8s]:%(message)s', level=lvl)

    _logging.captureWarnings(True)
    _logging.info("Logging started.")



def formMessage(component, msg):
    return "[%12s] %s" % (component, msg)

def systemcritical(msg, facility="SYSTEM"):
    return _logging.critical(formMessage(facility, msg))

def systemerror(msg, facility="SYSTEM"):
    return _logging.error(formMessage(facility, msg))

def systemwarn(msg, facility="SYSTEM"):
    return _logging.warn(formMessage(facility, msg))

def systeminfo(msg, facility="SYSTEM"):
    return _logging.info(formMessage(facility, msg))

def systemdebug(msg, facility="SYSTEM"):
    return _logging.debug(formMessage(facility, msg))

def debug(msg):
    return _logging.debug(msg)
def warn(msg):
    return _logging.warn(msg)
def warning(msg):
    return _logging.warning(msg)
def info(msg):
    return _logging.info(msg)
def error(msg):
    return _logging.error(msg)
def critical(msg):
    return _logging.critical(msg)