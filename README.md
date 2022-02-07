# IEDON-NET-AGENT

This is daemon script of DN42 Peering System for IEDON-NET. Currently only designed for WireGuard.

## Install

```bash
apt update
apt install python3 python3-pip
pip3 install -r requirements.txt
cp ./peerapi-agent.service /usr/lib/systemd/system/
```

## Run in service

```bash
systemctl enable peerapi-agent    # Auto start after reboot
systemctl start peerapi-agent
```

## Run in console

```bash
python3 peerapi-agent.py
```
