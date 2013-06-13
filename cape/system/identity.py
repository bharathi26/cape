#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
#     - identity Information Provider -
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

import uuid

from cape.system import logger, version, configuration

from pprint import pprint

SystemName = DefaultSystemName = "DEFAULT"
SystemClass = DefaultSystemClass = "DEFAULT"
SystemUUID = DefaultSystemUUID = int(uuid.uuid4())

Systemidentity = {'name': SystemName,
                  'class': SystemClass,
                  'UUID': SystemUUID
                  }


def setupidentity():
    global SystemName
    global SystemClass
    global SystemUUID
    global Systemidentity


    if 'IDENTITY' in configuration.Configuration:
        config = configuration.Configuration['IDENTITY']

        SystemName = config.get('name', None)
        if not SystemName:
            SystemName = DefaultSystemName
            logger.systemwarn("No SystemName set! Using default: '%s'" % SystemName)
        SystemClass = config.get('class', None)
        if not SystemClass:
            SystemClass = DefaultSystemClass
            logger.systemwarn("No SystemClass set! Using default: '%s'" % SystemClass)
        SystemUUID = config.get('UUID', None)
        if not SystemUUID:
            SystemUUID = DefaultSystemUUID
            logger.systemwarn("No SystemUUID set! Using default: '%s'" % SystemUUID)

        logger.systeminfo("System name configured from configuration", facility="IDENTITY")
    else:
        logger.systemwarn("Uh oh.", facility='IDENTITY')
        if version.node:
            SystemName = DefaultSystemClass + version.node
            SystemClass = DefaultSystemClass
            SystemUUID = DefaultSystemUUID
            logger.systemwarn("No configured name. You might want to configure this.", facility="IDENTITY")
        else:
            SystemName = DefaultSystemClass + DefaultSystemName
            SystemClass = DefaultSystemClass
            SystemUUID = DefaultSystemUUID
            logger.systemwarn("Default system name chosen! You might want to configure this.", facility="IDENTITY")

    Systemidentity = {'name': SystemName,
                      'class': SystemClass,
                      'UUID': SystemUUID
                      }
    configuration.Configuration['IDENTITY'] = Systemidentity



def test():
    """N/A: Should test the identity information system."""
    print("System Name: %s\nSystem Class: %s\nSystem UUID: %s" % (SystemName, SystemClass, SystemUUID))
    print("No other tests yet.")


if __name__ == "__main__":
    test()
