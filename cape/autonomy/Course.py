#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 cape Operating Software
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

from cape.system import registry
from cape.system.rpccomponent import RPCComponent
from cape.messages import Message
from time import time

class CourseController(RPCComponent):
    def __init__(self):
        self.MR['rpc_setCourse'] = {'newCourse': [float, 'New course bearing (0-360)']}
        self.MR['rpc_setSpeed'] = {'newSpeed': [float, 'Target speed in knots']}
        self.MR['rpc_updateControls'] = {
            'latitude': [float, 'Current latitude'],
            'longitude': [float, 'Current longitude'],
            'track': [float, 'Current track'],
            'speed': [float, 'Current speed']}
        super(CourseController, self).__init__()
        self.Configuration.update({
            'rudderProportionalGain': 0.1,
            'rudderDerivativeGain': 0.1,
            'thrustProportionalGain': 0.1,
            'thrustDerivativeGain': 0.1,
            'tracker': ""})
        self.course = None
        self.speed = None
        self.previousTime = None

    def main_prepare(self):
        self.loginfo("Controller subscribing to tracker")
        request = Message(sender=self.name, recipient=self.Configuration['tracker'],
                          func="subscribe", arg={'name': self.name, 'function': 'updateControls'})
        self.send(request, "outbox")

    def rpc_setCourse(self, newCourse):
        self.course = newCourse

    def rpc_setSpeed(self, newSpeed):
        self.speed = newSpeed

    def rpc_updateControls(self, latitude, longitude, track, speed):
        currentTime = time()
        if self.course is None:
            return False, "Course not set"
        elif self.speed is None:
            return False, "Speed not set"
        correction = self.course - track
        if correction > 180:
            correction -= 360
        elif correction < -180:
            correction += 360
        rudder = self.Configuration['rudderProportionalGain'] * correction
        if self.previousTime is not None:
            gain = self.Configuration['rudderDerivativeGain']
            change = track - self.previousTrack
            interval = currentTime - self.previousTime
            rudder -= gain * change / interval
        if rudder < -1:
            rudder = -1
        elif rudder > 1:
            rudder = 1
        request = Message(sender=self.name, recipient=self.Configuration['rudder'],
                          func="setRudder", arg={'newangle': float(rudder)})
        self.send(request, "outbox")
        correction = self.speed - speed
        thrust = self.Configuration['thrustProportionalGain'] * correction
        if self.previousTime is not None:
            gain = self.Configuration['thrustDerivativeGain']
            change = speed - self.previousSpeed
            interval = currentTime - self.previousTime
            thrust -= gain * change / interval
        if thrust < 0:
            thrust = 0
        elif thrust > 1:
            thrust = 1
        request = Message(sender=self.name, recipient=self.Configuration['engine'],
                          func="setThrust", arg={'newthrust': float(thrust)})
        self.send(request, "outbox")
        self.previousTrack = track
        self.previousSpeed = speed
        self.previousTime = currentTime
        return True

Registry.ComponentTemplates['CourseController'] = [CourseController, "Automatic Course Controller"]
