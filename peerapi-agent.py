#!/usr/bin/python3
# -*- coding: utf-8 -*-

###########       iEdon PeerAPI Agent      ###########
##                  Author: iEdon                   ##
##                Version : 1.0.0                   ##
######################################################


import asyncio
from aiohttp import web
from config import VAR_PORT
from modules import app


if __name__ == "__main__":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.create_task(web._run_app(app, port=VAR_PORT))
    loop.run_forever()
