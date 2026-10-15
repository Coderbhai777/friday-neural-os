"""
ULTRON HUD & Desktop Overlay Engine
Controls the floating Dynamic Island telemetry pill and desktop HUD state.
"""

import sys
import asyncio
from typing import Optional

from friday_tools.sound_engine import play_sound_async


async def toggle_dynamic_island(visible: bool = True) -> str:
    """
    Toggles the floating, frameless Dynamic Island telemetry pill on the top of the monitor.
    
    Args:
        visible: True to display the floating HUD pill, False to hide.
    """
    try:
        from aria_modules.dynamic_island import launch_dynamic_island, _ISLAND_INSTANCE
        inst = _ISLAND_INSTANCE or launch_dynamic_island()
        if inst:
            if visible:
                inst.show()
                play_sound_async("chime")
                return "[OK] Floating Desktop Dynamic Island is now ONLINE and visible."
            else:
                inst.hide()
                return "[OK] Floating Desktop Dynamic Island hidden."
        return "[INFO] Dynamic Island initialized."
    except Exception as e:
        return f"[FAIL] Could not toggle Dynamic Island: {e}"
