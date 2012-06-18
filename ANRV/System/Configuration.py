#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#     - Configuration and associated components
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

#import jsonpickle
import configparser
import os.path
import logging


DefaultFilename = "anrv.conf"

Configuration = configparser.ConfigParser()

def _getConfigFilename(filename):
    # TODO: This is stupid. Either read ONE configfile (which?) or read them one after another;
    # The latter would allow overwriting by the user.
    # Currently only the last one found will be inspected, wich works during development and testing
    paths = ['/etc/', '/etc/anrv/', os.path.expanduser('~/.'), os.path.expanduser('~/.anrv/')]

    configfile = None

    for item in paths:
        name = item + filename
        logging.debug("Trying %s." % name)
        if os.path.exists(name):
            logging.debug("Works")
            configfile = name

    return configfile


def _readConfig(filename):
    try:
        newconfig = configparser.ConfigParser()
        newconfig.read(filename)
        logging.info("Successfully read configuration file '%s'" % filename)
    except: # TODO: Catch more specific!!!
        newconfig = False
        logging.error("Couldn't open configuration file '%s'" % filename)
    return newconfig

def test():
    """N/A: Should test the configuration system."""
    # TODO: Needs testing. Heavy.
    print("No real tests yet")

logging.info("Determining configuration filename")
Filename = _getConfigFilename(DefaultFilename)
logging.info("Loading configuration from '%s'" % Filename)
Configuration = _readConfig(Filename)
logging.info("Configuration successfully loaded") # TODO: YUCK! This doesn't compute. All errors being ignored.

if __name__ == "__main__":
    test()
