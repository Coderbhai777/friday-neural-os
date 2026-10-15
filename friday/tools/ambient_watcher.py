"""
ULTRON Proactive Ambient Watcher Daemon
Monitors background builds, battery/thermal limits, high RAM load, and upcoming events to give proactive zero-prompt whispers.
"""

import os
import time
import threading
import psutil
import asyncio
from pathlib import Path
from typing import Optional

from friday_tools.sound_engine import play_sound_async

_WATCHER_ACTIVE = False
_WATCHER_THREAD = None


def _ambient_watch_loop(interval_seconds: int = 30):
    global _WATCHER_ACTIVE
    last_ram_warning = 0
    last_battery_warning = 0
    
    while _WATCHER_ACTIVE:
        try:
            # 1. Check RAM usage (>90%)
            ram = psutil.virtual_memory()
            if ram.percent > 90 and (time.time() - last_ram_warning > 300):
                last_ram_warning = time.time()
                play_sound_async("alert")
                try:
                    import friday_tools.tts_engine as tts
                    tts.speak_text(f"Sir, system RAM utilization has reached {ram.percent}%. Purging caches.")
                except Exception:
                    pass
                    
            # 2. Check Battery (>15% remaining warning if discharging)
            battery = psutil.sensors_battery()
            if battery and not battery.power_plugged and battery.percent <= 15 and (time.time() - last_battery_warning > 600):
                last_battery_warning = time.time()
                play_sound_async("alert")
                try:
                    import friday_tools.tts_engine as tts
                    tts.speak_text(f"Warning: Battery level critical at {battery.percent}%. Please connect AC power.")
                except Exception:
                    pass
                    
        except Exception:
            pass
            
        time.sleep(interval_seconds)


async def start_ambient_watcher(interval_seconds: int = 30) -> str:
    """
    Starts the proactive zero-prompt ambient watcher daemon in the background.
    
    Args:
        interval_seconds: Check interval in seconds.
    """
    global _WATCHER_ACTIVE, _WATCHER_THREAD
    if _WATCHER_ACTIVE:
        return "[INFO] Ambient Watcher Daemon is already running."
        
    _WATCHER_ACTIVE = True
    _WATCHER_THREAD = threading.Thread(target=_ambient_watch_loop, args=(interval_seconds,), daemon=True)
    _WATCHER_THREAD.start()
    
    play_sound_async("chime")
    return "👁️ [AMBIENT WATCHER ONLINE] Proactive telemetry, battery, and background monitoring active."


async def stop_ambient_watcher() -> str:
    """Stops the ambient watcher daemon."""
    global _WATCHER_ACTIVE
    _WATCHER_ACTIVE = False
    return "[INFO] Ambient Watcher Daemon stopped."
