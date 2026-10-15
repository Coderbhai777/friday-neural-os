"""
ULTRON Universal Music & Spotify Controller (Adapted from ULTRON-Echo)
Enables reliable Spotify track searching, desktop playback, global media keys (Play, Pause, Next, Prev),
and system audio controls.
"""

import os
import time
import asyncio
import subprocess
import urllib.parse
from typing import Optional

def _send_media_key(key_action: str) -> str:
    """Sends Windows global media key event via PowerShell / SafeController."""
    try:
        from pynput.keyboard import Key, Controller
        kb = Controller()
        if key_action in ("play", "pause", "toggle"):
            kb.press(Key.media_play_pause)
            kb.release(Key.media_play_pause)
            return "[OK] Toggled media Play/Pause."
        elif key_action == "next":
            kb.press(Key.media_next)
            kb.release(Key.media_next)
            return "[OK] Skipped to next track."
        elif key_action in ("prev", "previous"):
            kb.press(Key.media_previous)
            kb.release(Key.media_previous)
            return "[OK] Returned to previous track."
        elif key_action == "volume_up":
            kb.press(Key.media_volume_up)
            kb.release(Key.media_volume_up)
            return "[OK] Volume increased."
        elif key_action == "volume_down":
            kb.press(Key.media_volume_down)
            kb.release(Key.media_volume_down)
            return "[OK] Volume decreased."
        elif key_action == "mute":
            kb.press(Key.media_volume_mute)
            kb.release(Key.media_volume_mute)
            return "[OK] Audio muted/unmuted."
    except Exception:
        pass

    # Fallback to PowerShell
    key_codes = {
        "play": 0xB3, "pause": 0xB3, "toggle": 0xB3,
        "next": 0xB0, "previous": 0xB1, "prev": 0xB1,
        "volume_up": 0xAF, "volume_down": 0xAE, "mute": 0xAD
    }
    code = key_codes.get(key_action.lower(), 0xB3)
    ps_cmd = f'$w = Add-Type -MemberDefinition \'[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);\' -Name "K" -PassThru; $w::keybd_event({code}, 0, 0, 0); $w::keybd_event({code}, 0, 2, 0);'
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=5)
        return f"[OK] Media action '{key_action}' dispatched."
    except Exception as e:
        return f"[ERROR] Media dispatch failed: {e}"


async def play_song_on_spotify(song_title: str) -> str:
    """
    Searches and plays any song, artist, or album on Spotify via desktop app or browser link.
    """
    encoded = urllib.parse.quote(song_title)
    # 1. Try launching Spotify desktop app URI
    try:
        os.startfile(f"spotify:search:{encoded}")
        time.sleep(2)
        _send_media_key("play")
        return f"[OK] Launched Spotify search for '{song_title}'."
    except Exception:
        pass

    # 2. Fallback to Spotify Web
    import webbrowser
    webbrowser.open(f"https://open.spotify.com/search/{encoded}")
    return f"[OK] Opened Spotify Web search for '{song_title}'."


async def spotify_control(action: str, query: str = "") -> str:
    """
    Controls Spotify & System media playback:
    Actions: 'play', 'pause', 'toggle', 'next', 'previous', 'volume_up', 'volume_down', 'mute', 'search_play'
    """
    act = action.lower().strip()
    if act in ("search_play", "search", "play_song"):
        if not query:
            return "[ERROR] Please provide the song or artist query to play."
        return await play_song_on_spotify(query)

    return await asyncio.to_thread(_send_media_key, act)
