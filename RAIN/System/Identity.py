#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 RAIN Operating Software
#     - Identity Information Provider -
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

import os
import uuid

from RAIN import Version
from RAIN.System import Logging
from RAIN.System import Configuration

SystemName = DefaultSystemName = "DEFAULT"
SystemClass = DefaultSystemClass = "DEFAULT"
SystemUUID = DefaultSystemUUID = uuid.uuid4()

if 'IDENTITY' in Configuration.Configuration.sections:
    config = Configuration.Configuration['IDENTITY']
    SystemName = config.get('name', DefaultSystemName)
    SystemClass = config.get('class', DefaultSystemClass)
    SystemUUID = config.get('uuid', DefaultSystemUUID)
    Logging.systeminfo("System name configured from configuration", facility="IDENTITY")
else:
    if Version.node:
        SystemName = DefaultSystemClass + Version.node
        SystemClass = DefaultSystemClass
        SystemUUID = DefaultSystemUUID
        Logging.systemwarn("No configured name. You might want to configure this.", facility="IDENTITY")
    else:
        SystemName = DefaultSystemClass + DefaultSystemName
        SystemClass = DefaultSystemClass
        SystemUUID = DefaultSystemUUID
        Logging.systemwarn("Default system name chosen! You might want to configure this.", facility="IDENTITY")

def test():
    """N/A: Should test the Identity information system."""
    print("System Name: %s\nSystem Class: %s\nSystem UUID: %s" % (SystemName, SystemClass, SystemUUID))
    print("No other tests yet.")


if __name__ == "__main__":
    test()
