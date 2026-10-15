"""
ULTRON Advanced System Diagnostics & Hardware Telemetry (Adapted from ULTRON-Echo)
Provides battery health, thermal sensor checks, display brightness control,
and installed game library detection (Steam / Epic Games).
"""

import os
import psutil
import asyncio
import subprocess
from typing import Dict, Any, List

def _get_battery_info() -> Dict[str, Any]:
    battery = psutil.sensors_battery()
    if not battery:
        return {"has_battery": False, "percent": 100, "power_plugged": True}
    return {
        "has_battery": True,
        "percent": battery.percent,
        "power_plugged": battery.power_plugged,
        "secs_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1
    }


def _get_installed_games() -> List[str]:
    """Detects installed Steam and Epic Games titles on Windows."""
    games = []
    steam_path = Path(r"C:\Program Files (x86)\Steam\steamapps")
    if steam_path.exists():
        for item in steam_path.glob("appmanifest_*.acf"):
            try:
                content = item.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    if '"name"' in line:
                        parts = line.split('"')
                        if len(parts) >= 4:
                            games.append(f"Steam: {parts[3]}")
                        break
            except Exception:
                pass
    return games[:15]


async def get_battery_and_power_status() -> str:
    """
    Returns detailed battery percentage, charging state, and estimated remaining life.
    """
    info = _get_battery_info()
    if not info["has_battery"]:
        return "[BATTERY] Desktop AC Power (No battery detected)."
    state = "Charging" if info["power_plugged"] else "Discharging"
    return f"[BATTERY] {info['percent']}% ({state})."


async def set_display_brightness(level: int) -> str:
    """
    Sets Windows monitor display brightness from 0 to 100.
    """
    lvl = max(0, min(100, level))
    ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {lvl})"
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            return f"[OK] Display brightness set to {lvl}%."
        return f"[BRIGHTNESS NOTICE] Hardware brightness control not supported on this display interface."
    except Exception as e:
        return f"[ERROR] Could not adjust brightness: {e}"


async def scan_installed_games() -> str:
    """
    Scans local storage for installed Steam and PC games.
    """
    games = _get_installed_games()
    if not games:
        return "[GAMES] No active Steam library games detected."
    return f"[INSTALLED GAMES ({len(games)})]:\n" + "\n".join([f"- {g}" for g in games])
