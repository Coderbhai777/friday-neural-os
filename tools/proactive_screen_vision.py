# -*- coding: utf-8 -*-
"""
JARVIS Autonomous Proactive Screen Vision Perception Engine
Unified with ULTRON Ω Central Companion Orchestration Bridge:
- Continuous presence monitoring & user idle tracking via GetLastInputInfo
- High-speed desktop frame acquisition (<50ms, scaled to 640px JPEG)
- Unified delegation to ULTRON Ω Event-Driven Bridge (Zero competing background threads)
- Instant barge-in interruption when user speaks or interacts
"""

import os
import io
import time
import ctypes
from pathlib import Path
from ctypes import wintypes
from PIL import Image, ImageGrab
from dotenv import load_dotenv

# Ensure environment variables are loaded
for env_p in [
    Path.home() / "Documents" / "JARVIS_Data" / ".env",
    Path.home() / "Documents" / "ULTRON_Data" / ".env",
    Path.home() / ".env",
]:
    if env_p.exists():
        load_dotenv(env_p)

user32 = ctypes.windll.user32


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def get_system_idle_seconds() -> float:
    """Returns number of seconds since last keyboard or mouse input."""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return max(0.0, millis / 1000.0)
    return 0.0


def get_active_window_info() -> dict:
    """Returns the title, hwnd, and process of the foreground window."""
    try:
        from tools.ultron_vision_pipeline import get_active_window_info as _gaw
        return _gaw()
    except Exception:
        try:
            from friday_tools.ultron_vision_pipeline import get_active_window_info as _gaw
            return _gaw()
        except Exception:
            pass

    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {"title": "Desktop", "app": "explorer.exe", "hwnd": 0}

    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value or "Desktop"

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

    app_name = "application"
    try:
        import psutil
        proc = psutil.Process(pid.value)
        app_name = proc.name()
    except Exception:
        pass

    return {"title": title, "app": app_name, "hwnd": hwnd}


def capture_screen_jpeg(max_dim: int = 640, quality: int = 75) -> bytes:
    """Captures the primary monitor and downscales to max_dim JPEG bytes."""
    try:
        from tools.ultron_vision_pipeline import capture_screen_direct
        img = capture_screen_direct(max_dim=max_dim)
        if img:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            return buf.getvalue()
    except Exception:
        pass

    screen = None
    try:
        screen = ImageGrab.grab(all_screens=False)
    except Exception:
        try:
            import pyautogui
            screen = pyautogui.screenshot()
        except Exception:
            screen = Image.new("RGB", (640, 360), color=(15, 23, 42))

    orig_w, orig_h = screen.size
    scale = min(max_dim / float(orig_w), max_dim / float(orig_h), 1.0)
    new_w = max(1, int(orig_w * scale))
    new_h = max(1, int(orig_h * scale))

    if scale < 1.0:
        frame = screen.resize((new_w, new_h), Image.Resampling.BILINEAR)
    else:
        frame = screen

    if frame.mode in ("RGBA", "P"):
        frame = frame.convert("RGB")

    buf = io.BytesIO()
    frame.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


try:
    from tools.ultron_companion_bridge import (
        _COMPANION,
        start_ultron_companion,
        stop_ultron_companion,
        force_screen_perception
    )
except ImportError:
    from friday_tools.ultron_companion_bridge import (
        _COMPANION,
        start_ultron_companion,
        stop_ultron_companion,
        force_screen_perception
    )


class ProactiveVisionEngine:
    """
    Unified ProactiveVisionEngine wrapper delegating to ULTRON Ω Companion Bridge.
    Prevents duplicate threads and competing vision inference.
    """

    def __init__(self):
        pass

    @property
    def running(self) -> bool:
        return _COMPANION.running

    def start(self):
        _COMPANION.start()

    def stop(self):
        _COMPANION.stop()

    def notify_user_interaction(self):
        _COMPANION.notify_user_spoke()

    def inspect_and_contribute(self) -> str:
        analysis = _COMPANION.inspect_screen_now()
        return analysis.get("suggested_observation", "")


# Global singleton instance
_ENGINE = ProactiveVisionEngine()


# Tool interfaces
async def start_proactive_vision() -> str:
    """Starts JARVIS's continuous autonomous screen perception and commentary."""
    _ENGINE.start()
    return "JARVIS Proactive Screen Vision Perception is now ACTIVE via the unified ULTRON Ω Engine."


async def stop_proactive_vision() -> str:
    """Stops the autonomous background screen vision monitor."""
    _ENGINE.stop()
    return "JARVIS Proactive Screen Vision has been paused, Sir."


async def force_proactive_vision_inspection() -> str:
    """Forces an immediate visual inspection of your screen and returns JARVIS's observation."""
    return await force_screen_perception()


def notify_interaction():
    """Notify the vision engine that user interacted to defer commentary."""
    _ENGINE.notify_user_interaction()
