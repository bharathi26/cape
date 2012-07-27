#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from flup.server.fcgi import WSGIServer
import bottle

from ANRV.System.Registry import ComponentTemplates
#from ANRV.System.RPCComponent import RPCComponent
from ANRV.System.LoggableComponent import LoggableComponent

import Axon

class WSGIGateway(Axon.ThreadedComponent.threadedcomponent, LoggableComponent):
    def __init__(self):
        super(WSGIGateway, self).__init__()
        self.app = bottle.Bottle()
        self._setRoutes()

    def _setRoutes(self):
        self.loginfo("Setting up routes.")

        # Create a route by hand
        pseudoroute = bottle.Route(self.app, "/pseudowsgi/<path>", "GET", self.pseudowsgi)

        # Add route
        self.app.router.add("/pseudowsgi/<path>", "GET", pseudoroute)

        # Calling this results in a 500 internal error
        self.app.router.add("/hello", "GET", self.hello)

        # The following, it doesn't work. :(
        self.app.route('/hello/<url>', self.hello)
        self.app.route('/pseudowsgi/<path>', self.pseudowsgi)

    def hello(self, url):
        return "World tried to call my '%s'." % url

    def pseudowsgi(self, **kwargs):
        print(bottle.request.url)
        print(bottle.response)
        for cookie in bottle.request.cookies:
            print(cookie)
        return "FOOBAR %s" % kwargs

    def main(self):
        self.logdebug("Starting bottle server.")
        bottle.run(app=self.app, host="localhost", port=8080, debug=False)


ComponentTemplates["WSGIGateway"] = [WSGIGateway, "WSGI Gateway component"]
