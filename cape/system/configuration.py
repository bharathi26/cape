#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
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

#import configobj
import json, jsonpickle
import os.path
import sys

from pprint import pprint

# Filename of main configuration
ConfigFilename = "/etc/cape/cape.conf"

Configuration = {}

def readConfig(filename):
    """
    Reads a configuration file.
    """
    global Configuration

    def convert(input):
        if isinstance(input, dict):
            return dict([(convert(key), convert(value)) for key, value in input.iteritems()])
        elif isinstance(input, list):
            return [convert(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    try:
        #newconfig = configobj.ConfigObj(filename,
        #                                unrepr=True,
        #                                interpolation=False)
        configfile = open(filename, "r")
        newconfig = json.load(configfile, object_hook=convert)
        configfile.close()

        Configuration = newconfig
        return True
    except Exception as error:
        # TODO: Handle this better, friendlier
        print("Configuration error: %s" % error)


def reloadConfig():
    """
    Reloads the global configuration.
    """
    global Configuration
    Configuration.reload()
    return True


def writeConfig():
    """
    Writes the global configuration.
    """
    global Configuration
    global ConfigFilename

    try:
        configfile = open(ConfigFilename, "w")
        #json.dump(Configuration, configfile, indent=True)
        configfile.write(jsonpickle.encode(Configuration))
        configfile.close()

        return True
    except Exception as error:
        # TODO: Handle this better, friendlier
        print("Configuration error: %s" % error)

def setupConfig(filename=ConfigFilename):
    """
     Prepares a configuration file and loads it.
     """
    global ConfigFilename

    if not os.path.exists(ConfigFilename):
        print("""Configuration file not found!
        Copy the sample in cape/doc/cape.conf.example to /etc/cape/cape.conf for now.""")
        sys.exit(23)

    readConfig(ConfigFilename)

def test():
    """N/A: Should test the configuration system."""
    # TODO: Needs testing. Heavy.
    print("No real tests yet")

if __name__ == "__main__":
    test()
