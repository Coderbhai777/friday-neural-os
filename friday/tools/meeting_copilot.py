"""
ULTRON Meeting & Audio Intelligence Co-Pilot
Live audio transcription, timestamped minutes of meeting generator, and automated action-item extractor.
"""

import os
import time
import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, Any

from friday_tools.sound_engine import play_sound_async

_MEETINGS_DIR = Path.home() / "Documents" / "ULTRON_Data" / "Meetings"
_MEETINGS_DIR.mkdir(parents=True, exist_ok=True)


async def transcribe_meeting_audio(audio_path: Optional[str] = None, meeting_title: str = "Workstation Discussion") -> str:
    """
    Transcribes audio from a meeting or voice recording and generates structured minutes, key takeaways, and action items.
    
    Args:
        audio_path: Path to .mp3, .wav, or .m4a recording file.
        meeting_title: Title or topic of the meeting.
    """
    play_sound_async("scan")
    
    if not audio_path or not os.path.exists(audio_path):
        # Check latest voice recording
        recordings_dir = Path.home() / "Documents" / "ULTRON_Data" / "Voice_Recordings"
        if recordings_dir.exists():
            files = sorted(recordings_dir.glob("*.mp3"), key=os.path.getmtime, reverse=True)
            if files:
                audio_path = str(files[0])
                
    if not audio_path or not os.path.exists(audio_path):
        return "[FAIL] No audio recording file found to transcribe. Please provide audio_path."
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        
        # Upload audio file to Gemini
        uploaded = genai.upload_file(audio_path)
        
        prompt = (
            f"You are ULTRON's executive meeting secretary. Analyze this audio for '{meeting_title}'.\n"
            f"Provide:\n"
            f"1. Executive Summary (3-4 sentences)\n"
            f"2. Timestamped Key Discussion Points\n"
            f"3. Decisions Made\n"
            f"4. Action Items & Assignments Table (Owner, Task, Deadline)\n"
            f"5. Draft Follow-up Email to Participants"
        )
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([uploaded, prompt])
        
        out_file = _MEETINGS_DIR / f"Meeting_{int(time.time())}_{meeting_title.replace(' ', '_')}.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"# Meeting Minutes: {meeting_title}\nDate: {time.strftime('%Y-%m-%d %H:%M')}\nAudio: {os.path.basename(audio_path)}\n\n")
            f.write(response.text)
            
        play_sound_async("chime")
        return (
            f"📋 [MEETING MINUTES GENERATED]\n"
            f"• Title: {meeting_title}\n"
            f"• Saved To: {out_file}\n\n"
            f"{response.text[:1200]}..."
        )
    except Exception as e:
        return f"[FAIL] Meeting transcription failed: {e}"


async def get_latest_meeting_summary() -> str:
    """Returns the most recent meeting notes and action items."""
    files = sorted(_MEETINGS_DIR.glob("*.md"), key=os.path.getmtime, reverse=True)
    if not files:
        return "[INFO] No saved meeting notes found."
    with open(files[0], "r", encoding="utf-8") as f:
        return f"[LATEST MEETING: {files[0].name}]\n\n" + f.read()
