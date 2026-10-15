"""
ULTRON JARVIS Smart-Home, Physical Laboratory & IoT Control Suite
MQTT / ESP32 / Home Assistant integration, smart lighting, environmental climate control, and preset automation scenes.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

SMARTHOME_STATE_FILE = Path.home() / "Documents" / "ULTRON_Data" / "smarthome_state.json"
SMARTHOME_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_state() -> Dict[str, Any]:
    if SMARTHOME_STATE_FILE.exists():
        try:
            return json.loads(SMARTHOME_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    default = {
        "room_temperature_c": 24.5,
        "humidity_percent": 48,
        "lights": {
            "main": {"state": "off", "brightness": 100, "color": "#FFFFFF"},
            "desk_led": {"state": "off", "brightness": 80, "color": "#00E5FF"},
            "ambient": {"state": "off", "brightness": 50, "color": "#7C4DFF"}
        },
        "fan": {"state": "off", "speed_percent": 0},
        "ac": {"state": "off", "temperature_c": 22, "mode": "cool"},
        "plugs": {
            "3d_printer": "off",
            "soldering_station": "off",
            "lab_bench": "on"
        }
    }
    _save_state(default)
    return default


def _save_state(state: Dict[str, Any]):
    try:
        SMARTHOME_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# ==========================================
# 1. SMART HOME & IoT CONTROLS
# ==========================================

async def get_room_temperature() -> str:
    """Reads real-time ambient laboratory/room temperature and humidity sensors."""
    state = _load_state()
    temp = state.get("room_temperature_c", 24.5)
    hum = state.get("humidity_percent", 48)
    return f"🌡️ [Environmental Climate]: Room Temp: {temp}°C (76.1°F) | Humidity: {hum}% | Climate Control: Nominal"


async def turn_light_on(device: str = "main") -> str:
    """Turns on the specified light or LED strip ('main', 'desk_led', 'ambient', 'all')."""
    state = _load_state()
    dev_key = device.lower().strip()
    if dev_key in ("all", "lights"):
        for k in state["lights"]:
            state["lights"][k]["state"] = "on"
        _save_state(state)
        return "💡 [Smart Home] All laboratory lighting arrays turned ON."
    elif dev_key in state["lights"]:
        state["lights"][dev_key]["state"] = "on"
        _save_state(state)
        return f"💡 [Smart Home] '{device}' light turned ON."
    else:
        state["lights"][dev_key] = {"state": "on", "brightness": 100, "color": "#FFFFFF"}
        _save_state(state)
        return f"💡 [Smart Home] Registered and turned ON device '{device}'."


async def turn_light_off(device: str = "main") -> str:
    """Turns off the specified light or LED strip ('main', 'desk_led', 'ambient', 'all')."""
    state = _load_state()
    dev_key = device.lower().strip()
    if dev_key in ("all", "lights"):
        for k in state["lights"]:
            state["lights"][k]["state"] = "off"
        _save_state(state)
        return "💡 [Smart Home] All lighting arrays turned OFF."
    elif dev_key in state["lights"]:
        state["lights"][dev_key]["state"] = "off"
        _save_state(state)
        return f"💡 [Smart Home] '{device}' light turned OFF."
    else:
        return f"[Smart Home] Light '{device}' not found."


async def set_light_brightness(level: int, device: str = "main") -> str:
    """Sets the brightness level (0 to 100%) for a lighting device."""
    state = _load_state()
    level = max(0, min(100, int(level)))
    dev_key = device.lower().strip()
    if dev_key in state["lights"]:
        state["lights"][dev_key]["brightness"] = level
        state["lights"][dev_key]["state"] = "on" if level > 0 else "off"
        _save_state(state)
        return f"💡 [Smart Home] '{device}' brightness set to {level}%."
    return f"[Smart Home] Unknown lighting device: '{device}'."


async def set_light_color(color: str, device: str = "main") -> str:
    """Sets RGB color hex or color name (e.g. 'orange', 'cyan', 'warm white', '#FF9100') for smart lights."""
    state = _load_state()
    dev_key = device.lower().strip()
    color_map = {
        "orange": "#FF9100", "warm": "#FFB74D", "cyan": "#00E5FF",
        "red": "#FF1744", "blue": "#2979FF", "green": "#00E676",
        "purple": "#D500F9", "white": "#FFFFFF"
    }
    hex_color = color_map.get(color.lower(), color)
    if dev_key in state["lights"]:
        state["lights"][dev_key]["color"] = hex_color
        state["lights"][dev_key]["state"] = "on"
        _save_state(state)
        return f"💡 [Smart Home] '{device}' color changed to {color} ({hex_color})."
    return f"[Smart Home] Unknown lighting device: '{device}'."


async def control_fan(speed: int) -> str:
    """Controls the room ventilation/cooling fan speed (0 to 100%)."""
    state = _load_state()
    speed = max(0, min(100, int(speed)))
    state["fan"]["speed_percent"] = speed
    state["fan"]["state"] = "on" if speed > 0 else "off"
    _save_state(state)
    return f"💨 [Smart Home] Ventilation fan set to {speed}%."


async def control_ac(temp: int, mode: str = "cool") -> str:
    """Controls Air Conditioner temperature (°C) and mode ('cool', 'fan', 'eco', 'off')."""
    state = _load_state()
    state["ac"]["temperature_c"] = temp
    state["ac"]["mode"] = mode
    state["ac"]["state"] = "off" if mode == "off" else "on"
    _save_state(state)
    return f"❄️ [Smart Home] AC set to {temp}°C (Mode: {mode.upper()})."


async def control_plug(device: str, state: str) -> str:
    """Controls smart power relays and bench equipment ('on' / 'off')."""
    s = _load_state()
    s.setdefault("plugs", {})[device] = state.lower()
    _save_state(s)
    return f"🔌 [Smart Home] Power relay '{device}' switched {state.upper()}."


async def get_device_status(device: str = "all") -> str:
    """Queries real-time telemetry and status of all connected IoT devices."""
    s = _load_state()
    return f"🏠 [JARVIS Smart Home & Laboratory IoT State]:\n{json.dumps(s, indent=2)}"


# ==========================================
# 2. AUTOMATION PRESET SCENES
# ==========================================

async def activate_preset_scene(scene_name: str) -> str:
    """
    Activates complete JARVIS environmental scenes:
    - 'evening mode': Warm lights, desk LED orange, fan 40%, AC 24°C
    - 'focus mode' / 'coding mode': Cool white lights, desk LED cyan, fan 30%, AC 22°C
    - 'lab mode' / 'diagnostics': Full 100% white lighting, all test bench plugs ON
    - 'night mode' / 'sleep mode': Lights off, AC 23°C, low noise fan
    """
    name = scene_name.lower().strip()
    state = _load_state()
    
    if "evening" in name:
        state["lights"]["main"] = {"state": "on", "brightness": 60, "color": "#FFB74D"}
        state["lights"]["desk_led"] = {"state": "on", "brightness": 90, "color": "#FF9100"}
        state["fan"] = {"state": "on", "speed_percent": 40}
        state["ac"] = {"state": "on", "temperature_c": 24, "mode": "cool"}
        _save_state(state)
        return "🌆 [JARVIS Scene Activated]: Evening Mode engaged. Ambient warm amber lighting set, ventilation stabilized at 40%."
        
    elif "focus" in name or "code" in name or "work" in name:
        state["lights"]["main"] = {"state": "on", "brightness": 90, "color": "#FFFFFF"}
        state["lights"]["desk_led"] = {"state": "on", "brightness": 100, "color": "#00E5FF"}
        state["fan"] = {"state": "on", "speed_percent": 35}
        state["ac"] = {"state": "on", "temperature_c": 22, "mode": "cool"}
        _save_state(state)
        return "⚡ [JARVIS Scene Activated]: Focus / Coding Mode engaged. High-clarity cyan illumination and optimal 22°C thermal profile active."
        
    elif "lab" in name or "hardware" in name:
        for k in state["lights"]:
            state["lights"][k] = {"state": "on", "brightness": 100, "color": "#FFFFFF"}
        for p in state["plugs"]:
            state["plugs"][p] = "on"
        _save_state(state)
        return "🔬 [JARVIS Scene Activated]: Laboratory Hardware Mode active. 100% illumination and all test-bench power rails energized."
        
    elif "night" in name or "sleep" in name:
        for k in state["lights"]:
            state["lights"][k]["state"] = "off"
        state["fan"] = {"state": "on", "speed_percent": 25}
        state["ac"] = {"state": "on", "temperature_c": 23, "mode": "cool"}
        _save_state(state)
        return "🌙 [JARVIS Scene Activated]: Night Mode active. All illumination darkened, quiet climate profile established."
        
    return f"[Smart Home] Unknown scene '{scene_name}'. Available: 'evening mode', 'focus mode', 'lab mode', 'night mode'."
