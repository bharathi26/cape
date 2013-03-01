#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from RAIN.System.Registry import ComponentTemplates
from RAIN.System.RPCComponent import RPCComponent

import cherrypy
from cherrypy import Tool
import jsonpickle
import os

class WebGateway(RPCComponent):
    class WebClient(object):
        def __init__(self, gateway=None, loader=None):
            self.gateway = gateway
            self.loader = loader

        @cherrypy.expose
        def index(self):
            self.gateway.loginfo(str(cherrypy.request.__dict__))
            if self.loader:
                return self.loader

        @cherrypy.expose
        def submit(self, name):
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return jsonpickle.encode(dict(title="Hello, %s" %name))

    def __init__(self):
        self.MR= {'rpc_startEngine': {},
                  'rpc_stopEngine': {}
                 }
        super(WebGateway, self).__init__()

        self.Configuration['port'] = 8055
        self.Configuration['staticdir'] = os.path.join(os.path.abspath("."), "static")
        self.loader = None

    def main_prepare(self):
        self.start_Engine()

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

ComponentTemplates["WebGateway"] = [WebGateway, "AJAX-capable Gateway component"]
