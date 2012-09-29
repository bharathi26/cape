#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#    Simple Course Controller
#    Copyright (C) 2012 Martin Ling <martin@earth.li>
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

from ANRV.System import Registry
from ANRV.System.RPCComponent import RPCComponent
from time import time

class CourseController(RPCComponent):

    def __init__(self):
        self.MR['rpc_setCourse'] = {'default': [float, 'New course bearing (0-360)']}
        self.MR['rpc_getRudderAngle'] = {'default': [float, 'Current heading']}
        super(CourseController, self).__init__()
        self.Configuration.update({
            'ProportionalGain': 0.1,
            'DerivativeGain': 0.1})
        self.previousHeading = None
        self.previousTime = None

    def rpc_setCourse(self, newCourse):
        if isinstance(newCourse, float) and 0 <= newCourse < 360:
            self.course = newCourse
            return True
        else:
            return (False, "WRONG ARGUMENT")

    def rpc_getRudderAngle(self, currentHeading):
        if isinstance(currentHeading, float) and 0 <= currentHeading < 360:
            currentTime = time()
            correction = self.course - currentHeading
            if correction > 180:
                correction -= 360
            elif correction < -180:
                correction += 360
            rudder = self.Configuration['ProportionalGain'] * correction
            if self.previousHeading is not None:
                gain = self.Configuration['DerivativeGain']
                change = currentHeading - self.previousHeading
                interval = currentTime - self.previousTime
                rudder -= gain * change / interval
            if rudder < -1:
                rudder = -1
            elif rudder > 1:
                rudder = 1
            self.previousHeading = currentHeading
            self.previousTime = currentTime
            return (True, rudder)
        else:
            return (False, "WRONG ARGUMENT")

Registry.ComponentTemplates['CourseController'] = [CourseController, "Automatic Course Controller"]
