# -*- coding: utf-8 -*-

import json
import logging
from aiohttp import web

from . import router
from modules.bird import delete, disable, enable, info, query, add, approve


def initRoutes():
    pass


@router.post('/')
async def entry(request):
    response = {
        'success': False,
        'data': ''
    }

    try:
        payload = json.loads(await request.read())
        if payload.__contains__('action') == True:
            if payload['action'] == 'query':
                response['data'] = await query(payload)
                response['success'] = True

            elif payload['action'] == 'info':
                response['data'] = await info(payload)
                response['success'] = True

            elif payload['action'] == 'delete':
                response['success'] = await delete(payload)

            elif payload['action'] == 'add':
                response['success'] = await add(payload)

            elif payload['action'] == 'approve':
                response['success'] = await approve(payload)

            elif payload['action'] == 'enable':
                result, output = await enable(payload)
                response['success'] = result
                if result:
                    response['data'] = output

            elif payload['action'] == 'disable':
                result, output = await disable(payload)
                response['success'] = result
                if result:
                    response['data'] = output

    except Exception as ex:
        logging.exception(ex)

    return web.json_response(response)
