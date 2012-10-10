#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#    Prototype of the MS0x00 ANRV Operating Software
#     - Joystick Analyzer (loosely based on Mike Doty's work) -
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

__readme__ = "LOL. Just kidding."

# Original credits:
#######################################
# Code coded by Mike Doty
#
# If you want trackball checking, you will
# have to code it yourself.  Sorry!
#
# Oh, and it just grabs the first joystick.
#   Yes, that makes me lazy.
#
# Released February 8, 2008.
#######################################

# TODO:
# * Outsource useful parts to Kamaelia
# * Network code
# * Add  ANRV Interface Objects
#  * Bandwidth && Latency Meter
#  * Rudder && Thruster Visualization
#  * Messages Window
#   * Filter
#   * Color coding
#   * Dump
#  * OpenGL Display (esp. useful with bathymetry!)
#  * Bitmap import
#  * ship (self) object
#  * OSM import
#  * Landscape, Waterbodies, etc
# * Controller Actions
# * Useful 2D infodisplay
# * Configuration
# * Configuration Window

import pygame
from pygame.locals import *
from time import sleep
from ANRV.Interface.JoystickDescription import *
from math import cos, sin, pi
from time import time
import socket
import sys
import getopt

from .Colors import *


class App:
    def __init__(self,ip="127.0.0.1",port=55555):
        pygame.init()

        pygame.display.set_caption("ANRV Joystick Prototype")

        # Set up the network connection
        self.socket = None
        self.hostname = ip
        self.port = port

        self.connect()

        # Set up the joystick
        pygame.joystick.init()

        self.my_joystick = None
        self.joystick_names = []

        # Enumerate joysticks
        for i in range(0, pygame.joystick.get_count()):
            self.joystick_names.append(pygame.joystick.Joystick(i).get_name())

        print(self.joystick_names)

        # By default, load the first available joystick.
        if (len(self.joystick_names) > 0):
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()

        max_joy = max(self.my_joystick.get_numaxes(),
                      self.my_joystick.get_numbuttons(),
                      self.my_joystick.get_numhats())

        self.screen = pygame.display.set_mode( (max_joy * 40 + 10, 170) )

        self.font = pygame.font.SysFont("Helvetica", 10)

    def connect(self):
        print("Connecting to %s:%i" % (self.hostname, self.port))
        s = None
        for res in socket.getaddrinfo(self.hostname, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                s = None
                continue
            try:
                s.connect(sa)
            except socket.error as msg:
                s.close()
                s = None
                continue
            break
        if s is None:
            print('Could not open socket')
            sys.exit(1)
        else:
            print("Connected!")
        self.socket = s
        request = """{"py/object": "ANRV.Messages.Message", "sender": "ANRV.JoystickRemote", "timestamp": %f, "func": "AddRecipient", "arg": "ANRV.JoystickRemote", "recipient": "JSONServer"}\r\n""" % (time())
        self.socket.sendto(request, (self.hostname, self.port))


    # A couple of joystick functions...
    def check_axes(self, p_axes):
        if (self.my_joystick):
            if (p_axes < self.my_joystick.get_numaxes()):
                return self.my_joystick.get_axes(p_axes)

        return 0

    def check_button(self, p_button):
        if (self.my_joystick):
            if (p_button < self.my_joystick.get_numbuttons()):
                return self.my_joystick.get_button(p_button)

        return False

    def check_hat(self, p_hat):
        if (self.my_joystick):
            if (p_hat < self.my_joystick.get_numhats()):
                return self.my_joystick.get_hat(p_hat)

        return (0, 0)

    def draw_text(self, text, x, y, color, align_right=False):
        surface = self.font.render(text, True, color, (0, 0, 0))
        surface.set_colorkey( (0, 0, 0) )

        self.screen.blit(surface, (x, y))

    def center_text(self, text, x, y, color):
        surface = self.font.render(text, True, color, (0, 0, 0))
        surface.set_colorkey( (0, 0, 0) )

        self.screen.blit(surface, (x - surface.get_width() / 2,
                                   y - surface.get_height() / 2))


    def TransmitRudder(self, value):
        request = """{"py/object": "ANRV.Messages.Message", "sender": "ANRV.JoystickRemote", "timestamp": %f, "func": "SetRudder", "arg": %f, "recipient": "Rudder"}\r\n""" % (time(), value)
        self.socket.sendto(request, (self.hostname, self.port))

    def TransmitThrust(self, value):
        request = """{"py/object": "ANRV.Messages.Message", "sender": "ANRV.JoystickRemote", "timestamp": %f, "func": "SetThrust", "arg": %f, "recipient": "Engine"}\r\n""" % (time(), value)
        self.socket.sendto(request, (self.hostname, self.port))

    def main(self):
        freq = 60
        # TODO: Needs a default for unknown joysticks!
        # print JoystickDB
        JoystickConf = next(v for k,v in list(JoystickDB.items()) if self.joystick_names[0] in k)
   
        if JoystickConf:
            Correction = JoystickConf['correction']
            AxesConf = JoystickConf['axes']
            ButtonConf = JoystickConf['buttons']
        else:
            JoystickConf = None
        axescount = self.my_joystick.get_numaxes()
        buttoncount = self.my_joystick.get_numbuttons()

        axesval = [0.0] * axescount
        oldaxesval = [0.0] * axescount
        offset = [0.0] * axescount
        switched = [0.0] * buttoncount
        toggled = [0.0] * buttoncount
        oldtoggled = [0.0] * buttoncount
        switched = [0] * buttoncount
        hold = True
        reverse = False
        newthrust = False
        newrudder= False
        if JoystickConf:
            supported = "Supported"
            joysticknamecolor = GREEN
        else:
            supported = "Unsupported"
            joysticknamecolor = ORANGE

        while (True):
            sleep(1.0/freq)
            self.g_keys = pygame.event.get()

            self.screen.fill(0)
## This is bad, its blocking :/ Use a Monitor if you want to see what you're doing.
## (This is valid until we have a new Kamaelia based Joystick-Capable Client)
#            recvd= True
#            data = ""
#            while recvd:
#                newdata = self.socket.recv(1024)
#                if len(newdata) == 0:
#                    recvd = not recvd
#                data += newdata
#            print data
            for event in self.g_keys:
                if (event.type == KEYDOWN and event.key == K_ESCAPE):

                    self.quit()
                    return

                elif (event.type == QUIT):
                    self.quit()
                    return
            self.draw_text("Joystick Name:  %s (%s)" % (self.joystick_names[0], supported), 5, 5, joysticknamecolor)

            ############################ AXES ############################

            self.draw_text("Axes (%d)" % self.my_joystick.get_numaxes(), 5, 15, WHITE)

            for i in range(self.my_joystick.get_numaxes()):
                # Get current corrected axis value
                axesval[i] = Correction[i](self.my_joystick.get_axis(i))

                def rad(val):
                    return val * (pi / 180.0)
                def delta(a,b):
                    if a > b:
                        return a-b
                    else:
                        return b-a

                if AxesConf:
                    axescolor = DARKGREEN
                    if not hold and (delta(oldaxesval[i], axesval[i]) > 0.001):
                        if AxesConf[i] == THRUST:
                            newthrust = True
                            # YUK. Quick prototype hacking.
                            if reverse:
                                thrust = - axesval[i]
                            else:
                                thrust = axesval[i]
                        if AxesConf[i] == YAW:
                            newrudder = True
                            rudder = axesval[i]
                        oldaxesval[i] = axesval[i]
                        axescolor = BLUE
                    elif hold:
                        axescolor = DARKGRAY
                else:
                    axescolor = RED

                centerX, centerY = (30 + (i * 45)), 50
                pygame.draw.circle(self.screen, axescolor, (centerX, centerY), 20, 0)
                lineX = centerX + cos((axesval[i] * pi) - pi / 2) * 20
                lineY = centerY + sin((axesval[i] * pi) - pi / 2) * 20
                pygame.draw.line(self.screen, WHITE, (centerX, centerY), (lineX, lineY))

                arcdeg = ((axesval[i]+1)/2) * 360

                begin  = pi/2
                end    = rad((-arcdeg) % 360) - pi/2
                #pygame.draw.arc(self.screen, WHITE, (centerX-20, centerY-20, 40, 40), begin, end, 3)
                self.center_text(("%f" % axesval[i])[:5], 30 + (i * 45), 50, WHITE)

            ############################ BUTTONS ############################

            self.draw_text("Buttons (%d)" % self.my_joystick.get_numbuttons(),
                           5, 75, WHITE)

            for i in range(self.my_joystick.get_numbuttons()):
                buttoncolor = DARKGRAY
                if ButtonConf:
                    buttoncolor = RED
                    if self.my_joystick.get_button(i):
                        if ButtonConf[i] == FULLSTOP:
                            toggled[i] = 0
                            newthrust = True
                            thrust = 0
                        # TODO: I'd love to have "Press and hold long for shift functionality"
                        buttoncolor = GREEN
                        toggled[i] += 1
                        if (toggled[i] > 25): # TODO: This should be calculated into a time and measured well.
                            switched[i] = not switched[i]
                            toggled[i] = 0

                            if ButtonConf[i] == HOLD:
                               hold = not hold
                            if ButtonConf[i] == REVERSE:
                               reverse = not reverse
                    if switched[i] == 1:
                       buttoncolor = BLUE

                pygame.draw.circle(self.screen, buttoncolor, (20 + (i * 30), 100), 10, 0)

                self.center_text("%d" % i, 20 + (i * 30), 100, WHITE)

            ############################ Coolie Hat ############################

            self.draw_text("POV Hats (%d)" % self.my_joystick.get_numhats(),
                           5, 125, (255, 255, 255))

            for i in range(0, self.my_joystick.get_numhats()):
                if (self.my_joystick.get_hat(i) != (0, 0)):
                    pygame.draw.circle(self.screen, BLUE,
                                       (20 + (i * 30), 150), 10, 0)
                else:
                    pygame.draw.circle(self.screen, RED,
                                       (20 + (i * 30), 150), 10, 0)

                self.center_text("%d" % i, 20 + (i * 30), 100, WHITE)
            if not hold:
               if newthrust:
                  self.TransmitThrust(thrust)
                  newthrust = False
               if newrudder:
                  self.TransmitRudder(rudder)
                  newrudder= False
            pygame.display.flip()

    def quit(self):
        pygame.display.quit()

def ParseOpts():
    opts = []
    ip = "127.0.0.1"
    port = 55555
    
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:i:v", ["help","port", "ip", "verbose"])
    except getopt.error as msg:
        fail = True
    
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print(__readme__)
            sys.exit(0)
        if o in ("-i", "--ip"):
            ip = a
        if o in ("-p", "--port"):
            port = int(a)

    return ip, port


def Start():
    ip, port = ParseOpts()
    app = App(ip,port)
    app.main()

if __name__ == "__main__":
    Start()
