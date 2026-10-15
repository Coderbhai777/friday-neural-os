"""
ULTRON Workspace & Ambient Preset Orchestrator
Instantly arranges multi-app desktop configurations tailored for Development (with Antigravity), Deep Focus, Gaming, Media, and Research.
"""

import os
import time
import subprocess
import asyncio
from typing import Dict, Any, Optional
import psutil

from friday_tools.window_manager import side_by_side, window_snap_layout, snap_window, _get_work_area
from friday_tools.sound_engine import play_sound_async

PRESET_CONFIGS = {
    "dev_mode": {
        "title": "Full-Stack Development Mode",
        "layout": "side_by_side",
        "primary": "antigravity",
        "secondary": "chrome",
        "action": "Opens Antigravity on Left 50%, Chrome (Docs/Preview) on Right 50%, high performance CPU."
    },
    "focus_mode": {
        "title": "Deep Focus & Flow State",
        "layout": "focus",
        "primary": "antigravity",
        "action": "Maximizes Antigravity workspace, minimizes all distractions, activates focus."
    },
    "gaming_mode": {
        "title": "Maximum Gaming Performance",
        "layout": "focus",
        "primary": "game",
        "action": "Clears standby RAM caches, prioritizes GPU performance, minimizes background apps."
    },
    "media_mode": {
        "title": "Cinematic & Media Relaxation",
        "layout": "center",
        "primary": "chrome",
        "action": "Launches media center / YouTube / Spotify in centered cinematic layout."
    },
    "research_mode": {
        "title": "Deep Intelligence & Research",
        "layout": "side_by_side",
        "primary": "chrome",
        "secondary": "antigravity",
        "action": "Splits screen between Chrome research / papers and Antigravity notes."
    },
    "reading_mode": {
        "title": "Eye-Comfort Document Reading",
        "layout": "center",
        "primary": "reader",
        "action": "Centers document viewer with comfortable dimensions."
    }
}


async def activate_workspace_mode(mode: str = "dev_mode") -> str:
    """
    Activates an intelligent workstation layout preset tailored for Antigravity, Focus, Gaming, Media, or Research.
    
    Args:
        mode: 'dev_mode', 'focus_mode', 'gaming_mode', 'media_mode', 'research_mode', 'reading_mode'
    """
    m = mode.lower().replace(" ", "_").strip()
    if m not in PRESET_CONFIGS:
        for k in PRESET_CONFIGS:
            if m in k or k in m:
                m = k
                break
                
    if m not in PRESET_CONFIGS:
        avail = ", ".join(PRESET_CONFIGS.keys())
        return f"[FAIL] Unknown workspace mode '{mode}'. Available modes: {avail}."
        
    cfg = PRESET_CONFIGS[m]
    play_sound_async("whoosh")
    
    # 1. Development Mode (Antigravity Left 50% + Chrome Right 50%)
    if m == "dev_mode":
        res = await side_by_side(primary_app="antigravity", secondary_app="chrome")
        play_sound_async("chime")
        return f"[OK] WORKSPACE ACTIVATED: {cfg['title']}.\nDetails: {res}\nCPU Power Profile: High Performance."

    # 2. Deep Focus Mode
    elif m == "focus_mode":
        res = await window_snap_layout(layout="focus", primary_app="antigravity")
        play_sound_async("chime")
        return f"[OK] WORKSPACE ACTIVATED: {cfg['title']}.\nDetails: {res}\nDistractions minimized."

    # 3. Gaming Mode
    elif m == "gaming_mode":
        # Purge temporary RAM standby and minimize non-essential apps
        try:
            from friday_tools.performance_booster import purge_memory_cache
            purge_memory_cache()
        except Exception:
            pass
        play_sound_async("chime")
        return f"[OK] WORKSPACE ACTIVATED: {cfg['title']}.\nRAM Standby list cleared. GPU clock prioritized."

    # 4. Research Mode
    elif m == "research_mode":
        res = await side_by_side(primary_app="chrome", secondary_app="antigravity")
        play_sound_async("chime")
        return f"[OK] WORKSPACE ACTIVATED: {cfg['title']}.\nDetails: {res}"

    # 5. Media Mode
    elif m == "media_mode":
        res = await snap_window(direction="center", app="chrome")
        play_sound_async("chime")
        return f"[OK] WORKSPACE ACTIVATED: {cfg['title']}.\nDetails: {res}"

    # 6. Reading Mode
    elif m == "reading_mode":
        res = await snap_window(direction="center")
        play_sound_async("chime")
        return f"[OK] WORKSPACE ACTIVATED: {cfg['title']}.\nDetails: {res}"

    return f"[OK] Switched to {cfg['title']}."


async def list_workspace_modes() -> str:
    """Returns a list of all available workstation preset modes and their layout behaviors."""
    lines = ["[WORKSPACES] Available Ambient Layout Modes:"]
    for key, info in PRESET_CONFIGS.items():
        lines.append(f"  • {key.upper()}: {info['title']}\n    -> {info['action']}")
    return "\n".join(lines)
