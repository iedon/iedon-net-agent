# -*- coding: utf-8 -*-

###########       iEdon PeerAPI Agent      ###########
##                  Author: iEdon                   ##
##                Version : 1.0.0                   ##
######################################################


import aiofiles
from aiofiles import os
from config import VAR_BIRD_PEER_CONF_DIR, VAR_BIRD_PEER_TEMPLATE_FILE, VAR_ENDPOINT, VAR_IPV4, VAR_IPV6, VAR_IPV6_LINK_LOCAL, VAR_WIREGUARD_CONF_DIR, VAR_WIREGUARD_PUBLIC_KEY, VAR_WIREGUARD_TEMPLATE_FILE
from . import logging
from .functions import exec_shell, find_free_port, jwt_decode, jwt_encode


async def query(payload):
    # action: 'query',
    # asn: String(session.asn),
    # interface: session.interface,
    # data: session.data || ''

    ret1, ifconfig, stderr1 = await exec_shell(f'ifconfig {payload["interface"]}')
    ret2, bird, stderr2 = await exec_shell(f'birdc show pro {payload["interface"]}')
    if ret2 != 0 or bird.find('syntax error') != -1:
        ret21, bird1, stderr21 = await exec_shell(f'birdc show pro {payload["interface"]}_4')
        ret22, bird2, stderr22 = await exec_shell(f'birdc show pro {payload["interface"]}_6')
        bird = (bird1 if bird1.find('syntax error') == -1 else '') + '\n' + (bird2 if bird2.find('syntax error') == -1 else '')
        ret2 = ret21 == 0 and ret22 == 0
        ret2 = 0 if ret2 else -1
    ret3, wg, stderr3 = await exec_shell(f'wg show {payload["interface"]}')

    result = f'{bird}\n' if ret2 == 0 else ''
    result += f'{wg}\n' if ret3 == 0 else ''
    result += ifconfig if ret1 == 0 else ''
    return f'```\n{result}```'


# action: 'enable',
# session: {
#   asn: result.dataValues.asn,
#   status: result.dataValues.status,
#   ipv4: result.dataValues.ipv4,
#   ipv6: result.dataValues.ipv6,
#   ipv6LinkLocal: result.dataValues.ipv6_link_local,
#   type: result.dataValues.type,
#   extensions: result.dataValues.extensions ? JSON.parse(result.dataValues.extensions) : [],
#   interface: result.dataValues.interface,
#   endpoint: result.dataValues.endpoint,
#   credential: result.dataValues.credential,
#   data: result.dataValues.data ? JSON.parse(result.dataValues.data) : ''
# }
async def enable(payload):
    ret1, stdout1, stderr1 = await exec_shell(f'birdc enable {payload["session"]["interface"]}')
    ret11, stdout11, stderr11 = await exec_shell(f'birdc enable {payload["session"]["interface"]}_4')
    ret12, stdout12, stderr12 = await exec_shell(f'birdc enable {payload["session"]["interface"]}_6')
    ret1 = ret1 == 0 or (ret11 == 0 and ret12 == 0)
    ret1 = 0 if ret1 else -1
    stderr1 = f'{stderr1}\n{stderr11}\n{stderr12}'
    stderr2 = ''
    stderr3 = ''
    ret2 = -1
    ret3 = -1
    if ret1 == 0:
        ret2, stdout2, stderr2 = await exec_shell(f'systemctl enable wg-quick@\'{payload["session"]["interface"]}\'')
        if ret2 == 0:
            ret3, stdout3, stderr3 = await exec_shell(f'systemctl start wg-quick@\'{payload["session"]["interface"]}\'')

    # Fallback
    if ret1 != 0 or ret2 != 0 or ret3 != 0:
        await exec_shell(f'systemctl stop wg-quick@\'{payload["session"]["interface"]}\'')
        await exec_shell(f'systemctl disable wg-quick@\'{payload["session"]["interface"]}\'')
        await exec_shell(f'birdc disable {payload["session"]["interface"]}')
        await exec_shell(f'birdc disable {payload["session"]["interface"]}_4')
        await exec_shell(f'birdc disable {payload["session"]["interface"]}_6')

    return ret1 == 0 and ret2 == 0 and ret3 == 0, f'{stderr1}\n====={stderr2}\n====={stderr3}'


async def disable(payload):
    ret1, stdout1, stderr1 = await exec_shell(f'birdc disable {payload["session"]["interface"]}')
    ret11, stdout11, stderr11 = await exec_shell(f'birdc disable {payload["session"]["interface"]}_4')
    ret12, stdout12, stderr12 = await exec_shell(f'birdc disable {payload["session"]["interface"]}_6')
    ret1 = ret1 == 0 or (ret11 == 0 and ret12 == 0)
    ret1 = 0 if ret1 else -1
    stderr1 = f'{stderr1}\n{stderr11}\n{stderr12}'
    stderr2 = ''
    stderr3 = ''
    ret2 = -1
    ret3 = -1
    if ret1 == 0:
        ret2, stdout2, stderr2 = await exec_shell(f'systemctl stop wg-quick@\'{payload["session"]["interface"]}\'')
        if ret2 == 0:
            ret3, stdout3, stderr3 = await exec_shell(f'systemctl disable wg-quick@\'{payload["session"]["interface"]}\'')
    # Fallback
    if ret1 != 0 or ret2 != 0 or ret3 != 0:
        await exec_shell(f'systemctl enable wg-quick@\'{payload["session"]["interface"]}\'')
        await exec_shell(f'systemctl start wg-quick@\'{payload["session"]["interface"]}\'')
        await exec_shell(f'birdc enable {payload["session"]["interface"]}')
        await exec_shell(f'birdc enable {payload["session"]["interface"]}_4')
        await exec_shell(f'birdc enable {payload["session"]["interface"]}_6')

    return ret1 == 0 and ret2 == 0 and ret3 == 0, f'{stderr1}\n====={stderr2}\n====={stderr3}'


async def info(payload):
    # action: 'info',
    # asn: ctx.state.asn,
    # data
    data = {
        'asn': payload["asn"],
        'port': find_free_port()
    }
    return {
        'passthrough': jwt_encode(data),
        'info': f'**Endpoint**: ```{VAR_ENDPOINT}:{data["port"]}```\n\n**WireGuard** Public Key: ```{VAR_WIREGUARD_PUBLIC_KEY}```'
    }



async def approve(payload):
    payload["asn"] = payload["session"]["asn"]
    payload["ipv4"] = payload["session"]["ipv4"]
    payload["ipv6"] = payload["session"]["ipv6"]
    payload["ipv6LinkLocal"] = payload["session"]["ipv6LinkLocal"]
    payload["type"] = payload["session"]["type"]
    payload["extensions"] = payload["session"]["extensions"]
    payload["interface"] = payload["session"]["interface"]
    payload["endpoint"] = payload["session"]["endpoint"]
    payload["credential"] = payload["session"]["credential"]
    payload["data"] = payload["session"]["data"]
    return await add(payload)


async def add(payload):
    asn = payload["asn"]
    peerIpv4 = payload["ipv4"]
    peerIpv6 = payload["ipv6"]
    peerIpv6LinkLocal = payload["ipv6LinkLocal"]
    type = payload["type"]
    extensions = payload["extensions"]
    interface = payload["interface"]
    peerEndpoint = payload["endpoint"]
    peerCredential = payload["credential"]
    data = payload["data"]
    port = jwt_decode(data["passthrough"])["port"]

    if type != 'wireguard' or peerCredential == None:
        return False

    mp_bgp = True if 'mp-bgp' in extensions else False
    extended_nexthop = True if 'extended-nexthop' in extensions else False

    async with aiofiles.open(VAR_BIRD_PEER_TEMPLATE_FILE, mode='r') as f:
        birdConf = await f.read()

    async with aiofiles.open(VAR_WIREGUARD_TEMPLATE_FILE, mode='r') as f:
        wgConf = await f.read()

    wgConf = wgConf.replace('<%__IPV4__%>', VAR_IPV4)
    wgConf = wgConf.replace('<%__PEER_PUBLIC_KEY__%>', peerCredential)
    wgConf = wgConf.replace('<%__PEER_ENDPOINT__%>', f'Endpoint = {peerEndpoint}' if peerEndpoint != None else '')
    wgConf = wgConf.replace('<%__PORT__%>', str(port))
    wgPostUp = ''
    if peerIpv4 != None:
        wgPostUp = f'ip addr del dev {interface} {VAR_IPV4}/32 && ip addr add dev {interface} {VAR_IPV4}/32 peer {peerIpv4}/32'
    if peerIpv6LinkLocal != None:
        wgConf = wgConf.replace('<%__IPV6__%>', VAR_IPV6_LINK_LOCAL)
        if peerIpv4 != None:
            wgPostUp += ' && '
        wgPostUp += f'ip addr del dev {interface} {VAR_IPV6_LINK_LOCAL}/128 && ip addr add dev {interface} {VAR_IPV6_LINK_LOCAL}/128 peer {peerIpv6LinkLocal}/128'
    elif peerIpv6 != None:
        wgConf = wgConf.replace('<%__IPV6__%>', VAR_IPV6)
        if peerIpv4 != None:
            wgPostUp += ' && '
        wgPostUp += f'ip addr del dev {interface} {VAR_IPV6}/128 && ip addr add dev {interface} {VAR_IPV6}/128 peer {peerIpv6}/128'
    wgConf = wgConf.replace('<%__POSTUP__%>', wgPostUp)
    wgConf = wgConf.replace('<%__IPV6__%>', VAR_IPV6) # Default ipv6

    birdChannelIpv4 = '\tipv4 {\n\t\timport where import_filter_ebgp(1, 24, 33);\n\t\texport where export_filter_ebgp(1, 24, 33);\n\t\timport limit 3000 action block;\n\t\t'
    birdChannelIpv6 = '\tipv6 {\n\t\timport where import_filter_ebgp(1, 24, 33);\n\t\texport where export_filter_ebgp(1, 24, 33);\n\t\timport limit 3000 action block;\n\t\t'
    if extended_nexthop:
        birdChannelIpv4 += 'extended next hop on;\n\t};\n'
        birdChannelIpv6 += 'extended next hop on;\n\t};\n'
    else:
        birdChannelIpv4 += '\n\t};\n'
        birdChannelIpv6 += '\n\t};\n'

    if mp_bgp:
        birdConf = birdConf.replace('<%__INTERFACE__%>', interface)
        birdNeighbor = '\tneighbor '
        if peerIpv6LinkLocal != None:
            birdNeighbor += f'{peerIpv6LinkLocal}%\'{interface}\''
        elif peerIpv6 != None:
            birdNeighbor += f'{peerIpv6}'
        elif peerIpv4 != None:
            birdNeighbor += f'{peerIpv4}'
        birdNeighbor += f' as {asn};'
        birdConf = birdConf.replace('<%__NEIGHBOUR__%>', birdNeighbor)
        birdConf = birdConf.replace('<%__CHANNEL__%>', birdChannelIpv4 + birdChannelIpv6)
    else:
        birdConf_4 = birdConf
        birdConf_6 = birdConf
        birdConf = ''
        if peerIpv6 != None or peerIpv6LinkLocal != None:
            birdNeighbor = '\tneighbor '
            if peerIpv6LinkLocal != None:
                birdNeighbor += f'{peerIpv6LinkLocal}%\'{interface}\''
            elif peerIpv6 != None:
                birdNeighbor += f'{peerIpv6}'
            birdNeighbor += f' as {asn};'
            birdConf_6 = birdConf_6.replace('<%__NEIGHBOUR__%>', birdNeighbor)
            birdConf_6 = birdConf_6.replace('<%__INTERFACE__%>', f'{interface}_6')
            birdConf_6 = birdConf_6.replace('<%__CHANNEL__%>', birdChannelIpv6)
            birdConf = birdConf_6
        if peerIpv4 != None:
            birdNeighbor = f'\tneighbor {peerIpv4} as {asn};'
            birdConf_4 = birdConf_4.replace('<%__NEIGHBOUR__%>', birdNeighbor)
            birdConf_4 = birdConf_4.replace('<%__INTERFACE__%>', f'{interface}_4')
            birdConf_4 = birdConf_4.replace('<%__CHANNEL__%>', birdChannelIpv4)
            birdConf += '\n' + birdConf_4

    async with aiofiles.open(f'{VAR_BIRD_PEER_CONF_DIR}{interface}.conf', mode='w+') as f:
        await f.write(birdConf)

    async with aiofiles.open(f'{VAR_WIREGUARD_CONF_DIR}{interface}.conf', mode='w+') as f:
        await f.write(wgConf)

    ret1, stdout1, stderr1 = await exec_shell('birdc conf')
    if ret1 == 0:
        ret2, stdout2, stderr2 = await exec_shell(f'systemctl enable wg-quick@\'{interface}\'')
        if ret2 == 0:
            ret3, stdout3, stderr3 = await exec_shell(f'systemctl start wg-quick@\'{interface}\'')

    # Fallback
    if ret1 != 0 or ret2 != 0 or ret3 != 0:
        try:
            await exec_shell(f'systemctl stop wg-quick@\'{interface}\'')
            await exec_shell(f'systemctl disable wg-quick@\'{interface}\'')
            await os.remove(f'{VAR_BIRD_PEER_CONF_DIR}{interface}.conf')
            await os.remove(f'{VAR_WIREGUARD_CONF_DIR}{interface}.conf')
            await exec_shell('birdc conf')
        except Exception as ex:
            logging.error(ex)
            pass
        return False

    return True


async def delete(payload):
    result = False
    try:
        await os.remove(f'{VAR_BIRD_PEER_CONF_DIR}/{payload["session"]["interface"]}.conf')
        await exec_shell(f'systemctl stop wg-quick@\'{payload["session"]["interface"]}\'')
        await exec_shell(f'systemctl disable wg-quick@\'{payload["session"]["interface"]}\'')
        await os.remove(f'{VAR_WIREGUARD_CONF_DIR}/{payload["session"]["interface"]}.conf')
        await exec_shell('birdc conf')
        result = True
    except FileNotFoundError:
        result = True
        pass
    except Exception as ex:
        logging.error(ex)
    return result
