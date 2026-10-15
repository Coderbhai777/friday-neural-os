"""
ULTRON JARVIS Central World Model (Layer 1)
Consolidated real-time environmental state, user attention context, hardware bus status,
and active multi-step mission tracking.
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional

WORLD_STATE_FILE = Path.home() / "Documents" / "ULTRON_Data" / "world_state.json"
WORLD_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()


def _get_default_world_state() -> Dict[str, Any]:
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": {
            "name": "Shivansh Sagar Pancholi",
            "role": "Creator & Lead Architect",
            "current_focus": "Autonomous Robotics & AI Engineering",
            "attention_state": "Workstation Active"
        },
        "workstation": {
            "active_window": "VS Code",
            "cpu_percent": 0.0,
            "ram_percent": 0.0,
            "system_status": "ONLINE"
        },
        "hardware_bus": {
            "connected_boards": [],
            "i2c_devices": [],
            "sensors": [],
            "actuators": []
        },
        "environment": {
            "room_temperature_c": 24.5,
            "humidity_percent": 48,
            "lighting_scene": "Focus Mode (Cyan / 6500K)",
            "motion_detected": True
        },
        "active_mission": {
            "id": None,
            "title": "Idle / Standby",
            "progress_percent": 0,
            "current_step": "Awaiting Command"
        }
    }


def _load_world_state() -> Dict[str, Any]:
    with _lock:
        if WORLD_STATE_FILE.exists():
            try:
                return json.loads(WORLD_STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        state = _get_default_world_state()
        _save_world_state(state)
        return state


def _save_world_state(state: Dict[str, Any]):
    with _lock:
        try:
            state["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            WORLD_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


# ==========================================
# PUBLIC WORLD MODEL API
# ==========================================

async def get_world_state() -> str:
    """
    Returns the complete consolidated live world model: User Focus, Workstation, Hardware, Environment, and Active Mission.
    """
    state = _load_world_state()
    
    # Auto-refresh live workstation metrics if psutil is available
    try:
        import psutil
        state["workstation"]["cpu_percent"] = psutil.cpu_percent(interval=None)
        state["workstation"]["ram_percent"] = psutil.virtual_memory().percent
    except Exception:
        pass

    # Refresh active window
    try:
        from friday_tools.jarvis_system_control import get_active_window
        win_str = await get_active_window()
        state["workstation"]["active_window"] = win_str
    except Exception:
        pass

    _save_world_state(state)

    lines = [
        "🌐 [ULTRON LIVE WORLD MODEL]:",
        f"• USER: {state['user']['name']} | Focus: {state['user']['current_focus']} ({state['user']['attention_state']})",
        f"• WORKSTATION: CPU {state['workstation']['cpu_percent']}% | RAM {state['workstation']['ram_percent']}% | Focused: {state['workstation']['active_window']}",
        f"• ENVIRONMENT: {state['environment']['room_temperature_c']}°C | Lighting: {state['environment']['lighting_scene']}",
        f"• HARDWARE: {len(state['hardware_bus']['connected_boards'])} board(s) | {len(state['hardware_bus']['sensors'])} sensor(s)",
        f"• MISSION: {state['active_mission']['title']} [{state['active_mission']['progress_percent']}%] -> {state['active_mission']['current_step']}"
    ]
    return "\n".join(lines)


async def update_world_state(section: str, data_json_or_text: str) -> str:
    """
    Updates a section of the live world model ('user', 'workstation', 'hardware_bus', 'environment', 'active_mission').
    """
    state = _load_world_state()
    sec_key = section.lower().strip()
    
    try:
        val = json.loads(data_json_or_text) if (data_json_or_text.startswith("{") or data_json_or_text.startswith("[")) else data_json_or_text
    except Exception:
        val = data_json_or_text

    if sec_key in state and isinstance(state[sec_key], dict) and isinstance(val, dict):
        state[sec_key].update(val)
    elif sec_key in state:
        state[sec_key] = val
    else:
        state[sec_key] = val

    _save_world_state(state)
    return f"🌐 [World Model Updated]: Section '{section}' updated successfully."


async def get_user_context() -> str:
    """Returns real-time profile, active tasks, and context of the user."""
    state = _load_world_state()
    return f"👤 [User Context]: {json.dumps(state.get('user', {}), indent=2)}"


async def get_environment_state() -> str:
    """Returns ambient temperature, lighting scene, and physical environment state."""
    state = _load_world_state()
    return f"🌡️ [Environment State]: {json.dumps(state.get('environment', {}), indent=2)}"


async def get_device_state() -> str:
    """Returns connected microcontrollers, sensors, actuators, and serial links."""
    state = _load_world_state()
    return f"🔌 [Hardware & Device Bus]: {json.dumps(state.get('hardware_bus', {}), indent=2)}"


async def get_active_tasks() -> str:
    """Returns currently running background subagents and active mission milestones."""
    try:
        from friday_tools.subagents import list_subagents
        from friday_tools.jarvis_mission import get_mission_status
        sub_str = await list_subagents()
        mis_str = await get_mission_status()
        return f"📋 [ACTIVE TASKS & PIPELINES]:\n\n{mis_str}\n\n{sub_str}"
    except Exception as e:
        return f"[ERROR] Failed to fetch active tasks: {e}"


async def get_current_goal() -> str:
    """Returns the primary high-level strategic goal ULTRON is currently executing."""
    state = _load_world_state()
    mis = state.get("active_mission", {})
    return f"🎯 [Current Strategic Goal]: {mis.get('title', 'Idle')} ({mis.get('progress_percent', 0)}% Complete) -> {mis.get('current_step', 'Ready')}"
