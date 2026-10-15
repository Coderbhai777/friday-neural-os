"""
ULTRON LAN & IoT Network Discovery Engine
Maps connected local network devices, scans open IoT/embedded services, sends Wake-on-LAN packets, and diagnoses LAN bandwidth.
"""

import os
import sys
import socket
import struct
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


def _get_default_gateway_and_ip():
    """Returns local IP and default gateway."""
    local_ip = "127.0.0.1"
    gateway_ip = "192.168.1.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    try:
        # Check routing table via route print / netsh
        res = subprocess.run(["route", "print", "0.0.0.0"], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                gateway_ip = parts[2]
                break
    except Exception:
        pass

    return local_ip, gateway_ip


async def lan_get_local_ip_and_gateway() -> str:
    """
    Returns active network interface details, local IP address, subnet range, and default gateway.
    """
    def _run():
        lip, gw = _get_default_gateway_and_ip()
        hostname = socket.gethostname()
        return (
            f"🌐 **LOCAL NETWORK INTERFACE CONFIGURATION:**\n"
            f"• **Machine Hostname:** `{hostname}`\n"
            f"• **Local IPv4 Address:** `{lip}`\n"
            f"• **Default Gateway (Router):** `{gw}`\n"
            f"• **Subnet Network Scope:** `{'.'.join(lip.split('.')[:3])}.0/24`"
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run)


async def lan_scan_active_devices() -> str:
    """
    Scans the local LAN subnet via ARP table resolution to identify connected laptops, phones, IoT hubs, and smart devices.
    """
    def _scan():
        lip, gw = _get_default_gateway_and_ip()
        subnet_prefix = ".".join(lip.split(".")[:3])
        
        # 1. Read Windows ARP Cache
        devices = []
        try:
            res = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line or "Interface" in line or "Internet Address" in line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1].replace("-", ":").upper()
                    dev_type = parts[2]
                    
                    if ip.startswith(subnet_prefix) and dev_type.lower() == "dynamic":
                        # Try reverse DNS
                        name = ""
                        try:
                            name = socket.gethostbyaddr(ip)[0]
                        except Exception:
                            name = "Unknown Device" if ip != gw else "Default Router / Gateway"
                        
                        devices.append({
                            "ip": ip,
                            "mac": mac,
                            "name": name,
                            "is_gw": (ip == gw)
                        })
        except Exception as e:
            return f"[ERROR] ARP scan failed: {e}"

        if not devices:
            return f"No active dynamic devices found in ARP cache for subnet `{subnet_prefix}.0/24`."

        # Sort by IP
        def _ip_sort(d):
            try:
                return [int(x) for x in d["ip"].split(".")]
            except Exception:
                return [0,0,0,0]

        devices.sort(key=_ip_sort)

        lines = [f"📡 **LOCAL NETWORK (LAN) ACTIVE DEVICES ({len(devices)} Detected):**"]
        for idx, d in enumerate(devices, 1):
            tag = " 🌟 [ROUTER/GATEWAY]" if d["is_gw"] else ""
            lines.append(f"  {idx}. **{d['ip']}** | MAC: `{d['mac']}` | Host: *{d['name']}*{tag}")

        return "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scan)


async def lan_wake_on_lan(mac_address: str, broadcast_ip: str = "255.255.255.255", port: int = 9) -> str:
    """
    Broadcasts a Wake-on-LAN (WOL) Magic Packet to power on a sleeping PC, server, or NAS on the network.
    
    Args:
        mac_address: Target machine MAC address (e.g. 'AA:BB:CC:DD:EE:FF' or 'AA-BB-CC-DD-EE-FF').
        broadcast_ip: Network broadcast address (default: '255.255.255.255').
        port: UDP port (default: 9).
    """
    def _send_wol():
        clean_mac = mac_address.replace(":", "").replace("-", "").replace(".", "").strip()
        if len(clean_mac) != 12:
            return f"Invalid MAC address format: '{mac_address}'. Must be 12 hex characters."

        # Magic packet format: 6x 0xFF followed by MAC repeated 16 times
        mac_bytes = bytes.fromhex(clean_mac)
        magic_packet = b"\xff" * 6 + mac_bytes * 16

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(magic_packet, (broadcast_ip, port))

        return f"⚡ [WOL TRANSMITTED] Magic packet broadcasted to `{mac_address}` on `{broadcast_ip}:{port}`. Target device powering on."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_wol)


async def lan_inspect_port_services(ip: str, port_list: str = "22,80,443,445,3389,8080,8000,5000,1883") -> str:
    """
    Scans common services and open ports on a specific LAN device (SSH, HTTP, SMB, RDP, MQTT, Web).
    
    Args:
        ip: Target IPv4 address.
        port_list: Comma-separated list of ports to scan.
    """
    def _scan_ports():
        ports = []
        for p in port_list.split(","):
            try:
                ports.append(int(p.strip()))
            except ValueError:
                continue

        service_names = {
            21: "FTP",
            22: "SSH Secure Shell",
            23: "Telnet",
            53: "DNS",
            80: "HTTP Web Server",
            443: "HTTPS SSL Web Server",
            445: "SMB File Sharing",
            1883: "MQTT IoT Broker",
            3306: "MySQL Database",
            3389: "RDP Remote Desktop",
            5000: "Flask / API Server",
            5432: "PostgreSQL Database",
            8000: "Web Service (Port 8000)",
            8080: "HTTP Alt Web Server",
            9000: "Portainer / FastCGI",
        }

        open_ports = []
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.6)
            res = s.connect_ex((ip, port))
            if res == 0:
                s_name = service_names.get(port, "Custom Service")
                open_ports.append((port, s_name))
            s.close()

        if not open_ports:
            return f"Target `{ip}` is online but has no open ports among [{', '.join(map(str, ports))}]."

        lines = [f"🔍 **PORT AUDIT FOR DEVICE `{ip}` ({len(open_ports)} Open Services):**"]
        for p_num, s_name in open_ports:
            lines.append(f"  • Port **{p_num}**: {s_name} (OPEN/LISTENING)")

        return "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scan_ports)


async def lan_speedtest_internal(target_ip: str = "") -> str:
    """
    Measures internal round-trip packet latency and packet loss to your router or specified IP.
    
    Args:
        target_ip: Target IP address (defaults to default gateway/router if empty).
    """
    def _ping():
        nonlocal target_ip
        if not target_ip:
            _, gw = _get_default_gateway_and_ip()
            target_ip = gw

        try:
            res = subprocess.run(["ping", "-n", "4", target_ip], capture_output=True, text=True, timeout=8)
            lines = []
            for l in res.stdout.splitlines():
                if any(k in l for k in ["Minimum", "Average", "Packets:", "Lost", "Reply from", "Request timed out"]):
                    lines.append(f"  • {l.strip()}")
            
            return f"📶 **LAN LATENCY & HEALTH BENCHMARK (`{target_ip}`):**\n" + "\n".join(lines)
        except Exception as e:
            return f"[ERROR] Ping benchmark failed: {e}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _ping)
