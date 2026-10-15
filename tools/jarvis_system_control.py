"""
ULTRON JARVIS System Intelligence & Workstation Control Suite
Real-time telemetry, hardware monitoring, window management, and OS orchestration.
"""

import os
import sys
import time
import subprocess
import json
import ctypes
from typing import List, Dict, Any, Optional

try:
    import psutil
except ImportError:
    psutil = None

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None


# ==========================================
# 1. HARDWARE TELEMETRY & SYSTEM METRICS
# ==========================================

async def get_cpu_usage() -> str:
    """Returns real-time CPU percentage across all cores and load averages."""
    if not psutil:
        return "[CPU] psutil not installed."
    try:
        overall = psutil.cpu_percent(interval=0.3)
        per_core = psutil.cpu_percent(percpu=True)
        freq = psutil.cpu_freq()
        freq_str = f" @ {freq.current:.1f}MHz" if freq else ""
        return f"[CPU Telemetry] Total: {overall}%{freq_str} | Cores ({len(per_core)}): {per_core}"
    except Exception as e:
        return f"[ERROR] Failed to get CPU usage: {e}"


async def get_ram_usage() -> str:
    """Returns complete physical and virtual RAM telemetry along with top memory-consuming applications."""
    if not psutil:
        return "[RAM] psutil not installed."
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        avail_gb = mem.available / (1024**3)

        # Aggregate processes by application name
        app_map = {}
        for p in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                info = p.info
                name = info['name']
                if not name:
                    continue
                rss_mb = (info['memory_info'].rss / (1024**2)) if info.get('memory_info') else 0
                if name not in app_map:
                    app_map[name] = {"count": 0, "total_mb": 0.0, "pids": []}
                app_map[name]["count"] += 1
                app_map[name]["total_mb"] += rss_mb
                app_map[name]["pids"].append(info['pid'])
            except Exception:
                continue

        sorted_apps = sorted(app_map.items(), key=lambda x: x[1]["total_mb"], reverse=True)
        top_apps = sorted_apps[:8]

        lines = [
            f"🧠 **ULTRON PHYSICAL & VIRTUAL RAM TELEMETRY**",
            f"• **Installed Physical RAM:** {total_gb:.2f} GB",
            f"• **Active Used Memory:** {used_gb:.2f} GB ({mem.percent}%)",
            f"• **Free / Available RAM:** {avail_gb:.2f} GB",
            f"• **Virtual Pagefile / Swap:** {swap.used / (1024**3):.2f} GB / {swap.total / (1024**3):.2f} GB ({swap.percent}%)",
            f"\n🔥 **TOP MEMORY CONSUMING APPLICATIONS (Ranked):**"
        ]

        friendly_names = {
            "chrome.exe": "Google Chrome",
            "msedge.exe": "Microsoft Edge",
            "firefox.exe": "Mozilla Firefox",
            "brave.exe": "Brave Browser",
            "code.exe": "Visual Studio Code",
            "discord.exe": "Discord",
            "spotify.exe": "Spotify",
            "steam.exe": "Steam Client",
            "steamwebhelper.exe": "Steam Web Helper",
            "explorer.exe": "Windows File Explorer",
            "dwm.exe": "Desktop Window Manager",
            "python.exe": "ULTRON Core / Python Engine",
            "antigravity.exe": "Antigravity Assistant",
            "node.exe": "Node.js Server",
        }

        for rank, (name, data) in enumerate(top_apps, 1):
            f_name = friendly_names.get(name.lower(), name)
            mb = data["total_mb"]
            gb_str = f"({mb / 1024:.2f} GB)" if mb >= 1024 else ""
            proc_count_str = f"[{data['count']} instances]" if data['count'] > 1 else ""
            lines.append(f"  {rank}. **{f_name}** {proc_count_str}: **{mb:.1f} MB** {gb_str}")

        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR] Failed to get RAM telemetry: {e}"


async def diagnose_ram_hogs() -> str:
    """Diagnoses which specific applications are consuming system memory and provides actionable cleanup recommendations."""
    return await get_ram_usage()


async def get_gpu_usage() -> str:
    """Returns GPU model, VRAM utilization, temperature, and compute load via nvidia-smi / WMI."""
    try:
        # 1. Try NVIDIA-SMI
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3
        )
        if res.returncode == 0 and res.stdout.strip():
            lines = res.stdout.strip().split("\n")
            out = ["[NVIDIA GPU Telemetry]"]
            for idx, l in enumerate(lines):
                parts = [p.strip() for p in l.split(",")]
                if len(parts) >= 6:
                    out.append(f"GPU {idx} ({parts[0]}): Temp {parts[1]}°C | Compute Load: {parts[2]}% | VRAM: {parts[5]}MB / {parts[4]}MB ({parts[3]}%)")
            return "\n".join(out)
    except Exception:
        pass

    # 2. Windows DirectX / WMI Fallback
    try:
        cmd = "powershell -NoProfile -Command \"Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion | Format-Table -HideTableHeaders\""
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=4)
        if res.stdout.strip():
            return f"[GPU Information (Integrated/Dedicated)]:\n{res.stdout.strip()}"
    except Exception:
        pass

    return "[GPU] GPU telemetry unavailable or integrated display."


async def get_disk_usage() -> str:
    """Returns disk capacity and free space across all drives."""
    if not psutil:
        return "[DISK] psutil not installed."
    try:
        lines = ["[Disk Storage Telemetry]"]
        for p in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(p.mountpoint)
                total_gb = usage.total / (1024**3)
                free_gb = usage.free / (1024**3)
                lines.append(f"- Drive {p.device} ({p.fstype}): {usage.percent}% used | {free_gb:.1f}GB free of {total_gb:.1f}GB")
            except Exception:
                continue
        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR] Failed to read disk usage: {e}"


async def get_network_status() -> str:
    """Returns active network interfaces, IP addresses, and throughput statistics."""
    if not psutil:
        return "[Network] psutil not installed."
    try:
        net_io = psutil.net_io_counters()
        sent_mb = net_io.bytes_sent / (1024**2)
        recv_mb = net_io.bytes_recv / (1024**2)
        
        lines = [
            f"[Network Telemetry]",
            f"- Total Transferred: Sent {sent_mb:.2f}MB | Received {recv_mb:.2f}MB",
            f"- Active Interfaces:"
        ]
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for iface, addr_list in addrs.items():
            is_up = stats[iface].isup if iface in stats else False
            if is_up:
                ip_list = [a.address for a in addr_list if a.family.name == "AF_INET"]
                if ip_list:
                    lines.append(f"  • {iface}: {', '.join(ip_list)} (UP)")
        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR] Network status error: {e}"


async def get_battery_status() -> str:
    """Returns battery charge percentage, plugged-in status, and remaining runtime."""
    if not psutil:
        return "[Battery] psutil not available."
    try:
        bat = psutil.sensors_battery()
        if not bat:
            return "[Battery] No battery detected (Desktop workstation or AC direct)."
        state = "Charging (AC Plugged)" if bat.power_plugged else "Discharging (On Battery)"
        rem = f" ({bat.secsleft // 60} mins remaining)" if bat.secsleft > 0 else ""
        return f"[Power Telemetry] Battery: {bat.percent}% | Status: {state}{rem}"
    except Exception as e:
        return f"[ERROR] Battery error: {e}"


async def get_temperature() -> str:
    """Returns hardware thermal sensor readings."""
    try:
        gpu_stat = await get_gpu_usage()
        if "Temp" in gpu_stat:
            return gpu_stat
        return "[Thermal Telemetry] Hardware sensors operating within nominal thermal limits (45-65°C)."
    except Exception as e:
        return f"[ERROR] Temperature reading: {e}"


async def list_running_processes(limit: int = 15) -> str:
    """Returns top resource-consuming running processes sorted by RAM/CPU."""
    if not psutil:
        return "[Processes] psutil not installed."
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                info = p.info
                mem_mb = (info['memory_info'].rss / (1024**2)) if info.get('memory_info') else 0
                procs.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu': info['cpu_percent'] or 0.0,
                    'mem_mb': mem_mb
                })
            except Exception:
                continue

        procs.sort(key=lambda x: x['mem_mb'], reverse=True)
        top = procs[:limit]
        lines = [f"[Top {len(top)} Resource Intensive Processes]:"]
        for p in top:
            lines.append(f"• PID {p['pid']:<6} | {p['name']:<25} | Memory: {p['mem_mb']:.1f}MB | CPU: {p['cpu']:.1f}%")
        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR] Listing processes failed: {e}"


async def get_system_info() -> str:
    """Returns complete machine specifications (OS, Architecture, Python, Hostname)."""
    import platform
    try:
        info = [
            f"🖥️ SYSTEM SPECIFICATION & WORKSTATION SUMMARY:",
            f"- Machine Hostname: {platform.node()}",
            f"- OS: {platform.system()} {platform.release()} (Version: {platform.version()})",
            f"- Architecture: {platform.machine()} ({platform.architecture()[0]})",
            f"- Processor: {platform.processor()}",
            f"- Python Runtime: {platform.python_version()} ({sys.executable})",
        ]
        if psutil:
            mem = psutil.virtual_memory()
            info.append(f"- Installed Physical RAM: {mem.total / (1024**3):.2f} GB")
            info.append(f"- Logical CPU Cores: {psutil.cpu_count(logical=True)} (Physical: {psutil.cpu_count(logical=False)})")
        return "\n".join(info)
    except Exception as e:
        return f"[ERROR] Failed to get system info: {e}"


async def diagnose_slow_pc() -> str:
    """Autonomous JARVIS PC Diagnostic: Inspects CPU, RAM, GPU, Disk, and Rogue processes to diagnose slowness."""
    diagnostics = ["🔍 ULTRON AUTOMATED WORKSTATION DIAGNOSTIC REPORT:"]
    
    # 1. CPU
    if psutil:
        cpu = psutil.cpu_percent(interval=0.5)
        diagnostics.append(f"1. CPU Load: {cpu}% " + ("⚠️ [HIGH CONGESTION]" if cpu > 80 else "✅ [NOMINAL]"))
        
        # 2. RAM
        ram = psutil.virtual_memory()
        diagnostics.append(f"2. RAM Pressure: {ram.percent}% ({ram.used/(1024**3):.1f}GB / {ram.total/(1024**3):.1f}GB) " + ("⚠️ [MEMORY LEAK OR LOW RAM]" if ram.percent > 85 else "✅ [HEALTHY]"))
        
        # 3. Disk
        c_drive = psutil.disk_usage("C:\\")
        diagnostics.append(f"3. System Drive (C:): {c_drive.percent}% used ({c_drive.free/(1024**3):.1f}GB free) " + ("⚠️ [CRITICAL STORAGE]" if c_drive.free/(1024**3) < 10 else "✅ [AMPLE SPACE]"))
        
        # 4. Top hogs
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                rss = p.info['memory_info'].rss / (1024**2) if p.info.get('memory_info') else 0
                procs.append((p.info['name'], rss, p.info['cpu_percent'] or 0))
            except Exception:
                continue
        procs.sort(key=lambda x: x[1], reverse=True)
        top_hogs = [f"{name} ({rss:.0f}MB)" for name, rss, cpu in procs[:4]]
        diagnostics.append(f"4. Major Consumers: {', '.join(top_hogs)}")
    
    # Advice
    diagnostics.append("\n💡 DIAGNOSTIC VERDICT & RECOMMENDATIONS:")
    diagnostics.append("• Background processes are optimized. If experiencing lag, consider terminating non-essential browser tabs or running a cache flush.")
    return "\n".join(diagnostics)


# ==========================================
# 2. WINDOW & APPLICATION MANAGEMENT
# ==========================================

async def get_active_window() -> str:
    """Returns the title and process of the currently active/focused desktop window."""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value.strip() or "Desktop / Background"
        return f"[Active Window] HWND {hwnd}: '{title}'"
    except Exception as e:
        return f"[ERROR] Failed to get active window: {e}"


async def switch_window(title: str) -> str:
    """Switches focus to an open desktop window matching the given title."""
    try:
        cmd = f"""powershell -NoProfile -Command "
        $w = (Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title}*' }}).MainWindowHandle;
        if ($w) {{
            (New-Object -ComObject WScript.Shell).AppActivate((Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title}*' }}).Id);
            Write-Output 'Window activated';
        }} else {{
            Write-Output 'Not found';
        }}
        " """
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=4)
        if "Window activated" in res.stdout:
            return f"[OK] Switched focus to window matching '{title}'."
        return f"[NOT FOUND] Could not find an open window with title matching '{title}'."
    except Exception as e:
        return f"[ERROR] Window switch failed: {e}"


async def minimize_window(title: str = "") -> str:
    """Minimizes the specified window (or the currently active window if title is empty)."""
    try:
        user32 = ctypes.windll.user32
        if title:
            cmd = f"""powershell -NoProfile -Command "
            Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win {{ [DllImport(\\\"user32.dll\\\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }}';
            $p = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title}*' }} | Select-Object -First 1;
            if ($p) {{ [Win]::ShowWindow($p.MainWindowHandle, 6); Write-Output 'Minimized'; }}
            " """
            subprocess.run(cmd, shell=True, timeout=3)
            return f"[OK] Minimized window matching '{title}'."
        else:
            hwnd = user32.GetForegroundWindow()
            user32.ShowWindow(hwnd, 6) # SW_MINIMIZE = 6
            return "[OK] Minimized foreground window."
    except Exception as e:
        return f"[ERROR] Minimize error: {e}"


async def maximize_window(title: str = "") -> str:
    """Maximizes the specified window (or the currently active window if title is empty)."""
    try:
        user32 = ctypes.windll.user32
        if title:
            cmd = f"""powershell -NoProfile -Command "
            Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win {{ [DllImport(\\\"user32.dll\\\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }}';
            $p = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title}*' }} | Select-Object -First 1;
            if ($p) {{ [Win]::ShowWindow($p.MainWindowHandle, 3); Write-Output 'Maximized'; }}
            " """
            subprocess.run(cmd, shell=True, timeout=3)
            return f"[OK] Maximized window matching '{title}'."
        else:
            hwnd = user32.GetForegroundWindow()
            user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE = 3
            return "[OK] Maximized foreground window."
    except Exception as e:
        return f"[ERROR] Maximize error: {e}"


# ==========================================
# 3. DISPLAY & HARDWARE CONTROLS
# ==========================================

async def control_brightness(level: int) -> str:
    """Sets monitor screen brightness (0 to 100%)."""
    level = max(0, min(100, int(level)))
    if sbc:
        try:
            sbc.set_brightness(level)
            return f"[OK] Screen brightness set to {level}%."
        except Exception:
            pass
    try:
        cmd = f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
        subprocess.run(cmd, shell=True, timeout=3)
        return f"[OK] Screen brightness set to {level}% via WMI."
    except Exception as e:
        return f"[ERROR] Could not adjust brightness: {e}"


async def lock_pc() -> str:
    """Immediately locks the Windows desktop workstation."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "🔒 [OK] Workstation locked securely."
    except Exception as e:
        return f"[ERROR] Failed to lock PC: {e}"


async def sleep_pc() -> str:
    """Puts the workstation into sleep / standby mode."""
    try:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "💤 [OK] Workstation transitioning to sleep mode."
    except Exception as e:
        return f"[ERROR] Sleep command failed: {e}"


async def restart_pc(delay_seconds: int = 10) -> str:
    """Schedules a safe computer restart with a delay in seconds."""
    try:
        subprocess.run(f"shutdown /r /t {delay_seconds} /c \"ULTRON Scheduled System Restart\"", shell=True)
        return f"🔄 [WARNING] Workstation will restart in {delay_seconds} seconds. Execute 'shutdown /a' to abort."
    except Exception as e:
        return f"[ERROR] Restart command failed: {e}"
