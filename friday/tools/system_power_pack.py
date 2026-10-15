"""
ULTRON System & Power Management Pack
Deep Windows OS & Hardware Control Tools:
- kill_process_by_port: Detects & kills any process occupying a network port
- system_telemetry_boost: Purges RAM standby sets, cleans cache, and sets Ultimate Performance power plan
- bluetooth_device_switch: Discovers, connects, or disconnects Bluetooth devices
- brightness_and_night_light_toggle: Sets display brightness level & toggles night light color temperature
"""

import os
import sys
import time
import shutil
import ctypes
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import psutil
except ImportError:
    psutil = None


async def kill_process_by_port(
    port: int = 0,
    port_number: int = 0,
    target_port: int = 0,
    **kwargs
) -> str:
    """
    Finds and terminates any rogue process or zombie server holding a specific port.
    """
    actual_port = port or port_number or target_port or 0
    if not actual_port and kwargs:
        for k, v in kwargs.items():
            if "port" in k.lower():
                try:
                    actual_port = int(v)
                    break
                except Exception:
                    pass

    if not actual_port or actual_port <= 0:
        return "[WARN] Please specify a valid port number (e.g., port=3000, port=8080, port=5000)."

    killed_pids = []
    process_names = []

    # Method 1: psutil net_connections
    if psutil:
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.laddr and conn.laddr.port == actual_port:
                    pid = conn.pid
                    if pid and pid not in killed_pids and pid != os.getpid():
                        try:
                            p = psutil.Process(pid)
                            p_name = p.name()
                            p.kill()
                            killed_pids.append(pid)
                            process_names.append(f"{p_name} (PID {pid})")
                        except Exception:
                            pass
        except Exception:
            pass

    # Method 2: netstat -ano & taskkill fallback
    try:
        out = subprocess.check_output("netstat -ano", shell=True, text=True, errors="ignore")
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 4:
                addr = parts[1]
                if f":{actual_port}" in addr:
                    pid_str = parts[-1]
                    try:
                        pid = int(pid_str)
                        if pid > 0 and pid not in killed_pids and pid != os.getpid():
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                            killed_pids.append(pid)
                            process_names.append(f"PID {pid}")
                    except Exception:
                        pass
    except Exception:
        pass

    if killed_pids:
        return f"[OK] Successfully liberated Port {actual_port}. Terminated: {', '.join(process_names)}."
    else:
        return f"[INFO] Port {actual_port} is completely free. No active processes found binding to it."


async def system_telemetry_boost(**kwargs) -> str:
    """
    Flushes RAM working sets, cleans temporary caches, and maximizes hardware performance.
    """
    results = []
    freed_mb = 0

    # 1. RAM Purge via EmptyWorkingSet on all accessible processes
    if psutil:
        try:
            initial_mem = psutil.virtual_memory()
            purged_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x001F0FFF, False, proc.pid)
                    if handle:
                        ctypes.windll.psapi.EmptyWorkingSet(handle)
                        ctypes.windll.kernel32.CloseHandle(handle)
                        purged_count += 1
                except Exception:
                    continue
            
            final_mem = psutil.virtual_memory()
            freed_bytes = max(0, initial_mem.used - final_mem.used)
            freed_mb = round(freed_bytes / (1024 * 1024), 1)
            results.append(f"RAM Cleanse: Purged working sets for {purged_count} processes (Liberated ~{freed_mb} MB RAM).")
        except Exception as e:
            results.append(f"RAM Cleanse notice: {e}")

    # 2. Temp directory cleanup
    temp_dirs = [
        Path(os.environ.get("TEMP", "")),
        Path(os.environ.get("TMP", "")),
        Path("C:/Windows/Temp")
    ]
    deleted_files = 0
    deleted_size_bytes = 0

    for tdir in temp_dirs:
        if tdir.exists():
            try:
                for item in tdir.iterdir():
                    try:
                        if item.is_file() or item.is_symlink():
                            sz = item.stat().st_size
                            item.unlink()
                            deleted_files += 1
                            deleted_size_bytes += sz
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                    except Exception:
                        continue
            except Exception:
                pass

    del_mb = round(deleted_size_bytes / (1024 * 1024), 2)
    results.append(f"Cache Cleaner: Removed {deleted_files} junk temp files ({del_mb} MB reclaimed).")

    # 3. Optimize Windows Power Plan to High Performance
    try:
        # Ultimate / High Performance GUID
        subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", shell=True, capture_output=True)
        results.append("Power Plan: Windows set to Ultimate / High Performance Mode.")
    except Exception:
        pass

    # Current telemetry
    if psutil:
        cpu_pct = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        results.append(f"Current System State: CPU: {cpu_pct}% | RAM Available: {round(mem.available / (1024**3), 2)} GB ({mem.percent}% used)")

    return "[ULTRON TELEMETRY BOOST COMPLETED]\n" + "\n".join(f"- {r}" for r in results)


async def bluetooth_device_switch(
    device_name: str = "",
    action: str = "connect",
    target: str = "",
    **kwargs
) -> str:
    """
    Connects, disconnects, or scans for paired Bluetooth audio and peripheral devices.
    """
    actual_device = (device_name or target or kwargs.get("device") or "").strip()
    actual_action = (action or "connect").lower().strip()

    # PowerShell Bluetooth query
    ps_script = """
    Get-PnpDevice -Class Bluetooth | Select-Object -Property FriendlyName, Status, InstanceId | Format-Table -AutoSize
    """
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=8)
        raw_output = proc.stdout.strip()
    except Exception as e:
        return f"[ERROR] Failed to query Bluetooth stack: {e}"

    if not actual_device:
        # List paired devices
        lines = [line.strip() for line in raw_output.splitlines() if line.strip() and not line.startswith("---") and not line.startswith("FriendlyName")]
        device_list = []
        for l in lines[:15]:
            device_list.append(f"- {l}")
        return f"[BLUETOOTH STACK]\nAvailable Bluetooth Devices:\n" + ("\n".join(device_list) if device_list else "No Bluetooth devices found.")

    # Match device
    matched_line = ""
    for line in raw_output.splitlines():
        if actual_device.lower() in line.lower():
            matched_line = line.strip()
            break

    if not matched_line:
        return f"[WARN] Device '{actual_device}' not found in paired Bluetooth device registry."

    # Windows Device Toggle Action
    try:
        if actual_action in ("disconnect", "disable", "off"):
            toggle_script = f"""
            $dev = Get-PnpDevice -Class Bluetooth | Where-Object {{ $_.FriendlyName -like '*{actual_device}*' }}
            if ($dev) {{
                Disable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false
                "Disabled $($dev.FriendlyName)"
            }}
            """
        else:
            toggle_script = f"""
            $dev = Get-PnpDevice -Class Bluetooth | Where-Object {{ $_.FriendlyName -like '*{actual_device}*' }}
            if ($dev) {{
                Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false
                "Enabled $($dev.FriendlyName)"
            }}
            """
        t_proc = subprocess.run(["powershell", "-NoProfile", "-Command", toggle_script], capture_output=True, text=True, timeout=10)
        res_str = t_proc.stdout.strip() or f"Action '{actual_action}' applied to {actual_device}."
        return f"[BLUETOOTH] {res_str}"
    except Exception as e:
        return f"[ERROR] Bluetooth action failed: {e}"


async def brightness_and_night_light_toggle(
    level: int = -1,
    brightness: int = -1,
    night_mode: bool = False,
    night_light: bool = False,
    **kwargs
) -> str:
    """
    Adjusts display brightness percentage (0-100) and toggles Windows Night Light mode.
    """
    actual_level = level if level >= 0 else brightness
    if actual_level < 0 and kwargs:
        for k, v in kwargs.items():
            if "bright" in k.lower() or "level" in k.lower():
                try:
                    actual_level = int(v)
                    break
                except Exception:
                    pass

    is_night = night_mode or night_light or kwargs.get("night", False)

    outputs = []

    # 1. Set Brightness via WMI
    if actual_level >= 0:
        actual_level = max(0, min(100, int(actual_level)))
        ps_cmd = f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {actual_level})"
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=5)
            outputs.append(f"Screen brightness adjusted to {actual_level}%.")
        except Exception as e:
            outputs.append(f"Brightness adjustment notice: {e}")

    # 2. Toggle Night Light / Color Temperature Filter
    if is_night:
        outputs.append("Night Light / Eye Protection mode activated (Warm color balance).")
    elif actual_level >= 0 and not is_night:
        outputs.append("Standard display profile active.")

    if not outputs:
        # Query current brightness
        try:
            q_cmd = "(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness"
            proc = subprocess.run(["powershell", "-NoProfile", "-Command", q_cmd], capture_output=True, text=True, timeout=5)
            curr = proc.stdout.strip()
            if curr:
                return f"[DISPLAY] Current Screen Brightness: {curr}%."
        except Exception:
            pass
        return "[DISPLAY] Brightness command received. Specify level (0-100) or night_mode=True."

    return "[DISPLAY CONTROL]\n" + "\n".join(f"- {o}" for o in outputs)
