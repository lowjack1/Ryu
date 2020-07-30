import argparse
import os
import traceback

import tornado.ioloop
import tornado.web
from tornado.options import options, parse_command_line

from Ryu import app, settings


async def init():
    config = await settings.get_config()
    return config


if __name__ == '__main__':
    parse_command_line()
    app_root = os.path.dirname(__file__)
    options.parse_config_file(os.path.join(app_root, "conf/%s/server.conf" % options.env))

    # Initialize state and static resources
    config = tornado.ioloop.IOLoop.current().run_sync(init)
    # Start application
    application = app.Application(config, options.port)
    # Start eventloop
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        tornado.ioloop.IOLoop.current().stop()
