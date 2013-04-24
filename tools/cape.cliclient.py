#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    A Kamaelia based cape graphical CLIClient
#    Copyright (C) 2011-2013  riot <riot@hackerfleet.org>
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

# TODO:
# * configurable address
# * evaluate additional capabilities of TextDisplayer component
# * evaluate additional capabilities of Textbox component
# (If not sufficient - replace them!)

from Kamaelia.Chassis.Pipeline import Pipeline
from Kamaelia.Util.Console import ConsoleReader, ConsoleEchoer
from Kamaelia.Internet.TCPClient import TCPClient


Pipeline( ConsoleReader(),
          TCPClient("127.0.0.1", 55555),
          ConsoleEchoer(),
).run()
