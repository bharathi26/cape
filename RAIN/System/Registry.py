#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
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
Components = []         # Schema: ['ComponentName']
Directory = {}          # Schema: {'LookupName': ComponentName}
Dispatcher = None
Modules = {}

from RAIN.System import Configuration
from RAIN.System import Logger

from pkg_resources import iter_entry_points

#TODO: Reintegrate Registry Component.
# This involves clearing up a circular import, since RPCComponent needs to be imported
# for the RegistryComponent.

def findModules():
    # TODO: ...LOTS
    # * Make sure only ONE module containing a certain object is listed (the newest?) or with version numbers?
    # * Inspection of Components should happen - and thoroughly
    # * Modules should possibly signed and here, verification could happen (or better: upon (re)loading?)
    # * ...
    def gatherModules():
        dists = {}
        for ep in iter_entry_points(group='rain.components', name=None):
            Logger.systemdebug("Inspecting module '%s'" % ep)
            if not dists.has_key(ep.dist):
                dists[ep.dist] = {}
            dists[ep.dist][ep.name] = ep.load()

        for dist, mods in dists.items():
            Logger.systemdebug("Module Entrypoint: [%s] ('%s')" % (dist, mods))
            for templatename, template in mods.items():
                Logger.systemdebug("Component template found: [%s]" % templatename)
                ComponentTemplates[str(templatename)] = [template, template.__doc__]
            
            
        Logger.systemdebug("Found Distributions: %s" % dists.keys())
        Logger.systemdebug("Found Templates: %s" % ComponentTemplates.keys())
        Logger.systeminfo("Found %i Templates." % len(ComponentTemplates))

    gatherModules()
#    for path in Paths:
#        Logger.systemdebug("Inspecting modulepath '%s'" % path)
#        modules.update(gatherModules(path))

    return True


def _loadModule(modfilename):
    pass
    #if modname in sys.modules:
    #mod = imp.new_module(
    #return __import__(Filename)


def _updateModule(Name):
    reload(Name)



#for module in ModuleFiles:
#    Logger.systemdebug("Loading %s" % module)
#    Modules[module] = _loadModule(ModuleFiles[module])

def test():
    """N/A: Should test the version information system."""
    print("No tests yet.")

if __name__ == "__main__":
    test()
