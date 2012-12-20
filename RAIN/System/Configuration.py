#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
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

import configobj
import os.path

#TODO Rewrite the file/module finding...

# General paths to look for configuration and module data
Paths = DefaultPaths = {1: '/etc/rain/',
                        2: os.path.expanduser('~/.'),
                        3: os.path.expanduser('~/.rain/'),
                       }

# Filename of main configuration
ConfigFilename = DefaultConfigFilename = "rain.conf"

# Pathname to look for modules in
ModulePath = DefaultModulePath = "modules/"

# Actual found module paths
ModulePaths = []

# TODO:
# * Modules shouldn't be stored along configuration and only looked for in
#   trusted locations
# * Segmentation of Configurationdata - desired? Or only one host-exclusive
#   configuration?
#   (i.e. basic config is loaded from a general source, userdata can overwrite)

Configuration = configobj.ConfigObj()


def _getConfigFilename(filename=None):
    # TODO: This is stupid. Either read ONE configfile (which?) or read them
    # one after another. The latter would allow overwriting by the user.
    # Currently only the last one found will be inspected, wich works 
    # during development and testing

    configfile = None

    if filename and os.path.exists(filename):
        configfile = filename
    else:
        # TODO: Like this, using a dict with preference value is useless.
        # Needs config segmentation or clearing.
        for key, path in Paths.items():
            name = path + DefaultConfigFilename

            if os.path.exists(name):
                configfile = name

    return configfile


def _getModulePath(path=DefaultModulePath):
    modulepaths = []

    for key, path in Paths.items():
        name = path + ModulePath
        if os.path.exists(name):
            modulepaths.append(name)

    return modulepaths


def readConfig(filename=DefaultConfigFilename):
    """
    Reads a configuration file.
    """
    global Configuration
    try:
        newconfig = configobj.ConfigObj(filename,
                                        unrepr=True,
                                        interpolation=False)
        Configuration = newconfig
        return True
    except configobj.UnknownType as error:
        # TODO: do not silently ignore this!
        pass


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

    Configuration.write()
    return True


def setupConfig(filename=ConfigFilename):
    """
     Prepares a configuration file and loads it.
     """
    Filename = _getConfigFilename(filename)

    readConfig(Filename)

    ModulePaths = _getModulePath(ModulePath)


def test():
    """N/A: Should test the configuration system."""
    # TODO: Needs testing. Heavy.
    print("No real tests yet")

if __name__ == "__main__":
    test()
