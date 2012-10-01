#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#     - Registry and associated components
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

ComponentTemplates = {} # Schema: {'ComponentDescriptiveName': [class, 'Description'],}
Components = {}         # Schema: {'ComponentName': Component}
Dispatcher = None
Modules = {}

from ANRV.System import Configuration
from ANRV.System import Logging

import glob, os, imp

#TODO: Reintegrate Registry Component.
# This involves clearing up a circular import, since RPCComponent needs to be imported
# for the RegistryComponent.

def _findModules(Paths):
    # TODO: ...LOTS
    # * Make sure only ONE module containing a certain object is listed (the newest?) or with version numbers?
    # * Inspection of Components should happen - and thoroughly
    # * Modules should possibly signed and here, verification could happen (or better: upon (re)loading?)
    # * ...
    def gatherModules(path):
        Logging.systemdebug(os.path.dirname(path)+"/*.py")
        modules = {}
        for f in glob.glob(os.path.dirname(path)+"/*.py"):
            Logging.systemdebug("Inspecting '%s'" % f)
            modules[os.path.basename(f)[:-3]] = f
        Logging.systemdebug("Found modules: %s" % modules)
        return modules

    modules = {}
    for path in Paths:
        Logging.systemdebug("Inspecting modulepath '%s'" % path)
        modules.update(gatherModules(path))

    return modules

def _loadModule(modfilename):
    pass
    #if modname in sys.modules:
    #mod = imp.new_module(
    #return __import__(Filename)

def _updateModule(Name):
    reload(Name)


Logging.systeminfo("Looking for modules")
ModuleFiles = _findModules(Configuration.ModulePaths)
Logging.systeminfo("Found %i modules. Loading..." % len(ModuleFiles))

for module in ModuleFiles:
    Logging.systemdebug("Loading %s" % module)
    Modules[module] = _loadModule(ModuleFiles[module])

Logging.systeminfo("All modules loaded.")

def test():
    """N/A: Should test the version information system."""
    print("No tests yet.")

if __name__ == "__main__":
    test()
