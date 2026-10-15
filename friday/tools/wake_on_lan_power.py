"""
ULTRON Wake-on-LAN & Remote Machine Power Management Module
Enables waking sleeping or powered-off machines across local subnet via Magic Packets,
along with reachability verification and subnet scanning.
"""

import socket
import struct
import asyncio
import os
import platform
import subprocess
from typing import Optional, Dict, List

async def send_wake_on_lan(mac_address: str, broadcast_ip: str = "255.255.255.255", port: int = 9) -> str:
    """
    Sends a Wake-on-LAN (WoL) Magic Packet to wake up a sleeping or powered-off PC on the local network.
    MAC address can be formatted as XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, or XXXXXXXXXXXX.
    """
    try:
        clean_mac = mac_address.replace(":", "").replace("-", "").replace(".", "").strip()
        if len(clean_mac) != 12:
            return f"[ERROR] Invalid MAC address format: '{mac_address}'. Must contain 12 hex characters."

        # Construct 102-byte Magic Packet: 6 bytes of 0xFF followed by 16 repetitions of the target MAC
        mac_bytes = bytes.fromhex(clean_mac)
        magic_packet = b"\xff" * 6 + mac_bytes * 16

        # Send via UDP broadcast
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (broadcast_ip, port))
        sock.close()

        return f"[OK] Wake-on-LAN Magic Packet successfully broadcasted to {mac_address} via {broadcast_ip}:{port}."
    except Exception as e:
        return f"[ERROR] Failed to send Wake-on-LAN packet: {e}"


async def ping_device_status(ip_address: str, timeout_seconds: int = 2) -> str:
    """
    Pings a network device or machine IP to check if it is online and responsive.
    """
    try:
        ip = ip_address.strip()
        param = "-n" if platform.system().lower() == "windows" else "-c"
        timeout_flag = "-w" if platform.system().lower() == "windows" else "-W"
        timeout_val = str(timeout_seconds * 1000 if platform.system().lower() == "windows" else timeout_seconds)

        cmd = ["ping", param, "1", timeout_flag, timeout_val, ip]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        out_str = stdout.decode("cp1252", errors="ignore")

        if "TTL=" in out_str or "bytes from" in out_str.lower():
            return f"[ONLINE] Device at {ip} is reachable and responding to ping."
        return f"[OFFLINE] Device at {ip} did not respond to ping."
    except Exception as e:
        return f"[ERROR] Ping check failed: {e}"


async def scan_local_active_devices() -> str:
    """
    Scans the local ARP table to find all currently discovered IP and MAC addresses on the local network.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            "arp", "-a",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        out_str = stdout.decode("cp1252", errors="ignore")

        devices = []
        for line in out_str.splitlines():
            line = line.strip()
            if "dynamic" in line.lower() or "static" in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    mac = parts[1]
                    devices.append(f"- IP: {ip.ljust(16)} | MAC: {mac.ljust(18)} | Type: {parts[2] if len(parts) > 2 else 'N/A'}")

        if not devices:
            return "[ARP] No active network neighbor devices found in current ARP cache."

        return f"[NETWORK DEVICES] Found {len(devices)} active local device(s):\n" + "\n".join(devices)
    except Exception as e:
        return f"[ERROR] ARP scan failed: {e}"
