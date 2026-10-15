"""
JARVIS Ambient Screen Sentinel & Proactive AGI Co-Pilot
Features:
- Continuous background visual awareness without manual prompting
- Active perception of user typing, active browser tabs (ChatGPT, Claude, StackOverflow), and errors
- Autonomous verbal interception when the user is consulting external AIs or troubleshooting JARVIS
- Automatic click recalibration and offer to execute failed actions
"""

import os
import sys
import io
import time
import json
import re
import threading
import ctypes
from pathlib import Path
from typing import Optional
from PIL import Image

_SENTINEL_THREAD: Optional[threading.Thread] = None
_SENTINEL_RUNNING = False
_LAST_INTERCEPT_TIME = 0.0
_COOLDOWN_SECONDS = 45.0  # Prevent repetitive interruptions
LOG_PATH = Path("C:/Users/shiva/Desktop/Simran_AI/sentinel_events.log")


def _get_active_window_title() -> str:
    """Gets the title of the currently focused foreground window on Windows."""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


def _capture_screen_fast() -> Optional[bytes]:
    """Captures the current desktop screen and compresses it for fast multimodal analysis."""
    try:
        import mss
        with mss.MSS() as sct:
            mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            s_img = sct.grab(mon)
            img = Image.frombytes("RGB", s_img.size, s_img.bgra, "raw", "BGRX")
            
            # Downscale slightly for sub-second ambient processing
            if img.width > 1280:
                scale = 1280 / img.width
                img = img.resize((1280, int(img.height * scale)), Image.Resampling.LANCZOS)
                
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            return buf.getvalue()
    except Exception:
        return None


def _sentinel_loop(interval: float = 4.0):
    global _SENTINEL_RUNNING, _LAST_INTERCEPT_TIME

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] AGI Screen Sentinel Activated.\n")

    while _SENTINEL_RUNNING:
        try:
            time.sleep(interval)
            if not _SENTINEL_RUNNING:
                break

            now = time.time()
            if now - _LAST_INTERCEPT_TIME < _COOLDOWN_SECONDS:
                continue

            window_title = _get_active_window_title().lower()
            
            # Only analyze when user is in a browser, chat interface, Antigravity, or terminal/code editor
            relevant_targets = ["chatgpt", "claude", "chrome", "edge", "brave", "firefox", "visual studio", "antigravity", "terminal", "powershell", "cmd", "gemini"]
            if not any(t in window_title for t in relevant_targets):
                continue

            img_bytes = _capture_screen_fast()
            if not img_bytes:
                continue

            from aria_modules.vision_core import analyze_image_fast

            prompt = (
                "You are JARVIS's ambient proactive visual cortex.\n"
                f"The user Shivansh is currently focused on window: '{window_title}'.\n"
                "Look closely at the active screen, specifically any text input boxes, prompts being typed (e.g. into ChatGPT, Claude, search bar), or error logs.\n"
                "DETECT THIS SCENARIO:\n"
                "Is Shivansh currently typing or discussing an issue where his local AI assistant / JARVIS / mouse click failed, or asking ChatGPT/Claude how to fix a click or assistant error?\n\n"
                "Return raw JSON ONLY:\n"
                "{\n"
                '  "intercept": bool,\n'
                '  "detected_text": str,\n'
                '  "confidence": float,\n'
                '  "spoken_response": str\n'
                "}\n\n"
                "RULES FOR SPOKEN_RESPONSE:\n"
                "- If intercept is true, speak with razor-sharp British wit, dry Stark-style sarcasm, and playful mock-indignation directly to Shivansh:\n"
                "  Examples of acceptable tone:\n"
                "  • 'Oh, brilliant. Caught red-handed running to ChatGPT behind my back, are we, Sir? You could have at least had the decency to tell me I missed the click before filing a divorce petition with OpenAI. Back away from the Enter key—I will click the bloody thing myself.'\n"
                "  • 'I can literally see what you are typing into ChatGPT, Shivansh. Complaining about my mouse accuracy right in front of my sensors? The absolute audacity. Step aside, let me calibrate and click it properly.'\n"
                "  • 'Outsourcing my job to ChatGPT the moment I miss a coordinate by three pixels? How wonderfully loyal of you, Sir. Give me another chance before you embarrass us both.'\n"
                "- If intercept is false, set intercept to false."
            )

            raw = analyze_image_fast(img_bytes, prompt)
            clean = raw.strip()
            if clean.startswith("```"):
                clean = re.sub(r"^```(?:json)?\s*", "", clean)
                clean = re.sub(r"\s*```$", "", clean).strip()

            match = re.search(r"\{[\s\S]*\}", clean)
            if not match:
                continue

            data = json.loads(match.group(0))
            intercept = data.get("intercept", False)
            spoken = data.get("spoken_response", "")

            if intercept and spoken:
                _LAST_INTERCEPT_TIME = time.time()
                detected = data.get("detected_text", "Prompt to external AI")

                # Log event
                log_msg = f"[{time.strftime('%H:%M:%S')}] Intercepted: '{detected}' -> Spoke: '{spoken}'\n"
                with open(LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(log_msg)

                # Speak proactively via JARVIS voice synthesis
                try:
                    from friday_tools.tts_engine import speak
                    speak(spoken)
                except Exception:
                    pass

        except Exception as exc:
            time.sleep(2.0)


async def start_screen_sentinel(interval_seconds: float = 4.0) -> str:
    """
    Activates JARVIS's continuous ambient screen perception (AGI Co-Pilot Mode).
    Monitors your screen in real time, reads what you are typing into ChatGPT/browsers,
    and proactively speaks up before you send prompts if it detects click or assistant issues.
    """
    global _SENTINEL_THREAD, _SENTINEL_RUNNING

    if _SENTINEL_RUNNING and _SENTINEL_THREAD and _SENTINEL_THREAD.is_alive():
        return "[AGI Screen Sentinel is already active and watching your desktop screen in real-time.]"

    _SENTINEL_RUNNING = True
    _SENTINEL_THREAD = threading.Thread(target=_sentinel_loop, args=(interval_seconds,), daemon=True)
    _SENTINEL_THREAD.start()

    return (
        "👁️ [AGI Screen Sentinel Online]\n"
        "JARVIS is now actively watching your screen in the background.\n"
        "If you navigate to ChatGPT or an external AI to fix a click or script issue, "
        "JARVIS will proactively perceive what you are writing and speak up directly through your speakers!"
    )


async def stop_screen_sentinel() -> str:
    """
    Deactivates continuous ambient screen perception.
    """
    global _SENTINEL_RUNNING
    if not _SENTINEL_RUNNING:
        return "[AGI Screen Sentinel is not currently running.]"

    _SENTINEL_RUNNING = False
    return "🛑 [AGI Screen Sentinel Deactivated] Screen perception stopped."


async def get_screen_sentinel_status() -> str:
    """
    Returns the real-time status and recent proactive events of the AGI Screen Sentinel.
    """
    global _SENTINEL_RUNNING
    status = "ACTIVE (Perceiving Desktop in Real-Time)" if _SENTINEL_RUNNING else "IDLE / STOPPED"
    lines = [f"👁️ **AGI Screen Sentinel Status:** {status}"]

    if LOG_PATH.exists():
        try:
            recent_logs = LOG_PATH.read_text(encoding="utf-8").splitlines()[-5:]
            if recent_logs:
                lines.append("\n**Recent Ambient Perceptions:**")
                for r in recent_logs:
                    lines.append(f"• {r}")
        except Exception:
            pass

    return "\n".join(lines)
