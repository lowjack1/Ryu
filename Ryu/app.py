import argparse
import os
import traceback

import tornado.ioloop
import tornado.web

import Ryu.handlers as handlers
import Ryu.settings as settings


class Application(tornado.web.Application):
    def __init__(self, config, port):
        routes = [
            (r"/", handlers.common.HomePage),
            (r"/room", handlers.common.UserRoom),
            (r"/websocket", handlers.common.WebSocket),
            (r"/api", handlers.common.APIHandler),
            (r"/invalid_room", handlers.common.InvalidRoom),
        ]
        super(Application, self).__init__(handlers=routes, **config)
        # For the world to exist peacefully, this application should always listen on localhost.
        http_server = self.listen(port, address='127.0.0.1')
        # Set "xheaders" as true. Currently we are using this so that the over-write behaviour on "remote_ip" can be done
        # using the request headers present "X-Real-Ip" / "X-Forwarded-For". This is important as in our architecture Tornado sits behind a proxy server
        http_server.xheaders = True

