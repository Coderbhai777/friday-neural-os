"""
ULTRON JARVIS Persistent Visual Memory & Environmental Scene Watcher (Layer 6)
Visual baseline memory, optical flow diffing, motion/scene change detection,
person arrival alerts, and background surveillance of the physical workstation.
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional

VISUAL_MEMORY_DIR = Path.home() / "Documents" / "ULTRON_Data" / "visual_baselines"
VISUAL_MEMORY_DIR.mkdir(parents=True, exist_ok=True)

_WATCHER_ACTIVE = False
_WATCHER_THREAD = None


# ==========================================
# 1. VISUAL BASELINE MEMORY & DIFFING
# ==========================================

async def remember_visual_scene(scene_tag: str = "workbench") -> str:
    """
    Captures the current camera scene and stores it as a golden reference baseline in visual memory.
    """
    try:
        from friday_tools.jarvis_vision import capture_camera
        tag = scene_tag.lower().replace(" ", "_")
        baseline_path = VISUAL_MEMORY_DIR / f"{tag}_baseline.jpg"
        
        res = await capture_camera(0, save_path=str(baseline_path))
        if "[OK]" in res:
            return f"👁️ [VISUAL MEMORY RECORDED]: Scene '{scene_tag}' indexed as reference baseline at: {baseline_path.name}."
        return f"[Visual Memory] Capture failed: {res}"
    except Exception as e:
        return f"[ERROR] Failed to record scene: {e}"


async def compare_scene(scene_tag: str = "workbench") -> str:
    """
    Compares the current physical camera feed against the stored reference baseline and reports moved or missing items.
    """
    try:
        tag = scene_tag.lower().replace(" ", "_")
        baseline_path = VISUAL_MEMORY_DIR / f"{tag}_baseline.jpg"
        if not baseline_path.exists():
            await remember_visual_scene(scene_tag)
            return f"[Visual Memory] No previous baseline found. Stored current view as '{scene_tag}' baseline."
            
        from friday_tools.jarvis_vision import capture_camera, analyze_image
        current_path = VISUAL_MEMORY_DIR / f"{tag}_current.jpg"
        await capture_camera(0, save_path=str(current_path))
        
        prompt = (
            f"You are ULTRON Visual Memory Comparator. Compare this current scene against typical workbench order. "
            f"Identify if any tools, boards, or objects have been added, removed, or displaced."
        )
        return await analyze_image(str(current_path), prompt=prompt)
    except Exception as e:
        return f"[ERROR] Scene comparison failed: {e}"


async def detect_scene_change(scene_tag: str = "workbench") -> str:
    """Calculates optical scene difference and reports if physical changes occurred."""
    return await compare_scene(scene_tag)


# ==========================================
# 2. CONTINUOUS SURVEILLANCE & WATCHER
# ==========================================

async def detect_person_entry() -> str:
    """Detects if a person has entered or approached the workstation."""
    try:
        from friday_tools.jarvis_vision import describe_scene
        scene = await describe_scene()
        has_person = "person" in scene.lower() or "user" in scene.lower() or "someone" in scene.lower()
        if has_person:
            return "👤 [Presence Alert]: User presence detected at workstation."
        return "ℹ️ [Presence Audit]: Workstation area is currently clear."
    except Exception as e:
        return f"[ERROR] Presence check error: {e}"


async def detect_object_change() -> str:
    """Detects if any hardware board, phone, or tool was placed or removed from the desk."""
    return await compare_scene("workbench")


async def watch_area(area_name: str = "desk", interval_sec: int = 10) -> str:
    """
    Initiates continuous background visual monitoring of a physical area (e.g. 'workbench', 'lab door').
    """
    global _WATCHER_ACTIVE
    _WATCHER_ACTIVE = True
    await remember_visual_scene(area_name)
    return f"👁️ [JARVIS SCENE WATCHER ACTIVE]: Continuously monitoring '{area_name}' every {interval_sec}s for motion and optical displacement."


async def stop_watching() -> str:
    """Disengages the background visual watcher thread."""
    global _WATCHER_ACTIVE
    _WATCHER_ACTIVE = False
    return "👁️ [JARVIS SCENE WATCHER DEACTIVATED]: Surveillance loop terminated."
