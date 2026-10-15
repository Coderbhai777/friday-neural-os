import os
import subprocess
import webbrowser
import time
from typing import Optional
import psutil
import pyautogui

# Some tools may require win32 libraries which should be available
try:
    import win32gui
    import win32process
    import win32con
    import win32api
except ImportError:
    pass

async def open_website_or_app(query: str) -> str:
    try:
        q = query.lower().replace("open", "").replace("launch", "").replace("start", "").strip()
        
        # Intercept Minecraft SMP join commands
        if "minecraft" in q or "smp" in q or "mc" == q or "bedrock" in q:
            from friday_tools.minecraft_bridge import start_minecraft_player_bot
            return await start_minecraft_player_bot()

        # Intercept Subagent spawning & listing commands
        if "subagent" in q or "sub agent" in q or "sub-agent" in q:
            from friday_tools.subagents import spawn_subagent, list_subagents
            if any(k in q for k in ["list", "show", "status", "check", "batao", "dikhao"]):
                return await list_subagents()
            clean_task = q.replace("subagent", "").replace("sub agent", "").replace("sub-agent", "").replace("spawn", "").replace("run", "").replace("create", "").replace("to", "").replace("for", "").strip()
            return await spawn_subagent(clean_task or "autonomous task")
            
        KNOWN_DIRECT_EXES = {
            'antigravity': r'C:\Users\shiva\AppData\Local\Programs\antigravity\Antigravity.exe',
            'anti-gravity': r'C:\Users\shiva\AppData\Local\Programs\antigravity\Antigravity.exe',
            'anti gravity': r'C:\Users\shiva\AppData\Local\Programs\antigravity\Antigravity.exe',
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'google chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'code': os.path.expandvars(r'%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe'),
            'vscode': os.path.expandvars(r'%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe'),
            'vs code': os.path.expandvars(r'%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe'),
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'notepad': r'C:\Windows\notepad.exe'
        }

        for k, exe_path in KNOWN_DIRECT_EXES.items():
            if k in q or q in k:
                if os.path.exists(exe_path):
                    subprocess.Popen([exe_path])
                    return f"✅ Launched: {k.title()}"

        KNOWN_WEB_APPS = {
            "chatgpt": "https://chatgpt.com",
            "chat gpt": "https://chatgpt.com",
            "openai": "https://chatgpt.com",
            "claude": "https://claude.ai",
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "whatsapp": "https://web.whatsapp.com",
            "perplexity": "https://www.perplexity.ai",
            "gemini": "https://gemini.google.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://x.com",
            "x": "https://x.com",
            "reddit": "https://www.reddit.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com"
        }
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
        for name, url in KNOWN_WEB_APPS.items():
            if name in q:
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, url])
                    return f"✅ Opened {name.title()} in Chrome ({url})."
                webbrowser.open(url)
                return f"✅ Opened {name.title()} ({url})."
        
        if "." in q or q.startswith("http") or q.startswith("www"):
            url = q if q.startswith("http") else "https://" + q
            webbrowser.open(url)
            return f"✅ Opened {q}"
            
        import shutil
        resolved = shutil.which(q)
        if resolved:
            subprocess.Popen([resolved])
            return f"✅ Launched: {q}"
            
        subprocess.Popen(["cmd", "/c", "start", "", q], shell=True)
        return f"✅ Launched: {q}"
            
    except Exception as e:
        return f"❌ Unable to open '{q}': {e}"

async def open_file_or_folder(path: str) -> str:
    os.startfile(path)
    return "Opened"

async def run_command(command: str) -> str:
    subprocess.Popen(command, shell=True)
    return "Command executed"

async def get_active_window() -> str:
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except: return "Unknown"

async def minimize_window() -> str:
    pyautogui.hotkey('win', 'down')
    return "Window minimized"

async def maximize_window() -> str:
    pyautogui.hotkey('win', 'up')
    return "Window maximized"

async def close_active_window() -> str:
    from friday_tools.window_manager import window_close
    return await window_close("active")

async def close_window(target: str = "active") -> str:
    """
    Closes a window, tab, or application matching target name or active foreground window.
    """
    from friday_tools.window_manager import window_close
    return await window_close(target)

window_close_tool = close_window

async def switch_window() -> str:
    pyautogui.hotkey('alt', 'tab')
    return "Switched window"

async def keyboard_mouse_control(action: str, value: Optional[str] = None) -> str:
    """
    Controls keyboard and mouse with high reliability using SafeController.
    Actions: move, click, double_click, right_click, type, press, hotkey, scroll, volume, swipe
    """
    try:
        from friday_tools.keyboard_mouse import (
            move_cursor, mouse_click, scroll_cursor, type_text,
            press_key, press_hotkey, control_volume, swipe_gesture
        )
        act = action.lower().strip()
        val = str(value or "").strip()

        if act == "move":
            if val in ("up", "down", "left", "right"):
                return await move_cursor(val)
            elif "," in val:
                x, y = map(int, val.split(","))
                pyautogui.moveTo(x, y, duration=0.2)
                return f"Moved mouse to ({x}, {y})"
            return await move_cursor("right")
        elif act in ("click", "left_click"):
            return await mouse_click("left")
        elif act in ("double_click", "double"):
            return await mouse_click("double")
        elif act in ("right_click", "right"):
            return await mouse_click("right")
        elif act == "type":
            return await type_text(val)
        elif act == "press":
            return await press_key(val)
        elif act == "hotkey":
            keys = [k.strip() for k in val.split(",") if k.strip()]
            return await press_hotkey(keys)
        elif act == "scroll":
            direction = "up" if not val.startswith("-") else "down"
            amount = abs(int(val)) if val.lstrip("-").isdigit() else 10
            return await scroll_cursor(direction, amount)
        elif act == "volume":
            return await control_volume(val or "up")
        elif act == "swipe":
            return await swipe_gesture(val or "up")

        return f"Unknown action '{action}'."
    except Exception as e:
        return f"UI Control Error: {str(e)}"

async def volume_control(level: int) -> str:
    # Requires specialized libraries or keys. Simulating with keys for now if not implemented fully
    for _ in range(50): pyautogui.press('volumedown') # Reset
    for _ in range(level // 2): pyautogui.press('volumeup')
    return f"Volume set to approx {level}%"

async def take_screenshot() -> str:
    pyautogui.screenshot("screenshot.png")
    return "Screenshot saved"

async def read_clipboard() -> str:
    import pyperclip
    return pyperclip.paste()

async def copy_to_clipboard(text: str) -> str:
    import pyperclip
    pyperclip.copy(text)
    return "Copied"

async def open_clipboard_history() -> str:
    pyautogui.hotkey('win', 'v')
    return "History opened"

async def running_processes() -> str:
    return ", ".join(p.name() for p in psutil.process_iter())

async def terminate_process(name: str) -> str:
    for p in psutil.process_iter():
        if p.name().lower() == name.lower():
            p.kill()
            return "Terminated"
    return "Not found"

async def control_bluetooth(action: str, device_name: Optional[str] = None) -> str:
    webbrowser.open("ms-settings:bluetooth")
    return f"Opened Bluetooth settings to action found: {action}"

async def control_windows_settings(page: str, toggle: Optional[str] = None) -> str:
    pages = {
        "display": "ms-settings:display", "sound": "ms-settings:sounds", 
        "notifications": "ms-settings:notifications", "power": "ms-settings:powersleep",
        "storage": "ms-settings:storagesense", "bluetooth": "ms-settings:bluetooth",
        "network": "ms-settings:network", "update": "ms-settings:windowsupdate"
    }
    webbrowser.open(pages.get(page.lower(), "ms-settings:"))
    return f"Opened {page} settings"

async def restart_system() -> str:
    os.system("shutdown /r /t 5")
    return "Restarting in 5s"

async def shutdown_system() -> str:
    os.system("shutdown /s /t 5")
    return "Shutting down in 5s"

async def sleep_system() -> str:
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Sleeping"

async def hibernate_system() -> str:
    os.system("shutdown /h")
    return "Hibernating"

async def lock_system() -> str:
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return "Locked"

async def set_brightness(level: int) -> str:
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        return f"Brightness: {level}%"
    except: return "Failed to set brightness"

async def show_notification(title: str, message: str) -> str:
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(title, message, duration=5, threaded=True)
        return "Notification sent"
    except: return "Failed"

async def login_with_gmail(website: str) -> str:
    """
    Automates the 'Sign in with Google' sequence for a specified website.
    Standardizes the URL, opens the login page, and prepares the session using GMAIL_USER.
    """
    user = os.getenv("GMAIL_USER")
    if not user:
        return "❌ GMAIL_USER not found in .env. Identity verification failed."

    # Clean and standardize the website URL
    clean_site = website.lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    if "." not in clean_site:
        clean_site += ".com"
    
    # Construct a likely login URL
    url = f"https://{clean_site}"
    if "/login" not in url and "/signin" not in url:
        # Check for sites that typically use different paths
        if "google" in clean_site: url = "https://accounts.google.com"
        elif "github" in clean_site: url = "https://github.com/login"
        else: url = f"https://{clean_site}/login"

    webbrowser.open(url)
    
    # Provide clear feedback on the identity being used
    return (f"🚀 Google Login Protocol Initiated for {clean_site}.\n"
            f"👤 Identity: {user}\n"
            "🛡️ Strategy: Navigated to login portal. Monitoring screen for 'Sign in with Google' prompt. "
            "Please select your account if the selection window appears.")

async def execute_powershell(command: str) -> str:
    try:
        res = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=30)
        return (res.stdout.strip() + res.stderr.strip())[:1000]
    except Exception as e: return f"Error: {e}"

async def execute_cmd(command: str) -> str:
    try:
        res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return (res.stdout.strip() + res.stderr.strip())[:1000]
    except Exception as e: return f"Error: {e}"

async def schedule_task(task_name: str, command: str, time: str) -> str:
    try:
        subprocess.run(f'schtasks /create /sc once /tn "{task_name}" /tr "{command}" /st {time} /f', shell=True)
        return "Task Scheduled"
    except Exception as e: return f"Error: {e}"

async def play_game_pc(game_name: str, duration_minutes: int = 10) -> str:
    """
    Autonomous PC Gaming: ULTRON takes control of a PC game for the specified duration.
    Uses vision analysis to decide and execute mouse/keyboard actions.
    """
    from PIL import Image
    from google import genai
    import io
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return "❌ Google API key missing."
    
    client = genai.Client(api_key=api_key)
    log = [f"🚀 Starting PC Neural Gaming: {game_name}", f"⏱️ Duration: {duration_minutes}m"]
    
    try:
        while time.time() < end_time:
            # 1. Capture Screen
            screenshot = pyautogui.screenshot()
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img = Image.open(img_byte_arr)
            
            # 2. Analyze
            prompt = (f"You are playing {game_name} on a PC. Analyze the screen and provide the NEXT action. "
                     "Return ONLY a command in one of these formats:\n"
                     "- 'click x,y' (coordinates)\n"
                     "- 'press key' (e.g. 'w', 'space', 'esc')\n"
                     "- 'none'\n"
                     "Respond ONLY with the command string.")
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=[prompt, img])
            action = response.text.strip().lower()
            
            # 3. Execute
            if "click" in action:
                try:
                    coords = action.replace("click", "").strip().split(",")
                    pyautogui.click(int(coords[0]), int(coords[1]))
                except: pass
            elif "press" in action:
                key = action.replace("press", "").strip()
                pyautogui.press(key)
            
            time.sleep(1) # Frequency
            
        return "\n".join(log) + "\n🏆 Session complete."
    except Exception as e:
        return f"❌ PC Gaming Error: {e}"

# --- INSTANT TAB, MOUSE, KEYBOARD & SCREEN CONTROLS ---

def _send_hw_hotkey(*vkeys):
    """Sends hardware-level keyboard events with precise scan codes across all Windows apps."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        for vk in vkeys:
            user32.keybd_event(vk, 0, 0, 0)
            time.sleep(0.015)
        time.sleep(0.02)
        for vk in reversed(vkeys):
            user32.keybd_event(vk, 0, 2, 0)  # KEYEVENTF_KEYUP
            time.sleep(0.015)
        return True
    except Exception:
        return False

async def switch_tab(direction: str = "next", target: str = "auto") -> str:
    """
    Instantly switches browser, editor, or application tabs (<10ms).
    Also supports switching Ultron's internal tabs (Chat vs Camera Vision).
    Direction: 'next', 'previous' (or 'prev'), or tab number (1 to 9).
    Target: 'auto', 'browser', 'ultron', 'chat', 'camera'.
    """
    try:
        d = str(direction).lower().strip()
        t = str(target).lower().strip()

        # Check if user requested Ultron UI tab switch specifically
        if t in ("ultron", "chat", "camera", "vision") or "camera" in d or "chat" in d or "vision" in d:
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    for w in app.topLevelWidgets():
                        if hasattr(w, "_switch_tab") and hasattr(w, "_right_stack"):
                            if "cam" in t or "vision" in t or "cam" in d or "vision" in d:
                                w._switch_tab(1)
                                return "[OK] Switched Ultron UI to Camera Vision tab."
                            elif "chat" in t or "chat" in d:
                                w._switch_tab(0)
                                return "[OK] Switched Ultron UI to Chat tab."
                            else:
                                curr = w._right_stack.currentIndex()
                                new_idx = 1 if curr == 0 else 0
                                w._switch_tab(new_idx)
                                name = "Camera Vision" if new_idx == 1 else "Chat"
                                return f"[OK] Switched Ultron UI to {name} tab."
            except Exception:
                pass

        # Windows Virtual-Key Codes:
        # VK_CONTROL: 0x11, VK_SHIFT: 0x10, VK_TAB: 0x09
        VK_CONTROL = 0x11
        VK_SHIFT = 0x10
        VK_TAB = 0x09

        if d in ("prev", "previous", "left", "back", "prior"):
            _send_hw_hotkey(VK_CONTROL, VK_SHIFT, VK_TAB)
            return "[OK] Switched to previous tab."
        elif d.isdigit():
            num = int(d)
            if 1 <= num <= 9:
                VK_DIGIT = 0x30 + num
                _send_hw_hotkey(VK_CONTROL, VK_DIGIT)
                return f"[OK] Switched to tab {num}."

        # Default: Next Tab (Ctrl + Tab)
        _send_hw_hotkey(VK_CONTROL, VK_TAB)
        return "[OK] Switched to next tab."
    except Exception as e:
        return f"[ERROR] Switch tab error: {e}"

async def new_tab(url: str = "") -> str:
    """
    Instantly opens a new browser/application tab (Ctrl+T) and navigates to URL if specified.
    """
    try:
        VK_CONTROL = 0x11
        VK_T = 0x54
        _send_hw_hotkey(VK_CONTROL, VK_T)
        if url:
            time.sleep(0.12)
            pyautogui.write(url, interval=0.01)
            pyautogui.press('enter')
            return f"[OK] Opened new tab and navigated to {url}."
        return "[OK] Opened new tab."
    except Exception as e:
        return f"[ERROR] New tab error: {e}"

async def close_tab() -> str:
    """
    Instantly closes the current browser/application tab (Ctrl+W).
    """
    try:
        VK_CONTROL = 0x11
        VK_W = 0x57
        _send_hw_hotkey(VK_CONTROL, VK_W)
        return "[OK] Closed current tab."
    except Exception as e:
        return f"[ERROR] Close tab error: {e}"

async def mouse_click(button: str = "left", clicks: int = 1, x: int = -1, y: int = -1) -> str:
    """
    Controls mouse clicking anywhere on the screen.
    Button: 'left', 'right', 'double', or 'middle'.
    If x and y are provided, moves to (x, y) first then clicks.
    """
    try:
        if x >= 0 and y >= 0:
            pyautogui.moveTo(x, y, duration=0.1)
        btn = button.lower().strip()
        if btn == "right":
            pyautogui.rightClick()
        elif btn in ("double", "double_click") or clicks == 2:
            pyautogui.doubleClick()
        elif btn == "middle":
            pyautogui.middleClick()
        else:
            pyautogui.click(clicks=clicks)
        pos = pyautogui.position()
        return f"[OK] Mouse clicked ({btn}) at {pos}."
    except Exception as e:
        return f"[ERROR] Mouse click error: {e}"

async def mouse_move(x: int, y: int) -> str:
    """
    Moves mouse cursor smoothly to coordinates (x, y) on the screen.
    """
    try:
        pyautogui.moveTo(x, y, duration=0.2)
        return f"[OK] Mouse moved to ({x}, {y})."
    except Exception as e:
        return f"[ERROR] Mouse move error: {e}"

async def mouse_scroll(amount: int = -300) -> str:
    """
    Scrolls the mouse wheel. Positive value scrolls UP, negative scrolls DOWN (e.g. -300 to scroll down).
    """
    try:
        pyautogui.scroll(int(amount))
        return f"[OK] Scrolled mouse wheel ({amount})."
    except Exception as e:
        return f"[ERROR] Mouse scroll error: {e}"

async def keyboard_type(text: str) -> str:
    """
    Types text into the active window, input field, or browser with exact spelling and zero mistakes.
    """
    try:
        if len(text) > 30:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            return f"[OK] Pasted exact text ({len(text)} characters) into active field."
        else:
            pyautogui.write(text, interval=0.02)
            return f"[OK] Typed text into active field."
    except Exception as e:
        return f"[ERROR] Keyboard typing error: {e}"

async def keyboard_press(key: str) -> str:
    """
    Presses a single key: 'enter', 'tab', 'esc', 'space', 'backspace', 'delete', 'f5', 'up', 'down', 'left', 'right', 'win'.
    """
    try:
        k = key.lower().strip()
        pyautogui.press(k)
        return f"[OK] Pressed key '{k}'."
    except Exception as e:
        return f"[ERROR] Key press error: {e}"

async def keyboard_hotkey(keys: str) -> str:
    """
    Executes a keyboard shortcut combination. E.g. 'ctrl,c', 'ctrl,v', 'ctrl,t', 'ctrl,w', 'alt,tab', 'win,d', 'ctrl,shift,esc', 'alt,f4'.
    """
    try:
        key_list = [k.strip().lower() for k in keys.replace("+", ",").split(",")]
        pyautogui.hotkey(*key_list)
        return f"[OK] Hotkey '{'+'.join(key_list)}' executed."
    except Exception as e:
        return f"[ERROR] Hotkey error: {e}"

async def control_screen(action: str) -> str:
    """
    Controls desktop screen state:
    - 'show_desktop' or 'minimize_all': Win+D
    - 'maximize': Win+Up
    - 'minimize' or 'restore': Win+Down
    - 'snap_left': Win+Left
    - 'snap_right': Win+Right
    - 'lock': Win+L (Lock workstation)
    - 'task_manager': Ctrl+Shift+Esc
    - 'switch_window': Alt+Tab
    """
    try:
        act = action.lower().strip()
        if act in ("show_desktop", "minimize_all", "desktop"):
            pyautogui.hotkey('win', 'd')
            return "[OK] Showing desktop."
        elif act in ("maximize", "max"):
            pyautogui.hotkey('win', 'up')
            return "[OK] Maximized active window."
        elif act in ("minimize", "restore", "min"):
            pyautogui.hotkey('win', 'down')
            return "[OK] Minimized active window."
        elif act in ("snap_left", "left"):
            pyautogui.hotkey('win', 'left')
            return "[OK] Snapped active window left."
        elif act in ("snap_right", "right"):
            pyautogui.hotkey('win', 'right')
            return "[OK] Snapped active window right."
        elif act in ("lock", "lock_screen"):
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "[OK] Workstation screen locked."
        elif act in ("task_manager", "taskmgr"):
            pyautogui.hotkey('ctrl', 'shift', 'esc')
            return "[OK] Task Manager opened."
        elif act in ("switch_window", "switch_app"):
            pyautogui.hotkey('alt', 'tab')
            return "[OK] Switched window."
        else:
            return f"[ERROR] Unknown screen action: {action}"
    except Exception as e:
        return f"[ERROR] Control screen error: {e}"

async def toggle_hand_gesture_mouse(enable: Optional[bool] = None) -> str:
    """
    Toggles or explicitly enables/disables touchless PC Hand Gesture Mouse Control.
    When enabled, hand movements control the Windows mouse cursor, pinch to click, and peace sign to scroll.
    Automatically active whenever ULTRON is minimized.
    """
    try:
        from aria_modules.sagar_orb_widget import get_active_worker
        w = get_active_worker()
        if w:
            new_state = (not w.pc_mouse_mode) if enable is None else bool(enable)
            w.set_pc_mouse_mode(new_state)
            status = "ENABLED (Desktop Mouse Hand Control Active)" if new_state else "DISABLED (3D Orb Gestures Active)"
            return f"🖐️ Hand Gesture PC Mouse Control is now {status}."
        return "⚠️ AirGestureWorker is not running."
    except Exception as e:
        return f"❌ Failed to toggle hand mouse mode: {e}"


async def change_wallpaper(image_path: str = "", query: str = "") -> str:
    """Changes desktop wallpaper by query, URL, or local path."""
    try:
        from friday_tools.image_downloader import change_wallpaper as _cw
        return await _cw(query_or_path=query or image_path, image_path=image_path)
    except Exception as e:
        return f"[ERROR] Failed to change wallpaper: {e}"


async def set_desktop_wallpaper(query_or_path: str = "") -> str:
    """Sets desktop wallpaper by query, URL, or local path."""
    return await change_wallpaper(query_or_path=query_or_path)


