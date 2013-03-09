#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from RAIN.System.Registry import ComponentTemplates
from RAIN.System.RPCComponent import RPCComponent
from RAIN.Messages import Message

import cherrypy
from cherrypy import Tool
import jsonpickle
import os

from pprint import pprint

class WebGate(RPCComponent):
    """Cherrypy based Web Gateway Component for user interaction."""

    directory_name = "WebGate"

    class WebClient(object):
        def __init__(self, gateway=None, loader=None):
            self.gateway = gateway
            self.loader = loader

        @cherrypy.expose
        def index(self):
            #pprint(cherrypy.request)
            self.gateway.loginfo("Client connected from '%s:%s." % (cherrypy.request.remote.ip,
                                                                    cherrypy.request.remote.port))

            self.gateway.logdebug(str(cherrypy.request.__dict__))
            if self.loader:
                return self.loader

        @cherrypy.expose
        def submit(self, name):
            self.gateway.loginfo("Submission received!")
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return jsonpickle.encode(dict(title="Hello, %s" %name))

        @cherrypy.expose
        def rpc(self, recipient, func, arg):
            cherrypy.response.headers['Content-Type'] = 'application/json'
            msg = Message(sender=self.gateway.name, recipient=recipient, func=func, arg=arg)
            response = msg.response("Thank you for your request.")
            self.gateway.loginfo(msg)
            return jsonpickle.encode(response)

    def __init__(self):
        self.MR= {'rpc_startEngine': {},
                  'rpc_stopEngine': {}
                 }
        super(WebGate, self).__init__()

        self.Configuration['port'] = 8055
        self.Configuration['staticdir'] = os.path.join(os.path.abspath("."), "static")
        self.Configuration['enabled'] = True
        self.loader = None

    def main_prepare(self):
        if self.Configuration['enabled']:
            self.start_Engine()
        else:
            self.logwarning("WebGate not enabled!")

    def _ev_client_connect(self):
        self.loginfo("Client connected: '%s'" % cherrypy.request)
        self.clients.append(cherrypy.request)

    def start_Engine(self):
        cherrypy.config.update({'server.socket_port': self.Configuration['port'],
                                'server.socket_host': '0.0.0.0'})
        cherrypy.tools.clientconnect = Tool('on_start_resource', self._ev_client_connect)
        config = {'/static':
                  {'tools.staticdir.on': True,
                   'tools.staticdir.dir': self.Configuration['staticdir']}
                 }
        self.logcritical(str(config))
        self.loader = open(os.path.join(self.Configuration['staticdir'], "index.html")).read()
        self.logcritical(self.loader)

        cherrypy.tree.mount(self.WebClient(gateway=self, loader=self.loader), "/", config=config)
        cherrypy.engine.start()
        return True


    def rpc_startEngine(self):
        return self.start_Engine()

    def rpc_stopEngine(self):
        cherrypy.engine.stop()

ComponentTemplates["WebGate"] = [WebGate, "AJAX-capable Gate component"]
