# -*- coding: utf-8 -*-

###########       iEdon PeerAPI Agent      ###########
##                  Author: iEdon                   ##
##                Version : 1.0.0                   ##
######################################################

import asyncio, socket, jwt
from contextlib import closing
from . import logging
from config import VAR_JWT_SECRET


async def exec_process(*args):
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logging.error(f"Error executing command '{ args[0] }', process failed with code { process.returncode }, stderr: { stderr.decode().strip() }")

    return process.returncode, stdout.decode(), stderr.decode()


async def exec_shell(command):
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logging.error(f"Error executing command '{ command }', process failed with code { process.returncode }, stderr: { stderr.decode().strip() }")

    return process.returncode, stdout.decode(), stderr.decode()


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def jwt_encode(payload):
    return jwt.encode(payload, VAR_JWT_SECRET, algorithm="HS256")


def jwt_decode(encoded):
    return jwt.decode(encoded, VAR_JWT_SECRET, algorithms=["HS256"])
