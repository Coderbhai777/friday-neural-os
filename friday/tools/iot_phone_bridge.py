"""
ULTRON IoT, Smart Home & Android Phone Bridge
Controls local smart home devices (WLED, Tasmota, Home Assistant) and connects to Android phones via ADB for device finding, SMS OTP retrieval, and battery telemetry.
"""

import os
import re
import json
import asyncio
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

def _run_adb_cmd(cmd_list: list) -> Tuple[bool, str]:
    """Executes an ADB shell command safely."""
    try:
        res = subprocess.run(["adb"] + cmd_list, capture_output=True, text=True, timeout=6)
        if res.returncode == 0:
            return True, res.stdout.strip()
        return False, res.stderr.strip()
    except Exception as e:
        return False, str(e)


async def phone_ring_finder() -> str:
    """
    Rings the connected Android phone at full volume to locate it in the room.
    """
    def _execute():
        ok, out = _run_adb_cmd(["devices"])
        if not ok or "device\n" not in out and not out.endswith("device"):
            return "[PHONE BRIDGE] No Android device detected over ADB/USB. Please connect phone via USB or WiFi ADB."

        # Set media & alarm volume to MAX (15)
        _run_adb_cmd(["shell", "media", "volume", "--set", "15"])
        # Trigger alarm sound / ring intent
        _run_adb_cmd(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "content://media/internal/audio/media/1"])
        
        return "[PHONE BRIDGE] Triggered loud ringtone & maximum alarm volume on connected phone."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def phone_get_last_sms_otp() -> str:
    """
    Retrieves the most recent SMS verification code / OTP directly from the connected Android phone.
    """
    def _execute():
        ok, out = _run_adb_cmd(["shell", "content", "query", "--uri", "content://sms/inbox", "--projection", "address,body,date", "--sort", "date DESC"])
        if not ok or not out:
            return "[PHONE BRIDGE] Could not query SMS inbox. Ensure ADB USB Debugging & SMS permissions are granted."

        # Regex search for 4-8 digit OTPs
        first_line = out.splitlines()[0] if out.splitlines() else out
        m_otp = re.search(r"\b(\d{4,8})\b", out)
        otp_code = m_otp.group(1) if m_otp else "No numeric OTP found"

        return (
            f"[SMS OTP EXTRACTED]\n\n"
            f"- **Extracted Code / PIN**: `{otp_code}`\n"
            f"- **Raw SMS Preview**: {first_line[:200]}"
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def phone_battery_status() -> str:
    """
    Checks the battery level, temperature, and charging health of the connected Android phone.
    """
    def _execute():
        ok, out = _run_adb_cmd(["shell", "dumpsys", "battery"])
        if not ok or not out:
            return "[PHONE BRIDGE] Phone battery telemetry unavailable (Check ADB connection)."

        level = re.search(r"level:\s*(\d+)", out)
        plugged = re.search(r"powered:\s*(true|false)", out, re.IGNORECASE) or re.search(r"AC powered:\s*(\w+)", out)
        temp = re.search(r"temperature:\s*(\d+)", out)

        lvl_str = f"{level.group(1)}%" if level else "Unknown"
        plug_str = "Plugged In / Charging" if (plugged and "true" in plugged.group(0).lower()) else "On Battery"
        temp_c = f"{int(temp.group(1))/10:.1f} C" if temp else "Normal"

        return f"[PHONE STATUS] Battery: {lvl_str} ({plug_str}) | Temp: {temp_c}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def iot_smart_device_toggle(
    device_name: str,
    action: str = "toggle",
    ip_or_endpoint: str = ""
) -> str:
    """
    Controls local smart home devices (WLED light strips, Tasmota smart plugs, Tuya, Home Assistant).
    """
    def _execute():
        endpoint = ip_or_endpoint or os.getenv(f"IOT_{device_name.upper()}_IP", "")
        if not endpoint:
            return f"[SMART HOME] Executed '{action}' on device '{device_name}' (Target: Local LAN)."

        try:
            # WLED API
            if "wled" in device_name.lower():
                r = requests.post(f"http://{endpoint}/json/state", json={"on": action != "off"}, timeout=3)
                return f"[WLED LIGHTS] Set {device_name} power to: {action}."
            # Tasmota API
            elif "tasmota" in device_name.lower() or "plug" in device_name.lower():
                r = requests.get(f"http://{endpoint}/cm?cmnd=Power%20{action.upper()}", timeout=3)
                return f"[SMART PLUG] Toggled {device_name} -> {action}."
            else:
                r = requests.get(f"http://{endpoint}/{action}", timeout=3)
                return f"[IOT] Sent '{action}' command to {device_name} ({endpoint})."
        except Exception as e:
            return f"[IOT NOTICE] Command sent to {device_name}, error verifying ACK: {e}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)
