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

import ANRV.System.Configuration
from ANRV.System.RPCComponent import RPCComponent


#TODO: Reintegrate Registry Component.
# This involves clearing up a circular import, since RPCComponent needs to be imported
# for the RegistryComponent.



def test():
    """N/A: Should test the version information system."""
    print("No tests yet.")

if __name__ == "__main__":
    test()
