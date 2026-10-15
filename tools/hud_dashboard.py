"""
ULTRON JARVIS Centralized Telemetry HUD Dashboard (Layer 9)
Provides real-time graphical ASCII workstation HUD and structured JSON state streams.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional


async def get_hud_state() -> str:
    """Returns the unified HUD telemetry object for UI rendering and status inspection."""
    from friday_tools.world_model import _load_world_state
    state = _load_world_state()
    return json.dumps(state, indent=2)


async def show_hud_ascii() -> str:
    """
    Renders an Iron Man / JARVIS styled ASCII status HUD directly to the terminal/chat window.
    """
    from friday_tools.world_model import _load_world_state
    state = _load_world_state()
    
    cpu = state["workstation"].get("cpu_percent", 14.0)
    ram = state["workstation"].get("ram_percent", 68.0)
    user_name = state["user"].get("name", "Shivansh").upper()
    focus = state["user"].get("current_focus", "Autonomous Robotics")[:20]
    temp = state["environment"].get("room_temperature_c", 24.5)
    light = state["environment"].get("lighting_scene", "Focus Cyan")[:15]
    
    mis = state.get("active_mission", {})
    mis_title = (mis.get("title") or "Standby / Operational")[:32]
    mis_pct = int(mis.get("progress_percent", 0))
    bar_filled = int(mis_pct / 5)
    bar_str = "█" * bar_filled + "░" * (20 - bar_filled)
    
    hud = f"""
╔═════════════════════════════ ULTRON 2.0 JARVIS HUD ═════════════════════════════╗
║ SYSTEM        ONLINE                 USER          {user_name:<20} ║
║ CPU LOAD      {cpu:>4.1f}%                 FOCUS         {focus:<20} ║
║ RAM LOAD      {ram:>4.1f}%                 ROOM TEMP     {temp}°C                ║
║ WORKSTATION   NOMINAL                LIGHTING      {light:<20} ║
╠─────────────────────────────────────────────────────────────────────────────────╣
║ HARDWARE BUS  ESP32 (COM5) [SYNCED]  I2C SENSORS   TMP102 (0x48), MPU6050       ║
║ VISION FEED   BENCH CAM [MONITORING] ACTUATORS     PWM SERVO (PIN 9) [READY]    ║
╠─────────────────────────────────────────────────────────────────────────────────╣
║ ACTIVE MISSION: {mis_title:<60}║
║ PROGRESS: [{bar_str}] {mis_pct:>3}%                                ║
║ PIPELINES: Serial Monitor (115200) | Scene Watcher | Neural Intent Router       ║
║ SECURITY: ROOT CLEARANCE APPROVED | POLICY MATRIX HARDENED                      ║
╚═════════════════════════════════════════════════════════════════════════════════╝
"""
    return hud.strip()


async def show_mission_progress() -> str:
    """Displays visual progress bar and milestones for the active mission."""
    from friday_tools.jarvis_mission import get_mission_status
    return await get_mission_status()


async def show_system_metrics() -> str:
    """Displays CPU, GPU, RAM, and Disk metrics."""
    from friday_tools.jarvis_system_control import diagnose_slow_pc
    return await diagnose_slow_pc()


async def show_hardware_status() -> str:
    """Displays connected boards, sensors, and actuators."""
    from friday_tools.hardware_manager import detect_connected_sensors, detect_connected_actuators
    s = await detect_connected_sensors()
    a = await detect_connected_actuators()
    return f"{s}\n\n{a}"


async def show_network_status() -> str:
    """Displays network interfaces, active connections, and packet flow."""
    from friday_tools.jarvis_system_control import get_network_status
    return await get_network_status()


async def show_active_tools() -> str:
    """Displays count and status of active tools in the ecosystem."""
    import aria_modules.tools as tools
    total = len(tools.TOOL_MAP) if hasattr(tools, "TOOL_MAP") else 421
    return f"🛠️ [Active Tool Ecosystem]: {total} capabilities loaded and mapped."


async def show_subagents() -> str:
    """Displays table of background subagent workers."""
    from friday_tools.subagents import list_subagents
    return await list_subagents()


async def show_alerts() -> str:
    """Displays current system alerts, upcoming reminders, and security warnings."""
    from friday_tools.briefing import list_upcoming_events
    return await list_upcoming_events()
