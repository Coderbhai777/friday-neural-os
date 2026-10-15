# -*- coding: utf-8 -*-
"""
JARVIS / ULTRON Ambient Screen Sentinel & Proactive AGI Co-Pilot
Unified with ULTRON Ω Central Companion Orchestration Bridge:
- Silence-by-default architecture
- Event-driven roadblock and crash interception
- Zero duplicate or competing background polling loops
- Single-owner Charon neural TTS playback
"""

import sys
import ctypes
from typing import Optional, Dict, Any

try:
    from tools.ultron_companion_bridge import (
        _COMPANION,
        start_ultron_companion,
        stop_ultron_companion,
        force_screen_perception
    )
    from tools.ultron_vision_pipeline import (
        capture_screen_direct,
        get_active_window_info
    )
except ImportError:
    from friday_tools.ultron_companion_bridge import (
        _COMPANION,
        start_ultron_companion,
        stop_ultron_companion,
        force_screen_perception
    )
    from friday_tools.ultron_vision_pipeline import (
        capture_screen_direct,
        get_active_window_info
    )


def _get_active_window_title() -> str:
    """Gets the title of the currently focused foreground window on Windows."""
    info = get_active_window_info()
    return info.get("title", "")


def _capture_screen_fast() -> Optional[bytes]:
    """Captures the current desktop screen via Win32 GDI with Desktop attachment."""
    img = capture_screen_direct(max_dim=768)
    if img:
        import io
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        return buf.getvalue()
    return None


async def start_screen_sentinel(interval_seconds: float = 4.0) -> str:
    """
    Activates ULTRON's continuous ambient screen perception (AGI Co-Pilot Mode).
    Delegates directly to the unified event-driven ULTRON Ω Companion Bridge.
    """
    msg = await start_ultron_companion()
    return (
        "[AGI Screen Sentinel Online - Unified Engine]\n"
        f"{msg}\n"
        "Competing background loops deactivated. Silence-by-default and Charon neural TTS active."
    )


async def stop_screen_sentinel() -> str:
    """
    Deactivates continuous ambient screen perception.
    """
    return await stop_ultron_companion()


async def get_screen_sentinel_status() -> str:
    """
    Returns the real-time status of the unified AGI Screen Sentinel.
    """
    status = "ACTIVE (Silence-by-Default Observer)" if _COMPANION.running else "IDLE / STOPPED"
    return (
        f"**AGI Screen Sentinel Status:** {status}\n"
        f"• Engine: ULTRON Ω Event-Driven Companion Bridge\n"
        f"• Mode: Roadblock & Crash Interception Only (Zero Unsolicited Polling)"
    )
