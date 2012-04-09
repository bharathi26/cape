#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#     - Joystick Configuration Database -
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

ROLL = 'Roll'
PITCH = 'Pitch'
YAW = 'Yaw'
THRUST = 'Thrust'
HOLD = 'Hold'
REVERSE = 'Reverse'
BOOST = 'Boost'
FULLSTOP = 'Fullstop'
UNASSIGNED = 'Unassigned'
BAD = 'Bad'

JoystickDB = {('Logitech Logitech Extreme 3D Pro',
               'Logitech Logitech Extreme 3D'):{
                'buttons': {0:BOOST,                # 'Fire'
                            1:FULLSTOP,             # 'Thumb'
                            2:'Thumb_LowerLeft',
                            3:'Thumb_LowerRight',
                            4:'Thumb_UpperLeft',
                            5:'Thumb_UpperRight',
                            6:HOLD,                 # 'Seven'
                            7:BAD,                  # 'Eight'
                            8:'Nine',
                            9:'Ten',
                            10:REVERSE,             # 'Eleven'
                            11:'Twelve'},
               'axes': {0:ROLL, # 'Roll'
                      1:PITCH,  # 'Pitch'
                      2:YAW,    # 'Yaw'
                      3:THRUST},# 'Thrust'
               'correction': {0:lambda v: v,
                              1:lambda v: v,
                              2:lambda v: v/2,
                              3:lambda v: v}

               }
             }


