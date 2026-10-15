"""
ULTRON Window & Desktop Workspace Manager
Provides granular control over open Windows applications, focus modes, window snapping layouts, and regional screen captures.
"""

import os
import sys
import time
import subprocess
import ctypes
from ctypes import wintypes
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import psutil

user32 = ctypes.windll.user32

# Desktop & Window Station Access
WINSTA_ALL_ACCESS = 0x37F
DESKTOP_ALL_ACCESS = 0x1FF

def _attach_desktop():
    try:
        hWinSta = user32.OpenWindowStationW("WinSta0", False, WINSTA_ALL_ACCESS)
        if hWinSta:
            user32.SetProcessWindowStation(hWinSta)
        hDesk = user32.OpenDesktopW("default", 0, False, DESKTOP_ALL_ACCESS)
        if hDesk:
            user32.SetThreadDesktop(hDesk)
        return hDesk
    except Exception:
        return None

# Win32 Structures and Constants
class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

SPI_GETWORKAREA = 0x0030
SWP_SHOWWINDOW = 0x0040
SWP_FRAMECHANGED = 0x0020
SWP_NOACTIVATE = 0x0010
HWND_TOP = 0
SW_RESTORE = 9
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_SHOW = 5
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
WM_CLOSE = 0x0010
WM_SYSCOMMAND = 0x0112
SC_CLOSE = 0xF060

# Configure Win32 Function Signatures for 64-bit safety
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

try:
    user32.EnumDesktopWindows.argtypes = [wintypes.HDESK, WNDENUMPROC, wintypes.LPARAM]
    user32.EnumDesktopWindows.restype = wintypes.BOOL

    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL

    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int

    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int

    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD

    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL

    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user32.SetWindowPos.restype = wintypes.BOOL

    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL

    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.PostMessageW.restype = wintypes.BOOL
except Exception:
    pass

KNOWN_APP_ALIASES = {
    "vscode": ["code.exe", "code"],
    "vs code": ["code.exe", "code"],
    "visual studio code": ["code.exe", "code"],
    "antigravity": ["antigravity.exe", "antigravity"],
    "chrome": ["chrome.exe", "google chrome"],
    "google chrome": ["chrome.exe", "google chrome"],
    "chatgpt": ["chatgpt", "chatgpt.exe", "chrome.exe", "msedge.exe"],
    "edge": ["msedge.exe", "microsoft edge"],
    "browser": ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"],
    "terminal": ["windowsterminal.exe", "cmd.exe", "powershell.exe", "conhost.exe"],
    "powershell": ["powershell.exe"],
    "cmd": ["cmd.exe", "conhost.exe"],
    "notepad": ["notepad.exe", "notepad"],
    "explorer": ["explorer.exe", "file explorer"]
}

KNOWN_APP_LAUNCH_PATHS = {
    "antigravity": r"C:\Users\shiva\AppData\Local\Programs\antigravity\Antigravity.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    "code": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "notepad": "notepad.exe",
    "terminal": "wt.exe",
    "cmd": "cmd.exe"
}

def _get_work_area() -> tuple:
    """Returns (x, y, width, height) of the primary desktop usable work area."""
    rect = RECT()
    user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    x = rect.left
    y = rect.top
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w <= 0 or h <= 0:
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        x, y = 0, 0
    return x, y, w, h

def _get_all_visible_windows() -> List[Dict[str, Any]]:
    """Returns all open, interactive application windows on the desktop."""
    hDesk = _attach_desktop()
    results = []
    
    def win_proc(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
            
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
            
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip()
        if not title:
            return True
            
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if (ex_style & WS_EX_TOOLWINDOW) and not (ex_style & WS_EX_APPWINDOW):
            return True
            
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        pname = ""
        try:
            pname = psutil.Process(pid.value).name()
        except Exception:
            pass
            
        # Ignore system background helper shells
        ignore_titles = [
            "Program Manager", "Settings", "Windows Input Experience", 
            "DesktopWindowXamlSource", "Task Switching", "PopupHost", 
            "MS_WebcheckMonitor", "BluetoothNotificationAreaIconWindowClass",
            "MiracastConnectionWindow", "DDE Server Window", "GDI+ Window (Explorer.EXE)"
        ]
        if title in ignore_titles:
            return True
            
        results.append({
            "hwnd": hwnd,
            "title": title,
            "process": pname,
            "pid": pid.value
        })
        return True

    cb = WNDENUMPROC(win_proc)
    user32.EnumDesktopWindows(hDesk, cb, 0)
    return results

def _find_window(query: str, windows: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """Finds matching window dictionary given a query string or process name."""
    if not query:
        return None
    if windows is None:
        windows = _get_all_visible_windows()
        
    q = query.lower().strip()
    
    # Check active/foreground
    if q in ("active", "foreground", "current", "this"):
        fg_hwnd = user32.GetForegroundWindow()
        for w in windows:
            if w["hwnd"] == fg_hwnd:
                return w
        if windows:
            return windows[0]
            
    # Check process exact/contains
    for w in windows:
        p_clean = w["process"].lower().replace(".exe", "")
        if q == p_clean or q in w["process"].lower() or p_clean in q:
            return w
            
    # Check title contains
    for w in windows:
        if q in w["title"].lower():
            return w
            
    # Check aliases
    for alias_key, alias_vals in KNOWN_APP_ALIASES.items():
        if alias_key in q or q in alias_key:
            for val in alias_vals:
                for w in windows:
                    if val in w["process"].lower() or val in w["title"].lower():
                        return w
                        
    return None

def _launch_app_if_needed(app_name: str) -> None:
    """Launches an application if it's not currently running and waits briefly for the window to appear."""
    q = app_name.lower().strip()
    
    # Check specific paths first for Chrome
    if "chrome" in q:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe")
        ]
        for cp in chrome_paths:
            if os.path.exists(cp):
                try:
                    subprocess.Popen([cp, "https://www.google.com"])
                    time.sleep(1.2)
                    return
                except Exception:
                    pass

    for key, path in KNOWN_APP_LAUNCH_PATHS.items():
        if key in q or q in key:
            try:
                if os.path.exists(path):
                    subprocess.Popen([path])
                else:
                    os.system(f'start "" "{key}"')
                time.sleep(1.0)
                return
            except Exception:
                pass
    try:
        os.system(f'start "" "{q}"')
        time.sleep(1.0)
    except Exception:
        pass

def _position_window(hwnd: int, x: int, y: int, width: int, height: int) -> None:
    """Positions and restores a window into specific coordinates."""
    if not hwnd:
        return
    user32.ShowWindow(hwnd, SW_RESTORE)
    time.sleep(0.04)
    user32.SetWindowPos(hwnd, HWND_TOP, int(x), int(y), int(width), int(height), SWP_SHOWWINDOW | SWP_FRAMECHANGED)
    time.sleep(0.04)
    # Bring to foreground safely without locking ALT
    try:
        user32.keybd_event(0x12, 0, 0, 0)
        user32.SetForegroundWindow(hwnd)
        user32.keybd_event(0x12, 0, 2, 0)
    except Exception:
        pass

# =========================================================================
# PUBLIC ASYNC TOOLS
# =========================================================================

async def side_by_side(primary_app: str = "antigravity", secondary_app: str = "chrome") -> str:
    """
    Arranges two applications side-by-side on the screen (50% left, 50% right).
    
    Args:
        primary_app: Left application name/window title (e.g. 'antigravity', 'code', 'chrome').
        secondary_app: Right application name/window title (e.g. 'chrome', 'edge', 'terminal').
    """
    return await window_snap_layout(layout="side_by_side", primary_app=primary_app, secondary_app=secondary_app)

async def window_snap_layout(layout: str = "side_by_side", primary_app: str = "antigravity", secondary_app: str = "chrome") -> str:
    """
    Arranges open application windows into predefined workstation layouts.
    
    Args:
        layout: Preset: 'side_by_side' (50/50 split), 'focus' (primary maximized, others minimized), 
                'grid' (4 quadrants), or 'code_and_browser'.
        primary_app: Substring title/process of the main application.
        secondary_app: Substring title/process of secondary application.
    """
    def _execute():
        wa_x, wa_y, wa_w, wa_h = _get_work_area()
        wins = _get_all_visible_windows()
        
        layout_clean = layout.lower().strip()
        
        if layout_clean in ("side_by_side", "code_and_browser", "split", "50/50", "side-by-side"):
            p_win = _find_window(primary_app, wins)
            if not p_win:
                _launch_app_if_needed(primary_app)
                wins = _get_all_visible_windows()
                p_win = _find_window(primary_app, wins)
                
            s_win = _find_window(secondary_app, wins)
            if not s_win:
                _launch_app_if_needed(secondary_app)
                wins = _get_all_visible_windows()
                s_win = _find_window(secondary_app, wins)
                
            if not p_win and len(wins) > 0:
                p_win = wins[0]
            if not s_win and len(wins) > 1:
                s_win = wins[1] if wins[1]["hwnd"] != (p_win["hwnd"] if p_win else 0) else (wins[0] if len(wins) > 0 else None)
                
            half_w = wa_w // 2
            p_title = primary_app
            s_title = secondary_app
            
            if p_win:
                _position_window(p_win["hwnd"], wa_x, wa_y, half_w, wa_h)
                p_title = p_win["title"][:25]
                
            if s_win:
                _position_window(s_win["hwnd"], wa_x + half_w, wa_y, wa_w - half_w, wa_h)
                s_title = s_win["title"][:25]
                
            return f"[OK] Side-by-side layout configured: '{p_title}' (Left 50%) | '{s_title}' (Right 50%)."

        elif layout_clean == "focus":
            target = _find_window(primary_app, wins) or (wins[0] if wins else None)
            if not target:
                return "[FAIL] No target window found for focus layout."
                
            for w in wins:
                if w["hwnd"] != target["hwnd"]:
                    user32.ShowWindow(w["hwnd"], SW_MINIMIZE)
                    
            user32.ShowWindow(target["hwnd"], SW_MAXIMIZE)
            try:
                user32.SetForegroundWindow(target["hwnd"])
            except Exception:
                pass
            return f"[OK] Focus Mode Activated for '{target['title'][:30]}'. All other windows minimized."

        elif layout_clean == "grid":
            qw = wa_w // 2
            qh = wa_h // 2
            quadrants = [
                (wa_x, wa_y, qw, qh),
                (wa_x + qw, wa_y, wa_w - qw, qh),
                (wa_x, wa_y + qh, qw, wa_h - qh),
                (wa_x + qw, wa_y + qh, wa_w - qw, wa_h - qh)
            ]
            count = min(len(wins), 4)
            for idx in range(count):
                _position_window(wins[idx]["hwnd"], *quadrants[idx])
            return f"[OK] Grid Layout Configured: {count} application windows aligned in quadrants."

        return f"[FAIL] Unknown layout '{layout}'. Supported: 'side_by_side', 'focus', 'grid', 'code_and_browser'."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)

async def snap_window(direction: str = "left", app: Optional[str] = None) -> str:
    """
    Snaps a specific application or the active window to a screen region.
    
    Args:
        direction: 'left', 'right', 'top', 'bottom', 'up', 'down', 'maximize', 'minimize', 'center', 'side_by_side'
        app: Optional application name or window title to target. If omitted, targets active foreground window.
    """
    def _execute():
        wa_x, wa_y, wa_w, wa_h = _get_work_area()
        wins = _get_all_visible_windows()
        
        target = _find_window(app, wins) if app else (_find_window("active", wins) or (wins[0] if wins else None))
        if not target:
            return f"[FAIL] Could not locate target window for '{app or 'active window'}'."
            
        hwnd = target["hwnd"]
        d = direction.lower().strip()
        
        if any(k in d for k in ["left", "snap_left", "snap_to_left"]):
            _position_window(hwnd, wa_x, wa_y, wa_w // 2, wa_h)
            return f"[OK] Snapped '{target['title'][:25]}' to the Left half."
        elif any(k in d for k in ["right", "snap_right", "snap_to_right"]):
            half_w = wa_w // 2
            _position_window(hwnd, wa_x + half_w, wa_y, wa_w - half_w, wa_h)
            return f"[OK] Snapped '{target['title'][:25]}' to the Right half."
        elif any(k in d for k in ["snap_to_top", "snap_top", "top_half"]):
            half_h = wa_h // 2
            _position_window(hwnd, wa_x, wa_y, wa_w, half_h)
            return f"[OK] Snapped '{target['title'][:25]}' to the Top half."
        elif any(k in d for k in ["snap_to_bottom", "snap_bottom", "bottom_half"]):
            half_h = wa_h // 2
            _position_window(hwnd, wa_x, wa_y + half_h, wa_w, wa_h - half_h)
            return f"[OK] Snapped '{target['title'][:25]}' to the Bottom half."
        elif any(k in d for k in ["up", "max", "maximize", "top"]):
            user32.ShowWindow(hwnd, SW_MAXIMIZE)
            return f"[OK] Maximized '{target['title'][:25]}'."
        elif any(k in d for k in ["down", "min", "minimize", "bottom"]):
            user32.ShowWindow(hwnd, SW_MINIMIZE)
            return f"[OK] Minimized '{target['title'][:25]}'."
        elif "center" in d or "middle" in d:
            cw = int(wa_w * 0.75)
            ch = int(wa_h * 0.75)
            cx = wa_x + (wa_w - cw) // 2
            cy = wa_y + (wa_h - ch) // 2
            _position_window(hwnd, cx, cy, cw, ch)
            return f"[OK] Centered '{target['title'][:25]}' on screen."
        elif "side" in d or "split" in d:
            return "[OK] Use side_by_side(primary, secondary) to split two windows."
            
        return f"[FAIL] Unknown direction '{direction}'. Use: left, right, top, bottom, up, down, maximize, minimize, center."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)

async def window_snap_to(window: str = "", position: str = "left", target: str = "") -> str:
    """
    Universal window snapping tool for arbitrary target windows and positions.
    
    Args:
        window: Name or title of the window/app to snap (e.g. 'chrome', 'antigravity', 'vscode').
        position: Target position: 'left', 'right', 'top', 'bottom', 'maximize', 'minimize', 'center'.
        target: Optional alias for window.
    """
    app_query = window or target or "active"
    return await snap_window(direction=position, app=app_query)

async def get_open_windows() -> str:
    """Returns a list of all currently open and visible application windows on the desktop."""
    def _execute():
        wins = _get_all_visible_windows()
        if not wins:
            return "[INFO] No visible application windows found on desktop."
        lines = [f"[WINDOWS] Open Applications ({len(wins)}):"]
        for idx, w in enumerate(wins, 1):
            safe_t = w["title"].encode("ascii", "replace").decode("ascii")
            safe_p = w["process"].encode("ascii", "replace").decode("ascii")
            lines.append(f"  {idx}. [{safe_p}] {safe_t} (HWND: {w['hwnd']}, PID: {w['pid']})")
        return "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)

async def manage_window(title: str, action: str) -> str:
    """
    Manages a specific window by title or process name.
    
    Args:
        title: Window title or process name substring.
        action: 'activate', 'focus', 'minimize', 'maximize', 'restore', 'close', 
                'snap_left', 'snap_right', 'snap_to_top', 'snap_to_bottom', 'center'
    """
    action_clean = action.lower().strip()
    if action_clean in ("close", "exit", "kill", "terminate"):
        return await window_close(target=title)
    elif action_clean in ("snap_left", "left", "snap_to_left"):
        return await snap_window(direction="left", app=title)
    elif action_clean in ("snap_right", "right", "snap_to_right"):
        return await snap_window(direction="right", app=title)
    elif action_clean in ("snap_to_top", "snap_top", "top"):
        return await snap_window(direction="snap_to_top", app=title)
    elif action_clean in ("snap_to_bottom", "snap_bottom", "bottom"):
        return await snap_window(direction="snap_to_bottom", app=title)
    elif action_clean in ("center", "middle"):
        return await snap_window(direction="center", app=title)
    elif action_clean in ("minimize", "min", "down"):
        return await snap_window(direction="minimize", app=title)
    elif action_clean in ("maximize", "max", "up"):
        return await snap_window(direction="maximize", app=title)
    elif action_clean in ("side_by_side", "split", "tile"):
        return await side_by_side(primary_app=title)
    elif action_clean in ("activate", "focus", "restore", "show"):
        def _execute():
            wins = _get_all_visible_windows()
            target = _find_window(title, wins)
            if not target:
                return f"[FAIL] Window matching '{title}' not found."
            user32.ShowWindow(target["hwnd"], SW_RESTORE)
            user32.keybd_event(0x12, 0, 0, 0)
            user32.SetForegroundWindow(target["hwnd"])
            user32.keybd_event(0x12, 0, 2, 0)
            return f"[OK] Window '{target['title'][:30]}' activated to foreground."
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _execute)

    return f"[FAIL] Unknown action '{action}'. Supported: activate, focus, minimize, maximize, restore, close, snap_left, snap_right, snap_to_top, snap_to_bottom, center."

async def window_close(target: str = "active") -> str:
    """
    Closes an open application window, browser tab, or active foreground window matching target query.
    
    Args:
        target: Window title, process name (e.g. 'chatgpt', 'chrome', 'notepad', 'code'), or 'active' for foreground.
    """
    def _execute():
        wins = _get_all_visible_windows()
        q = target.lower().strip()
        
        # 1. Target active window
        if q in ("active", "current", "foreground", "this"):
            fg_hwnd = user32.GetForegroundWindow()
            if fg_hwnd:
                user32.PostMessageW(fg_hwnd, WM_CLOSE, 0, 0)
                time.sleep(0.1)
                user32.PostMessageW(fg_hwnd, WM_SYSCOMMAND, SC_CLOSE, 0)
                return "[OK] Closed active foreground window."
                
        # 2. Match target window
        match = _find_window(target, wins)
        if match:
            hwnd = match["hwnd"]
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            time.sleep(0.1)
            user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_CLOSE, 0)
            
            # Browser tab closure fallback
            if any(b in match["process"].lower() for b in ["chrome", "msedge", "firefox", "brave"]):
                try:
                    import pyautogui
                    pyautogui.hotkey("ctrl", "w")
                except Exception:
                    pass
                    
            return f"[OK] Closed window: '{match['title'][:35]}' ({match['process']})."

        # 3. Process kill fallback if window not found but process is running
        for p in psutil.process_iter(['name', 'pid']):
            try:
                pname = p.info['name'] or ''
                if q in pname.lower() or pname.lower().replace('.exe', '') == q:
                    p.terminate()
                    return f"[OK] Terminated application process: {pname} (PID: {p.info['pid']})."
            except Exception:
                continue

        return f"[FAIL] Could not find any open window or process matching '{target}' to close."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)

async def close_tab() -> str:
    """Closes the currently active browser tab or document tab via Ctrl+W hotkey."""
    try:
        import pyautogui
        pyautogui.hotkey("ctrl", "w")
        return "[OK] Closed active tab."
    except Exception as e:
        return f"[FAIL] Could not close tab: {e}"

async def switch_window(target: str = "next") -> str:
    """
    Switches focus between open desktop application windows (real Windows Alt+Tab / App Switcher).
    
    Args:
        target: 'next' (or 'cycle' / 'alt_tab' to switch to next active window), or specific app name (e.g. 'chrome', 'antigravity', 'vscode', 'terminal', 'notepad').
    """
    def _execute():
        wins = _get_all_visible_windows()
        q = (target or "next").lower().strip()
        
        if q in ("next", "cycle", "alt_tab", "alt tab", "switch", "window", "tab", ""):
            try:
                import pyautogui
                pyautogui.hotkey("alt", "tab")
                time.sleep(0.1)
                return "[OK] Switched to next active application window."
            except Exception:
                if len(wins) > 1:
                    fg_hwnd = user32.GetForegroundWindow()
                    next_win = next((w for w in wins if w["hwnd"] != fg_hwnd), wins[0])
                    user32.ShowWindow(next_win["hwnd"], SW_RESTORE)
                    user32.keybd_event(0x12, 0, 0, 0)
                    user32.SetForegroundWindow(next_win["hwnd"])
                    user32.keybd_event(0x12, 0, 2, 0)
                    return f"[OK] Switched focus to '{next_win['title'][:30]}'."
                return "[OK] Cycled active window."
        
        # Specific target window
        target_win = _find_window(q, wins)
        if not target_win:
            _launch_app_if_needed(q)
            time.sleep(1.0)
            wins = _get_all_visible_windows()
            target_win = _find_window(q, wins)
            
        if target_win:
            hwnd = target_win["hwnd"]
            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.keybd_event(0x12, 0, 0, 0)
            user32.SetForegroundWindow(hwnd)
            user32.keybd_event(0x12, 0, 2, 0)
            return f"[OK] Switched and focused '{target_win['title'][:35]}' ({target_win['process']})."
            
        return f"[FAIL] Could not locate application matching '{target}'."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)

async def switch_app(app: str = "next") -> str:
    """Alias for switch_window to switch applications."""
    return await switch_window(target=app)

async def alt_tab() -> str:
    """Performs OS Alt+Tab window cycling."""
    return await switch_window(target="next")

async def switch_tab(direction: str = "next") -> str:
    """Switches tabs within the active application (browser or editor) via Ctrl+Tab or Ctrl+Shift+Tab."""
    try:
        import pyautogui
        if "prev" in direction.lower() or "back" in direction.lower():
            pyautogui.hotkey("ctrl", "shift", "tab")
            return "[OK] Switched to previous tab."
        else:
            pyautogui.hotkey("ctrl", "tab")
            return "[OK] Switched to next tab."
    except Exception as e:
        return f"[FAIL] Could not switch tab: {e}"

async def focus_window(app_or_title: str) -> str:
    """Brings a specific application window or document to the foreground."""
    return await switch_window(target=app_or_title)

# Convenience Aliases
sidebyside = side_by_side
split_screen = side_by_side
close_window = window_close
list_windows = get_open_windows
snap_to = window_snap_to
switch_to_app = switch_window
switch_app_window = switch_window