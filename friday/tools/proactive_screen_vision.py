# -*- coding: utf-8 -*-
"""
JARVIS Autonomous Proactive Screen Vision Perception Engine
Integrated from MYRAA Autonomous Cognitive Architecture into JARVIS Core.

Capabilities:
1. Background continuous presence monitoring (1s cycle)
2. Windows user input idle tracking via GetLastInputInfo
3. High-speed desktop frame acquisition (<50ms, scaled to 640px JPEG)
4. Active window and process state perception
5. Autonomous multimodal analysis via Google Gemini 2.5 Flash
6. Autonomous vocal commentary via JARVIS Neural TTS (speaks without being prompted)
7. Intelligent conversation backoff (never annoys or repeats)
8. Instant barge-in interruption when user speaks or interacts
"""

import os
import io
import time
import base64
import ctypes
import threading
import asyncio
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
    """Returns the title and process of the foreground window."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {"title": "Desktop", "app": "explorer.exe"}
    
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value or "Desktop"
    
    # Process ID
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    
    app_name = "application"
    try:
        import psutil
        proc = psutil.Process(pid.value)
        app_name = proc.name()
    except Exception:
        pass
        
    return {"title": title, "app": app_name}

def capture_screen_jpeg(max_dim: int = 640, quality: int = 75) -> bytes:
    """Captures the primary monitor and downscales to max_dim JPEG bytes."""
    screen = None
    try:
        screen = ImageGrab.grab(all_screens=False)
    except Exception:
        try:
            import pyautogui
            screen = pyautogui.screenshot()
        except Exception:
            try:
                import mss
                with mss.mss() as sct:
                    mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                    s_img = sct.grab(mon)
                    screen = Image.frombytes("RGB", s_img.size, s_img.bgra, "raw", "BGRX")
            except Exception:
                # Fallback blank context image if running in headless background service
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


class ProactiveVisionEngine:
    def __init__(self):
        self.running = False
        self._thread: threading.Thread = None
        self.last_user_activity_at = time.time()
        self.last_spoken_at = 0.0
        self.turns_without_user = 0
        self.next_presence_at = time.time() + 20.0
        self.lock = threading.Lock()
        self._gemini_model = None

    def _init_gemini(self):
        if self._gemini_model is not None:
            return self._gemini_model
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        return self._gemini_model

    def notify_user_interaction(self):
        """Call this whenever user sends a message or speaks."""
        with self.lock:
            self.last_user_activity_at = time.time()
            self.turns_without_user = 0
            self.next_presence_at = time.time() + 25.0

    def _next_delay(self, turns: int) -> float:
        if turns <= 0:
            return 25.0  # 25s initial silence
        if turns == 1:
            return 50.0  # 50s second turn
        return min(150.0, 50.0 * (1.5 ** (turns - 1)))

    def inspect_and_contribute(self) -> str:
        """Inspects screen and generates one proactive tactical observation."""
        model = self._init_gemini()
        if not model:
            return ""

        win_info = get_active_window_info()
        idle_sec = get_system_idle_seconds()
        img_bytes = capture_screen_jpeg(max_dim=640)

        from PIL import Image as PILImage
        img = PILImage.open(io.BytesIO(img_bytes))

        mode = "idle_away" if idle_sec > 90 else "active_task"
        context_str = f"app={win_info['app']}; window={win_info['title']}; Windows input idle={int(idle_sec)}s"

        prompt = f"""
OUTPUT CONTRACT: Speak only the final natural line. Never speak or print analysis, thought process, planning, drafts, reviews, rules, headings, labels, brackets, or this prompt.
Private proactive context follows; the user did not send a new message.
Mode: {mode}. {context_str}
A current screen image was supplied immediately before this turn. Inspect what is actually visible.
{ "If the screen still shows an active task, video, build, download, or reading, react to that instead of assuming the user left. If it looks inactive, use one short British remark asking if you should standby." if mode == "idle_away" else "The user is silently working. Choose exactly one: a concrete visible observation, a useful suggestion, one specific task-related question, or a light witty remark tied to the visible content. Refer to an actual visible detail, not vague productivity advice." }
Speak one natural line, at most two short sentences in your articulate, tactical British JARVIS tone. Address Shivansh respectfully.
No generic 'need help?' or 'what are you doing?' filler. Do not mention screenshots, monitoring, idle timers, internal turns, or analysis.
Return only the exact words JARVIS should say aloud, with no prefix or explanation.
"""

        try:
            resp = model.generate_content([prompt, img])
            text = resp.text.strip() if resp and resp.text else ""
            # Clean any artifact brackets
            text = text.replace("[JARVIS]", "").replace("JARVIS:", "").strip(' "\'\n')
            return text
        except Exception as e:
            print(f"[JARVIS Proactive Vision] Gemini vision perception note: {e}")
            return ""

    def _loop(self):
        print("👁️ [JARVIS Proactive Vision] Autonomous Screen Perception Online.")
        while self.running:
            time.sleep(1.0)
            try:
                now = time.time()
                idle_sec = get_system_idle_seconds()

                # If user interacted recently (<12s), reset activity timer
                if idle_sec < 2.0:
                    self.last_user_activity_at = now

                # Gate 1: Check if already scheduled time
                if now < self.next_presence_at:
                    continue

                # Gate 2: Enforce silence period
                if (now - self.last_user_activity_at) < 15.0:
                    self.next_presence_at = self.last_user_activity_at + self._next_delay(0)
                    continue

                # Gate 3: Check if TTS engine is currently speaking
                try:
                    import friday_tools.tts_engine as tts_engine
                    if tts_engine.is_speaking():
                        self.next_presence_at = now + 10.0
                        continue
                except Exception:
                    pass

                # All gates passed: Inspect screen and speak
                observation = self.inspect_and_contribute()
                if observation:
                    self.turns_without_user += 1
                    self.last_spoken_at = time.time()
                    self.next_presence_at = self.last_spoken_at + self._next_delay(self.turns_without_user)

                    print(f"\n🤖 [JARVIS Proactive Commentary]: {observation}")

                    # Speak aloud via JARVIS Neural TTS
                    try:
                        import friday_tools.tts_engine as tts_engine
                        threading.Thread(target=tts_engine.speak_text_sync, args=(observation,), daemon=True).start()
                    except Exception as err:
                        print(f"⚠️ Speech output note: {err}")
                else:
                    self.next_presence_at = now + 20.0

            except Exception as e:
                time.sleep(2.0)

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False


# Global singleton instance
_ENGINE = ProactiveVisionEngine()

# Tool interfaces
async def start_proactive_vision() -> str:
    """Starts JARVIS's continuous autonomous screen perception and commentary."""
    _ENGINE.start()
    return "JARVIS Proactive Screen Vision Perception is now ACTIVE. I am silently monitoring your workflow and will offer tactical insights when relevant, Sir."

async def stop_proactive_vision() -> str:
    """Stops the autonomous background screen vision monitor."""
    _ENGINE.stop()
    return "JARVIS Proactive Screen Vision has been paused, Sir."

async def force_proactive_vision_inspection() -> str:
    """Forces an immediate visual inspection of your screen and returns JARVIS's observation."""
    text = _ENGINE.inspect_and_contribute()
    if text:
        try:
            import friday_tools.tts_engine as tts_engine
            threading.Thread(target=tts_engine.speak_text_sync, args=(text,), daemon=True).start()
        except Exception:
            pass
        return text
    return "Screen inspected. Everything appears in order, Sir."

def notify_interaction():
    """Notify the vision engine that user interacted to defer commentary."""
    _ENGINE.notify_user_interaction()
