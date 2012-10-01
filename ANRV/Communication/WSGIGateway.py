#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#from flup.server.fcgi import WSGIServer
import bottle

from ANRV.System.Registry import ComponentTemplates
from ANRV.System.RPCComponent import RPCComponentThreaded
from ANRV.System.LoggableComponent import LoggableComponent

import Axon

class WSGIGateway(RPCComponentThreaded):
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

        # The following, it doesn't work. :(
        self.app.route('/pseudowsgi/<path>', self.pseudowsgi)

    def pseudowsgi(self, **kwargs):
        self.logdebug(bottle.request.url)
        self.logdebug(bottle.response)
        for cookie in bottle.request.cookies:
            self.logdebug(cookie)
        return "FOOBAR %s" % kwargs

    def main(self):
        self.loginfo("Starting bottle server.")
        bottle.run(app=self.app, host="localhost", port=8080, debug=False)


ComponentTemplates["WSGIGateway"] = [WSGIGateway, "WSGI Gateway component"]
