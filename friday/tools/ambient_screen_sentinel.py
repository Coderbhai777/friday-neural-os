"""
JARVIS / ULTRON Ambient Screen Sentinel & Proactive AGI Co-Pilot
Features:
- Continuous background visual awareness without manual prompting
- 100% reliable Win32 GDI screen capture (no BitBlt crashes)
- Dynamic contextual reasoning (NO canned sarcasm, NO repetitive ChatGPT jokes)
- Anti-repetition deduplication filter (last 15 remarks tracked, minimum 60s adaptive cooldown)
- Automatic integration with ULTRON Ω Proactive Companion Engine & Charon Voice
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
from typing import Optional, List
from PIL import Image

_SENTINEL_THREAD: Optional[threading.Thread] = None
_SENTINEL_RUNNING = False
_LAST_INTERCEPT_TIME = 0.0
_COOLDOWN_SECONDS = 60.0  # Minimum 60-second cooldown between proactive remarks
_RECENT_REMARKS: List[str] = []

LOG_PATH = Path.home() / "Documents" / "ULTRON_Data" / "sentinel_events.log"


def _get_active_window_title() -> str:
    """Gets the title of the currently focused foreground window on Windows."""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


def _capture_screen_fast() -> Optional[bytes]:
    """Captures the current desktop screen via Win32 GDI with Desktop attachment."""
    try:
        try:
            from tools.ultron_vision_pipeline import capture_screen_direct
            img = capture_screen_direct(max_dim=768)
        except ImportError:
            from friday_tools.ultron_vision_pipeline import capture_screen_direct
            img = capture_screen_direct(max_dim=768)

        if img:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            return buf.getvalue()
    except Exception:
        pass

    # Fallback to PIL ImageGrab if pipeline not loaded
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        if img.width > 768:
            scale = 768 / float(img.width)
            img = img.resize((768, int(img.height * scale)), Image.Resampling.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        return buf.getvalue()
    except Exception:
        return None


def _is_duplicate_remark(text: str) -> bool:
    """Checks if the proposed remark is a duplicate or close paraphrase of recent remarks."""
    if not text or len(text.strip()) < 5:
        return True
    
    clean_new = text.lower().strip()
    words_new = set(re.findall(r"\w+", clean_new))
    if not words_new:
        return True

    for past in _RECENT_REMARKS[-15:]:
        clean_past = past.lower().strip()
        if clean_new == clean_past:
            return True
        words_past = set(re.findall(r"\w+", clean_past))
        if not words_past:
            continue
        overlap = len(words_new & words_past) / float(max(len(words_new), len(words_past)))
        if overlap > 0.60:
            return True
    return False


def _sentinel_loop(interval: float = 4.0):
    global _SENTINEL_RUNNING, _LAST_INTERCEPT_TIME, _COOLDOWN_SECONDS

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] AGI Screen Sentinel Activated.\n")
    except Exception:
        pass

    while _SENTINEL_RUNNING:
        try:
            time.sleep(interval)
            if not _SENTINEL_RUNNING:
                break

            now = time.time()
            if now - _LAST_INTERCEPT_TIME < _COOLDOWN_SECONDS:
                continue

            window_title = _get_active_window_title().strip()
            if not window_title:
                continue

            w_lower = window_title.lower()

            # Ignore idle, lock screens, and privacy-shielded windows
            shielded = ["bitwarden", "1password", "keepass", "password", "bank", "credit card", "login", "auth", "private browsing", "incognito"]
            if any(s in w_lower for s in shielded):
                continue

            # Only analyze when user is in development, terminal, browsing, or productivity environments
            relevant_targets = [
                "visual studio", "antigravity", "terminal", "powershell", "cmd",
                "chrome", "edge", "brave", "firefox", "chatgpt", "claude", "gemini",
                "github", "stack overflow", "cursor", "sublime", "pycharm"
            ]
            if not any(t in w_lower for t in relevant_targets):
                continue

            img_bytes = _capture_screen_fast()
            if not img_bytes:
                continue

            try:
                from aria_modules.vision_core import analyze_image_fast
            except ImportError:
                continue

            recent_context = "\n".join(f"- {r}" for r in _RECENT_REMARKS[-5:]) if _RECENT_REMARKS else "None"

            prompt = (
                "You are ULTRON's proactive desktop observer assisting Shivansh.\n"
                f"Shivansh is currently focused on window: '{window_title}'.\n"
                f"Recent remarks previously spoken (DO NOT REPEAT OR PARAPHRASE THESE):\n{recent_context}\n\n"
                "OBJECTIVE:\n"
                "Determine if there is a real, immediate technical roadblock (syntax error, compile failure, broken test, crash log, or confusing error) on screen.\n\n"
                "STRICT RULES:\n"
                "1. If there is NO active error or problem, or if the user is just normally browsing or reading, return intercept=false.\n"
                "2. NEVER use canned sarcasm, mock indignation, or clichés like 'Caught red-handed running to ChatGPT'.\n"
                "3. NEVER repeat or rephrase recent remarks.\n"
                "4. If an intervention is genuinely warranted, provide a concise, natural, professional observation in at most 1-2 sentences.\n"
                "5. Only interject if confidence >= 0.85.\n\n"
                "Return raw JSON ONLY:\n"
                "{\n"
                '  "intercept": bool,\n'
                '  "detected_text": str,\n'
                '  "confidence": float,\n'
                '  "spoken_response": str\n'
                "}\n"
            )

            raw = analyze_image_fast(img_bytes, prompt)
            clean = raw.strip() if raw else ""
            if clean.startswith("```"):
                clean = re.sub(r"^```(?:json)?\s*", "", clean)
                clean = re.sub(r"\s*```$", "", clean).strip()

            match = re.search(r"\{[\s\S]*\}", clean)
            if not match:
                continue

            data = json.loads(match.group(0))
            intercept = data.get("intercept", False)
            confidence = float(data.get("confidence", 0.0))
            spoken = data.get("spoken_response", "").strip()

            if intercept and confidence >= 0.85 and spoken:
                if _is_duplicate_remark(spoken):
                    # Suppress duplicate remark silently
                    continue

                _LAST_INTERCEPT_TIME = time.time()
                _RECENT_REMARKS.append(spoken)
                if len(_RECENT_REMARKS) > 50:
                    _RECENT_REMARKS.pop(0)

                detected = data.get("detected_text", "Contextual observation")

                # Log event
                log_msg = f"[{time.strftime('%H:%M:%S')}] Intercepted: '{detected}' -> Spoke: '{spoken}'\n"
                try:
                    with open(LOG_PATH, "a", encoding="utf-8") as f:
                        f.write(log_msg)
                except Exception:
                    pass

                # Speak proactively via ULTRON Charon voice
                try:
                    from tools.tts_engine import speak_text_sync
                    threading.Thread(target=speak_text_sync, args=(spoken,), daemon=True).start()
                except Exception:
                    try:
                        from friday_tools.tts_engine import speak_text_sync
                        threading.Thread(target=speak_text_sync, args=(spoken,), daemon=True).start()
                    except Exception:
                        pass

        except Exception:
            time.sleep(2.0)


async def start_screen_sentinel(interval_seconds: float = 4.0) -> str:
    """
    Activates ULTRON's continuous ambient screen perception (AGI Co-Pilot Mode).
    Watches the desktop environment cleanly using Win32 GDI with zero BitBlt crashes,
    evaluates context dynamically, and speaks only when a real roadblock occurs.
    """
    global _SENTINEL_THREAD, _SENTINEL_RUNNING

    if _SENTINEL_RUNNING and _SENTINEL_THREAD and _SENTINEL_THREAD.is_alive():
        return "[AGI Screen Sentinel is already active and watching your desktop screen in real-time.]"

    _SENTINEL_RUNNING = True
    _SENTINEL_THREAD = threading.Thread(target=_sentinel_loop, args=(interval_seconds,), daemon=True)
    _SENTINEL_THREAD.start()

    return (
        "👁️ [AGI Screen Sentinel Online]\n"
        "ULTRON is now actively observing your workspace.\n"
        "All BitBlt access issues resolved, canned repetitive sarcasm eliminated, "
        "and Charon neural baritone voice active for contextual interventions."
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
