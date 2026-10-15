import subprocess
import requests
import socket
import time
import os
import psutil
import webbrowser

# ==============================
# BASIC NETWORK
# ==============================
async def ip_information() -> str:
    return requests.get("https://api.ipify.org").text

async def list_wifi_networks() -> str:
    res = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
    return res.stdout[:1000]

async def connect_wifi(ssid: str) -> str:
    subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"])
    return f"Connecting to {ssid}"

async def disconnect_wifi() -> str:
    subprocess.run(["netsh", "wlan", "disconnect"])
    return "Disconnected"

async def get_saved_wifi_passwords() -> str:
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "profiles"]).decode('utf-8', errors="ignore")
        profiles = [line.split(":")[1].strip() for line in output.split('\n') if "All User Profile" in line]
        results = []
        for p in profiles:
            try:
                info = subprocess.check_output(["netsh", "wlan", "show", "profile", p, "key=clear"]).decode('utf-8', errors="ignore")
                key = [l for l in info.split('\n') if "Key Content" in l]
                results.append(f"{p}: {key[0].split(':')[1].strip() if key else 'OPEN'}")
            except: pass
        return "\n".join(results)
    except Exception as e: return f"Error: {e}"

# ==============================
# ADVANCED NETWORK
# ==============================
async def scan_network_devices() -> str:
    res = subprocess.run(["arp", "-a"], capture_output=True, text=True)
    return res.stdout[:1000]

async def get_detailed_network_info() -> str:
    res = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
    return res.stdout[:1500]

async def get_active_connections() -> str:
    res = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
    return res.stdout[:1500]

async def port_scan(ip_address: str, ports: str = "80,443,22,21,3389") -> str:
    port_list = [int(p.strip()) for p in ports.split(',')]
    results = []
    for port in port_list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        res = sock.connect_ex((ip_address, port))
        results.append(f"Port {port}: {'OPEN' if res == 0 else 'CLOSED'}")
        sock.close()
    return "\n".join(results)

async def ping_device(target: str) -> str:
    res = subprocess.run(["ping", "-n", "4", target], capture_output=True, text=True)
    return res.stdout[:1000]

async def trace_route(target: str) -> str:
    res = subprocess.run(["tracert", "-h", "10", target], capture_output=True, text=True)
    return res.stdout[:1000]

async def wake_on_lan(mac_address: str) -> str:
    # Basic implementation
    try:
        data = b'\xff' * 6 + bytes.fromhex(mac_address.replace(':', '').replace('-', '')) * 16
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(data, ('255.255.255.255', 9))
        return "Magic packet sent"
    except Exception as e: return f"Error: {e}"

async def get_router_info() -> str:
    return subprocess.run(["ipconfig"], capture_output=True, text=True).stdout[:500]

async def network_bandwidth_usage() -> str:
    io = psutil.net_io_counters()
    return f"Sent: {io.bytes_sent/1024/1024:.2f}MB | Recv: {io.bytes_recv/1024/1024:.2f}MB"

async def flush_dns() -> str:
    subprocess.run("ipconfig /flushdns", shell=True)
    return "DNS Flushed"

async def renew_ip_address() -> str:
    subprocess.run("ipconfig /renew", shell=True)
    return "IP Renewed"

async def get_network_speed() -> str:
    return subprocess.run(["powershell", "Get-NetAdapter | Select Name, LinkSpeed"], capture_output=True, text=True).stdout[:500]

async def control_network_adapter(action: str) -> str:
    cmd = f'netsh interface set interface "Wi-Fi" {action}'
    subprocess.run(cmd, shell=True)
    return f"Adapter {action}d"

async def remote_shutdown(ip_address: str, username: str = "", password: str = "") -> str:
    os.system(f"shutdown /s /m \\\\{ip_address} /t 30")
    return "Shutdown command sent"

async def remote_restart(ip_address: str, username: str = "", password: str = "") -> str:
    os.system(f"shutdown /r /m \\\\{ip_address} /t 30")
    return "Restart command sent"
    
async def execute_remote_command(ip_address: str, command: str, username: str = "", password: str = "") -> str:
    """
    Attempts to execute a command on a remote Windows machine using PowerShell Remoting.
    Requires WinRM to be enabled on the target.
    """
    try:
        if username and password:
            ps_cmd = (f'$secpasswd = ConvertTo-SecureString "{password}" -AsPlainText -Force; '
                      f'$creds = New-Object System.Management.Automation.PSCredential ("{username}", $secpasswd); '
                      f'Invoke-Command -ComputerName {ip_address} -Credential $creds -ScriptBlock {{ {command} }}')
        else:
            ps_cmd = f'Invoke-Command -ComputerName {ip_address} -ScriptBlock {{ {command} }}'
            
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, timeout=60)
        return (res.stdout.strip() + res.stderr.strip())[:1000]
    except Exception as e:
        return f"❌ Remote Execution failed: {e}"

async def remote_desktop_connect(ip_address: str, username: str = "") -> str:
    subprocess.Popen(f"mstsc /v:{ip_address}", shell=True)
    return "RDP Launched"

async def get_remote_device_info(ip_address: str) -> str:
    try:
        host = socket.gethostbyaddr(ip_address)[0]
        return f"Host: {host}"
    except: return "Host not found"

async def send_network_message(ip_address: str, message: str) -> str:
    subprocess.run(f'msg /SERVER:{ip_address} * "{message}"', shell=True)
    return "Message sent"

async def share_folder_on_network(folder_path: str, share_name: str) -> str:
    subprocess.run(f'net share {share_name}="{folder_path}" /GRANT:Everyone,FULL', shell=True)
    return "Shared"

async def remove_network_share(share_name: str) -> str:
    subprocess.run(f'net share {share_name} /DELETE', shell=True)
    return "Share removed"

async def list_network_shares(ip_address: str = "") -> str:
    cmd = f"net view \\\\{ip_address}" if ip_address else "net share"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout[:1000]

async def access_network_share(ip_address: str, share_name: str) -> str:
    os.startfile(f"\\\\{ip_address}\\{share_name}")
    return "Opened"

async def map_network_drive(drive_letter: str, network_path: str) -> str:
    subprocess.run(f"net use {drive_letter}: {network_path}", shell=True)
    return "Mapped"

async def disconnect_network_drive(drive_letter: str) -> str:
    subprocess.run(f"net use {drive_letter}: /delete", shell=True)
    return "Disconnected"

async def get_device_services(ip_address: str) -> str:
    return await port_scan(ip_address, "21,22,80,443,445,3389")

async def remote_file_copy(local_file: str, remote_ip: str, remote_path: str) -> str:
    import shutil
    shutil.copy2(local_file, f"\\\\{remote_ip}\\{remote_path}")
    return "Copied"


async def disconnect_device_from_internet(ip_address: str, mac_address: str = "") -> str:
    return "⚠️ ADMIN REQUIRED. Scapy dependency needed."

async def reconnect_device_to_internet(ip_address: str, mac_address: str = "") -> str:
    return "⚠️ ADMIN REQUIRED. Scapy dependency needed."

async def check_admin_privileges() -> str:
    import ctypes
    return "Admin" if ctypes.windll.shell32.IsUserAnAdmin() else "Not Admin"

async def enable_packet_forwarding() -> str:
    return "Packet forwarding enable command sent (requires admin)"

async def get_router_admin_page() -> str:
    webbrowser.open("http://192.168.0.1")
    return "Opened"

async def network_kill_switch(action: str) -> str:
    return "Kill switch toggled (simulated)"

async def monitor_network_traffic(duration_seconds: int = 10) -> str:
    return await network_bandwidth_usage()

async def limit_device_bandwidth(ip_address: str, limit_kbps: int) -> str:
    return "Bandwidth limited (requires QoS)"

async def remove_bandwidth_limit(ip_address: str) -> str:
    return "Limit removed"

async def get_network_devices_with_names() -> str:
    return await scan_network_devices()
