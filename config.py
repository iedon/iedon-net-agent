# -*- coding: utf-8 -*-

###########       iEdon PeerAPI Agent      ###########
##                  Author: iEdon                   ##
##                Version : 1.0.0                   ##
######################################################

import logging

# Log Level
VAR_LOG_LEVEL = logging.INFO

# Log Format
VAR_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Log Date Format
VAR_LOG_DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

# Log Path
VAR_LOG_PATH = './logs/peerapi-agent.log'

# Log Max Size
VAR_LOG_SIZE = 1024*1024*32

# Log backups to hold
VAR_LOG_BACKUPS = 5

# Port to listen
VAR_PORT = 3000

# JWT Secret
VAR_JWT_SECRET = '________________'

# NODE_ENDPOINT
VAR_ENDPOINT = '_______________________'

# NODE_IP
VAR_IPV4 = '172.x.x.x'
VAR_IPV6 = 'fdxx::xxx'
VAR_IPV6_LINK_LOCAL = 'fe80::xxxx'

# WireGuard Public Key
VAR_WIREGUARD_PUBLIC_KEY = '___________________'

# Template file for bird
VAR_BIRD_PEER_TEMPLATE_FILE = './templates/bird.conf'

# Template file for wireguard
VAR_WIREGUARD_TEMPLATE_FILE = './templates/wireguard.conf'

# Path to place bird configuration file(ends with '/')
VAR_BIRD_PEER_CONF_DIR = '/etc/bird/peers/'

# Path to place WireGuard configuration file(ends with '/')
VAR_WIREGUARD_CONF_DIR = '/etc/wireguard/'
