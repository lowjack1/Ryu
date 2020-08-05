import asyncio

from os import getenv, makedirs, mkdir, remove
from os.path import dirname, exists, join, splitext
from dotenv import load_dotenv
import logging

import aiohttp
import asyncpg

from tornado.web import escape, HTTPError
from tornado.ioloop import IOLoop
import tornado.options

from Ryu.handlers import common

################################################################################################################################

logging.basicConfig(
    format='[%(asctime)s] p%(thread)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%d %b %y %H:%M:%S',
    level=logging.DEBUG
)

tornado.options.define("port", default=8080, help="run on the given port", type=int)
tornado.options.define("env", default="dev", help="default runtime environment")
tornado.options.define("debug", default=False, help="Debug mode", type=bool)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

PG_CONFIG = {
    'user': getenv('DB_USER'),
    'pass': getenv('DB_PASS'),
    'host': getenv('DB_HOST'),
    'database': getenv('DB_NAME'),
    'port': getenv('DB_PORT')
}
PG_CONFIG['dsn'] = "postgres://%s:%s@%s:%s/%s" % (PG_CONFIG['user'], PG_CONFIG['pass'], PG_CONFIG['host'], PG_CONFIG['port'], PG_CONFIG['database'])


async def get_config():
    isDebug = tornado.options.options.debug
    app_path = "build" if isDebug else "dist"

    app_location = dirname(__file__)
    template_path = join(app_location, 'client', app_path, 'templates')
    static_path = join(app_location, 'client', app_path, 'static')

    return {
        'template_path': template_path,
        'static_path': static_path,
        'pool': await asyncpg.create_pool(PG_CONFIG['dsn']),
        'debug': tornado.options.options.debug,
        'cookie_secret': getenv('COOKIE_SECRET'),
        'default_handler_class': common.Default404Handler
    }

################################################################################################################################


