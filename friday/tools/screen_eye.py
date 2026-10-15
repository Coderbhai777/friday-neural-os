"""
ULTRON Screen Eye, Instant OCR & Ambient Meeting Copilot
Captures on-screen text, detects compilation/system errors, and transcribes live meetings.
"""

import os
import io
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
NOTES_DIR = Path.home() / "Documents" / "ULTRON_Notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)


def _get_gemini_model():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(DATA_DIR / ".env")
        api_key = os.getenv("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def _capture_screen_bytes() -> bytes:
    import pyautogui
    from PIL import Image
    
    screenshot = pyautogui.screenshot()
    buf = io.BytesIO()
    screenshot.save(buf, format='JPEG', quality=85)
    return buf.getvalue()


async def screen_ocr_read(focus: str = "all text") -> str:
    """
    Instantly extracts non-selectable text, tables, or code from the current screen via Gemini Vision.
    """
    try:
        from aria_modules.vision_core import analyze_image_fast
        img_bytes = _capture_screen_bytes()
        prompt = f"Perform OCR on this screen image. Extract and transcribe {focus}. Preserve code formatting, tables, and exact text verbatim."
        res = await analyze_image_fast(img_bytes, prompt)
        return res
    except Exception as e:
        return f"Error reading screen text: {e}"


async def screen_detect_and_fix_error() -> str:
    """
    Scans the current screen for any visible compiler errors, stack traces, or dialog popups,
    and returns an immediate diagnosis with the exact copy-paste fix.
    """
    try:
        from aria_modules.vision_core import analyze_image_fast
        img_bytes = _capture_screen_bytes()
        prompt = """Inspect this screen capture for any visible errors, stack traces, compiler output, terminal failures, or warning dialogs.
If an error is found:
1. State the exact error message and file/line number
2. Diagnose the root cause
3. Provide the EXACT code fix or terminal command to resolve it.
If no error is visible on screen, state that the screen appears normal."""
        res = await analyze_image_fast(img_bytes, prompt)
        return res
    except Exception as e:
        return f"Error scanning screen for errors: {e}"


async def meeting_take_notes(duration_seconds: int = 60, topic: str = "Live Discussion") -> str:
    """
    Captures live audio from the microphone for the specified duration and compiles structured meeting minutes.
    """
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.record(source, duration=duration_seconds)
            
        try:
            transcript = r.recognize_google(audio)
        except Exception:
            return "No intelligible speech detected during the recording window."
            
        prompt = f"""You are an Executive Meeting Secretary.
The following transcript was captured from a live discussion on '{topic}':

RAW AUDIO TRANSCRIPT:
"{transcript}"

Generate structured Meeting Minutes:
1. DISCUSSION TOPIC & ATTENDEES SUMMARY
2. KEY DECISIONS MADE
3. ACTION ITEMS & OWNERS
4. FOLLOW-UP DEADLINES"""

        model = _get_gemini_model()
        notes = model.generate_content(prompt).text
        
        note_file = NOTES_DIR / f"Meeting_{int(time.time())}.md"
        with open(note_file, "w", encoding="utf-8") as f:
            f.write(f"# Meeting Notes: {topic}\n\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{notes}")
            
        return f"### 📝 Meeting Minutes Compiled ({topic}):\n\n{notes}\n\n[Saved to]: {note_file}"
    except Exception as e:
        return f"Error taking meeting notes: {e}"
