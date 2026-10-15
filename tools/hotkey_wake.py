"""
Ultron Global Hotkey Wake Engine
Listens for: Ctrl + Shift + Alt + U
Brings Ultron to the front, unhides window, and wakes the assistant.
"""

import ctypes
import threading
import time
from ctypes import wintypes

user32 = ctypes.windll.user32

# Modifier constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

# Virtual Keys
VK_U = 0x55
VK_A = 0x41
HOTKEY_ID_ULTRON_WAKE = 9001

_wake_callbacks = []
_listener_thread = None
_running = False


def register_wake_callback(cb):
    """Registers a function to call when Ctrl+Shift+Alt+U is pressed."""
    _wake_callbacks.append(cb)


def _hotkey_loop():
    global _running
    # Register Ctrl + Shift + Alt + U
    modifiers = MOD_CONTROL | MOD_SHIFT | MOD_ALT | MOD_NOREPEAT
    if not user32.RegisterHotKey(None, HOTKEY_ID_ULTRON_WAKE, modifiers, VK_U):
        print(f"[ULTRON] Hotkey Ctrl+Shift+Alt+U register failed (Error {ctypes.GetLastError()})")
        return

    print("[ULTRON] Global Wake Hotkey Active: Ctrl + Shift + Alt + U [OK]")
    _running = True

    try:
        msg = wintypes.MSG()
        while _running:
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1): # PM_REMOVE = 1
                if msg.message == 0x0312: # WM_HOTKEY
                    if msg.wParam == HOTKEY_ID_ULTRON_WAKE:
                        print("\n⚡ [HOTKEY TRIGGERED] Ctrl+Shift+Alt+U -> Waking Ultron!")
                        for cb in _wake_callbacks:
                            try:
                                cb()
                            except Exception as e:
                                print(f"[ULTRON] Wake callback error: {e}")
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.05)
    finally:
        user32.UnregisterHotKey(None, HOTKEY_ID_ULTRON_WAKE)


def start_wake_listener():
    """Starts the background hotkey listener thread."""
    global _listener_thread
    if _listener_thread is None or not _listener_thread.is_alive():
        _listener_thread = threading.Thread(target=_hotkey_loop, daemon=True, name="UltronWakeHotkeyThread")
        _listener_thread.start()


# Auto-start on module import
start_wake_listener()
