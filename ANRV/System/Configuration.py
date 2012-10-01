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
import configobj
import os.path

from ANRV.System import Logging

#TODO Rewrite the file/module finding...

# General paths to look for configuration and module data
Paths = DefaultPaths = {1: '/etc/anrv/', 2: os.path.expanduser('~/.'), 3: os.path.expanduser('~/.anrv/')}

# Filename of main configuration
ConfigFilename = DefaultConfigFilename = "anrv.conf"

# Pathname to look for modules in
ModulePath = DefaultModulePath = "modules/"

# Actual found module paths
ModulePaths = []

# TODO:
# * Modules shouldn't be stored along configuration and only looked for in trusted locations
# * Segmentation of Configurationdata - desired? Or only one host-exclusive configuration?
#   (i.e. basic config is loaded from a general source, userdata can overwrite)

Configuration = configobj.ConfigObj()

def _getConfigFilename(filename=None):
    # TODO: This is stupid. Either read ONE configfile (which?) or read them one after another;
    # The latter would allow overwriting by the user.
    # Currently only the last one found will be inspected, wich works during development and testing

    configfile = None

    if filename and os.path.exists(filename):
        configfile = filename
    else:
        # TODO: Like this, using a dict with preference value is useless. Needs config segmentation or clearing.
        for key, path in Paths.items():
            name = path + DefaultConfigFilename
            Logging.systemdebug("Trying %s." % name)
            if os.path.exists(name):
                Logging.systemdebug("Works")
                configfile = name

    return configfile

def _getModulePath(path=DefaultModulePath):
    modulepaths = []

    for key, path in Paths.items():
        name = path + ModulePath
        Logging.systemdebug("Trying %s." % name)
        if os.path.exists(name):
            Logging.systemdebug("Found module folder: %s" % name)
            modulepaths.append(name)

    return modulepaths

def _readConfig(filename=DefaultConfigFilename):
    global Configuration
    try:
        newconfig = configobj.ConfigObj(filename, unrepr=True)
        Configuration = newconfig
        Logging.systeminfo("Successfully read configuration file '%s'" % filename)
        return True
    except configobj.UnknownType as error:
        Logging.systemerror("Couldn't read configuration: '%s'" % error)

def _reloadConfig():
    global Configuration
    Configuration.reload()
    return True

def _writeConfig():
    global Configuration
    Logging.systeminfo("Configuration: \n%s" % Configuration)
    Configuration.write()
    return True

def setupConfig(filename=ConfigFilename):
    Logging.systeminfo("Determining configuration filename")
    Filename = _getConfigFilename(filename)

    Logging.systeminfo("Loading configuration from '%s'" % Filename)
    _readConfig(Filename)

    Logging.systeminfo("Checking module paths")
    ModulePaths = _getModulePath(ModulePath)
    Logging.systeminfo("Found module paths: %s" % ModulePaths)

def test():
    """N/A: Should test the configuration system."""
    # TODO: Needs testing. Heavy.
    print("No real tests yet")

if __name__ == "__main__":
    test()
