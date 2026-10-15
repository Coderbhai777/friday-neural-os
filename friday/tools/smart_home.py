"""
ULTRON Smart Home, Wake-on-LAN & IoT Controller
Controls local smart devices, Wake-on-LAN packets, ESP32 IoT endpoints, and local network devices.
"""

import os
import socket
import struct
import subprocess
import asyncio
from typing import Optional

from friday_tools.sound_engine import play_sound_async


async def send_wake_on_lan(mac_address: str, broadcast_ip: str = "255.255.255.255", port: int = 9) -> str:
    """
    Sends a Wake-on-LAN magic packet to remotely power on a PC or device on the local network.
    
    Args:
        mac_address: Target MAC address (e.g. 'AA:BB:CC:DD:EE:FF' or 'AA-BB-CC-DD-EE-FF').
        broadcast_ip: Broadcast IP address (default '255.255.255.255').
        port: UDP port (default 9).
    """
    try:
        clean_mac = mac_address.replace(":", "").replace("-", "").replace(".", "").strip()
        if len(clean_mac) != 12:
            return f"[FAIL] Invalid MAC address format: '{mac_address}'. Expected 12 hex characters."
            
        mac_bytes = bytes.fromhex(clean_mac)
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (broadcast_ip, port))
        sock.close()
        
        play_sound_async("chime")
        return f"[OK] Wake-on-LAN Magic Packet dispatched to MAC: {mac_address} via {broadcast_ip}:{port}."
    except Exception as e:
        return f"[FAIL] Wake-on-LAN failed: {e}"


async def ping_network_device(host: str) -> str:
    """
    Pings a network host or smart device IP to verify online/offline status and latency.
    
    Args:
        host: IP address or hostname (e.g. '192.168.1.1', 'esp32-livingroom.local').
    """
    try:
        p = subprocess.run(["ping", "-n", "2", "-w", "1000", host], capture_output=True, text=True)
        if p.returncode == 0:
            return f"[ONLINE] Device '{host}' responded to ping.\n{p.stdout.strip()}"
        else:
            return f"[OFFLINE] Device '{host}' is unreachable on local network."
    except Exception as e:
        return f"[FAIL] Ping error: {e}"
