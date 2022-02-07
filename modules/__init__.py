# -*- coding: utf-8 -*-

###########       iEdon PeerAPI Agent      ###########
##                  Author: iEdon                   ##
##                Version : 1.0.0                   ##
######################################################

import logging, logging.handlers
from config import VAR_LOG_LEVEL, VAR_LOG_FORMAT, VAR_LOG_DATE_FORMAT, VAR_LOG_PATH, VAR_LOG_SIZE, VAR_LOG_BACKUPS
#logging.basicConfig(level=VAR_LOG_LEVEL, format=VAR_LOG_FORMAT, datefmt=VAR_LOG_DATE_FORMAT, handlers=[ logging.StreamHandler() ])
logging.basicConfig(level=VAR_LOG_LEVEL, format=VAR_LOG_FORMAT, datefmt=VAR_LOG_DATE_FORMAT, handlers=[ logging.handlers.RotatingFileHandler(filename=VAR_LOG_PATH, maxBytes=VAR_LOG_SIZE, backupCount=VAR_LOG_BACKUPS,encoding="utf-8") ])


from aiohttp import web
app = web.Application()
router = web.RouteTableDef()

from . import routes
routes.initRoutes()


async def on_startup(app):
    pass


async def on_shutdown(app):
    pass


app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.add_routes(router)
