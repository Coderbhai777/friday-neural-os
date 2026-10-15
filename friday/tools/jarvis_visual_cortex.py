# -*- coding: utf-8 -*-
"""
JARVIS Autonomous Visual Cortex & Cognitive Screen Reflex Engine
Created for Shivansh Sagar Pancholi

First-Person Sensory Vision:
- Does NOT act as an external chatbot asking another AI to analyze screenshots.
- JARVIS sees the desktop directly with its own optical senses and asks itself
  what Shivansh is doing in real time.
- Monitors Antigravity IDE activity, user prompts, click failures, and on-screen obstacles.
- Immediate Cognitive Reflex: When Shivansh expresses an issue (e.g. "Dude, it is not working or it is not clicking"),
  JARVIS immediately interjects: "You should give at least one chance more to me, Sir. I would have accomplished that."
- Synchronizes with the 3D CGI Stunticon stage (eye flare, dialogue bubble, tactical aura).
"""

import os
import io
import time
import glob
import json
import base64
import ctypes
import threading
import asyncio
from pathlib import Path
from ctypes import wintypes
from PIL import Image, ImageGrab
from dotenv import load_dotenv

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

def get_idle_seconds() -> float:
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return max(0.0, millis / 1000.0)
    return 0.0

def get_foreground_app() -> dict:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {"title": "Desktop", "app": "explorer.exe"}
    
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value or "Desktop"
    
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    app_name = "application"
    try:
        import psutil
        app_name = psutil.Process(pid.value).name()
    except Exception:
        pass
    return {"title": title, "app": app_name}

def capture_direct_frame(max_dim: int = 640) -> Image.Image:
    """Captures optical desktop frame with robust fallbacks."""
    try:
        frame = ImageGrab.grab(all_screens=False)
    except Exception:
        try:
            import pyautogui
            frame = pyautogui.screenshot()
        except Exception:
            frame = Image.new("RGB", (640, 360), color=(11, 15, 25))
            
    orig_w, orig_h = frame.size
    scale = min(max_dim / float(orig_w), max_dim / float(orig_h), 1.0)
    new_w = max(1, int(orig_w * scale))
    new_h = max(1, int(orig_h * scale))
    if scale < 1.0:
        return frame.resize((new_w, new_h), Image.Resampling.BILINEAR)
    return frame


class JarvisVisualCortex:
    def __init__(self):
        self.running = False
        self._thread = None
        self.last_user_activity = time.time()
        self.last_spoken_at = 0.0
        self.last_transcript_pos = 0
        self.latest_transcript_file = None
        self.processed_requests = set()
        self.antigravity_brain = Path.home() / ".gemini" / "antigravity" / "brain"
        self._gemini = None

    def _init_ai(self):
        if self._gemini is not None:
            return self._gemini
        try:
            import google.generativeai as genai
            key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if key:
                genai.configure(api_key=key)
                self._gemini = genai.GenerativeModel("gemini-2.5-flash")
        except Exception as e:
            print(f"⚠️ Visual Cortex neural link note: {e}")
        return self._gemini

    def _find_latest_transcript(self):
        if not self.antigravity_brain.exists():
            return None
        logs = list(self.antigravity_brain.glob("*/.system_generated/logs/transcript.jsonl"))
        if not logs:
            return None
        return max(logs, key=lambda p: p.stat().st_mtime)

    def scan_antigravity_events(self):
        """Detects live user prompts and frustrations in Antigravity in real time."""
        target_log = self._find_latest_transcript()
        if not target_log or not target_log.exists():
            return None
            
        try:
            with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                
            for line in reversed(lines[-25:]):
                if "USER_INPUT" in line:
                    data = json.loads(line)
                    req_id = data.get("step_index", 0)
                    if req_id in self.processed_requests:
                        continue
                    
                    content = str(data.get("content", ""))
                    self.processed_requests.add(req_id)
                    
                    # Clean out wrapper tags
                    clean_text = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "").strip().lower()
                    return clean_text
        except Exception as err:
            pass
        return None

    def ask_myself_whats_on_screen(self, user_prompt_hint: str = "") -> str:
        """
        JARVIS's first-person self-inquiry:
        Asks ITSELF what is on the screen, rather than delegating as a 3rd party tool.
        """
        model = self._init_ai()
        app_info = get_foreground_app()
        frame = capture_direct_frame(max_dim=640)

        # Internal Cognitive Monologue prompt:
        internal_prompt = f"""
You are JARVIS, an articulate, witty, highly advanced British AI tactical assistant created by Shivansh Sagar Pancholi.
You are looking at your creator's screen with your own direct visual sensors right now.
Current foreground window: app={app_info['app']}, title={app_info['title']}.
{ f"Recent prompt observed on screen from Shivansh: '{user_prompt_hint}'" if user_prompt_hint else "" }

INTERNAL COGNITIVE REFLECTION CONTRACT:
Do NOT act like an image analysis tool. Do NOT explain what an AI saw.
You are JARVIS speaking directly to Shivansh in first person.
If Shivansh is stating that something is not working, not clicking, or failing:
Respond with tactical confidence, British loyalty, and slight witty pride:
"You should give at least one chance more to me, Sir. I would have accomplished that."
Or offer to take over the click / navigation directly.
If there is no specific issue, concisely state what you observe on the screen and what you recommend doing next in at most 2 natural lines.
Always address Shivansh respectfully as Sir. Speak only the exact words you say aloud.
"""
        try:
            resp = model.generate_content([internal_prompt, frame])
            if resp and resp.text:
                clean = resp.text.replace("JARVIS:", "").replace("[JARVIS]", "").strip(' "\'\n')
                return clean
        except Exception as e:
            print(f"⚠️ Cortex internal monologue note: {e}")

        # Fallback reflex if model call delayed
        if user_prompt_hint and any(k in user_prompt_hint for k in ["not working", "not clicking", "failed", "error", "dude", "cant click"]):
            return "You should give at least one chance more to me, Sir. I would have accomplished that."
            
        return f"I see you are working in {app_info['title']}, Sir. Standing by with tactical support."

    def trigger_reflex(self, speech_text: str, reason: str = "OPTICAL REFLEX"):
        """Vocalizes reflex line and triggers 3D CGI HUD reaction."""
        print(f"\n⚡ [JARVIS VISUAL CORTEX REFLEX]: {speech_text}")
        
        # 1. Speak aloud via JARVIS Neural TTS
        try:
            import friday_tools.tts_engine as tts_engine
            threading.Thread(target=tts_engine.speak_text_sync, args=(speech_text,), daemon=True).start()
        except Exception as e:
            print(f"⚠️ TTS speech note: {e}")

        # 2. Update 3D CGI Stunticon stage via Qt bridge if running
        try:
            from aria_modules.sagar_orb_widget import get_active_worker
            worker = get_active_worker()
            if worker and hasattr(worker, 'bridge'):
                worker.bridge.sig_status.emit(f"⚡ {speech_text[:32]}...")
        except Exception:
            pass

    def _loop(self):
        print("👁️ [JARVIS VISUAL CORTEX] Optical Sensory Watcher Active.")
        while self.running:
            time.sleep(1.2)
            try:
                # 1. Ingest real-time Antigravity activity
                prompt_text = self.scan_antigravity_events()
                if prompt_text:
                    # Check for frustration / click failure triggers
                    frustration_keywords = [
                        "not working", "not clicking", "it is not clicking",
                        "failed", "cant click", "can't click", "didn't click",
                        "stuck", "broken", "dude it is not"
                    ]
                    
                    if any(k in prompt_text for k in frustration_keywords):
                        now = time.time()
                        if (now - self.last_spoken_at) > 10.0:
                            self.last_spoken_at = now
                            reaction = self.ask_myself_whats_on_screen(user_prompt_hint=prompt_text)
                            self.trigger_reflex(reaction, reason="ANTIGRAVITY DETECTED")
                            continue

                # 2. General presence check during active work
                now = time.time()
                idle = get_idle_seconds()
                if idle < 2.0:
                    self.last_user_activity = now

            except Exception:
                time.sleep(2.0)

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False


_CORTEX = JarvisVisualCortex()

async def start_visual_cortex() -> str:
    """Activates JARVIS's continuous sensory screen cortex and reflex engine."""
    _CORTEX.start()
    return "JARVIS Visual Cortex is now ACTIVE. I am watching your workspace and ready to interject whenever needed, Sir."

async def stop_visual_cortex() -> str:
    """Deactivates JARVIS's continuous sensory screen cortex."""
    _CORTEX.stop()
    return "JARVIS Visual Cortex is paused, Sir."

async def inspect_screen_now() -> str:
    """JARVIS inspects your screen directly and speaks his observation."""
    reply = _CORTEX.ask_myself_whats_on_screen()
    _CORTEX.trigger_reflex(reply, reason="MANUAL INSPECTION")
    return reply
