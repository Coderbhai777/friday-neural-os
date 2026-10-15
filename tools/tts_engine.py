"""
ULTRON Neural TTS Engine
Voice: en-GB-RyanNeural (British English, Male) - JARVIS / Ultron Baritone
Pitch: -5Hz | Rate: +0% | Sampling: 24,000 Hz (24 kHz) | Audio: MP3 Mono 48 kbps
Features:
- Instant barge-in interruption (stop_speech)
- Automatic length sanitization (prevents TTS hangs on huge documents/patent drafts)
- 30-second hard playback safety cap
- Synthesis network timeout protection (8s)
- Lock-free playback loop to prevent thread deadlocks
"""

import os
import io
import re
import sys
import time
import asyncio
import tempfile
import threading
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv(Path.home() / "Documents" / "ULTRON_Data" / ".env")

DEFAULT_VOICE = "en-GB-RyanNeural"
DEFAULT_PITCH = "-5Hz"
DEFAULT_RATE = "+0%"
DEFAULT_VOLUME = "+0%"

_is_speaking = False
_stop_requested = False
_lock = threading.Lock()


def is_speaking() -> bool:
    global _is_speaking
    return _is_speaking


def stop_speech():
    """Immediately stops any ongoing speech playback for instant barge-in interruption."""
    global _stop_requested, _is_speaking
    _stop_requested = True
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
    except Exception:
        pass
    _is_speaking = False


def _clean_text_for_speech(text: str) -> str:
    """
    Cleans and caps text for natural spoken conversation.
    Large documents (e.g. patent proposals, long code blocks, essays) are trimmed
    to the executive summary / first 2 sentences (max 280 chars) to prevent TTS hangs.
    """
    if not text:
        return ""

    # Strip thinking tags
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Strip triple backtick code blocks
    cleaned = re.sub(r"```[\s\S]*?```", " [Code output displayed on screen] ", cleaned)
    # Strip inline backticks
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    # Strip URLs
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Strip markdown symbols & headers
    cleaned = re.sub(r"[#*_~>]+", "", cleaned)
    # Strip JSON-like brackets
    cleaned = re.sub(r"\{.*?\}", "", cleaned)
    # Compress whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        return ""

    # For massive texts (like patent drafts, essays, long technical reports)
    # limit voice output to the first 2 meaningful sentences or ~250 chars
    if len(cleaned) > 280:
        sentences = re.split(r'(?<=[.!?])\s+', cleaned)
        spoken_summary = []
        cur_len = 0
        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            if cur_len + len(s_clean) <= 260:
                spoken_summary.append(s_clean)
                cur_len += len(s_clean)
            else:
                break

        if spoken_summary:
            cleaned = " ".join(spoken_summary)
        else:
            cleaned = cleaned[:250].rsplit(' ', 1)[0] + "."

        if not cleaned.endswith((".", "!", "?")):
            cleaned += "."

    return cleaned


def speak_text_sync(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
    volume: str = DEFAULT_VOLUME,
) -> str:
    """
    Synchronously speaks text aloud using Edge Neural TTS with exact RyanNeural parameters.
    Guaranteed thread-safe, non-deadlocking, and barge-in responsive.
    """
    global _is_speaking, _stop_requested

    # Preemptively stop previous speech
    stop_speech()

    cleaned = _clean_text_for_speech(text)
    if not cleaned:
        return "No text to speak."

    tmp_path = ""
    try:
        import edge_tts
        import pygame

        async def _synthesize():
            communicate = edge_tts.Communicate(
                text=cleaned,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume=volume,
            )
            nonlocal tmp_path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp_path = tmp.name
            await asyncio.wait_for(communicate.save(tmp_path), timeout=8.0)

        # Run synthesis with strict timeout
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_synthesize())
            loop.close()
        except Exception:
            try:
                asyncio.run(asyncio.wait_for(_synthesize(), timeout=8.0))
            except Exception as se:
                return f"TTS Synthesis note: {se}"

        if not tmp_path or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            return "Failed to synthesize speech audio file."

        with _lock:
            _stop_requested = False
            _is_speaking = True

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()

        # Playback loop runs outside the lock with 30s safety timeout to prevent deadlocks
        start_time = time.time()
        while pygame.mixer.music.get_busy() and not _stop_requested:
            if time.time() - start_time > 30.0:  # 30-second hard safety timeout
                pygame.mixer.music.stop()
                break
            time.sleep(0.05)

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass

        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

        _is_speaking = False
        return f"[Edge-TTS RyanNeural] Spoke: '{cleaned[:80]}...'"

    except Exception as e:
        _is_speaking = False
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return f"TTS Error: {e}"
    finally:
        _is_speaking = False


async def speak_text(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
    volume: str = DEFAULT_VOLUME,
) -> str:
    """
    Speaks text aloud using Edge Neural TTS with exact RyanNeural parameters.
    Supports real-time barge-in interruption.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, speak_text_sync, text, voice, rate, pitch, volume)


# Convenient alias
speak = speak_text_sync


async def generate_speech_audio(
    text: str,
    output_path: str = "",
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> str:
    """Generates a high-fidelity MP3 neural voice file from text."""
    if not output_path:
        out_dir = Path.home() / "Documents" / "ULTRON_Data" / "Voice_Recordings"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f"speech_{int(time.time())}.mp3")

    cleaned = _clean_text_for_speech(text)
    try:
        import edge_tts
        communicate = edge_tts.Communicate(
            text=cleaned,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )
        await asyncio.wait_for(communicate.save(output_path), timeout=15.0)
        return f"[OK] Speech audio generated: {output_path}"
    except Exception as e:
        return f"Audio generation error: {e}"


async def list_neural_voices() -> str:
    """Lists available neural voices."""
    voices = [
        ("en-GB-RyanNeural", "British English (Male) — Refined JARVIS / Ultron Baritone [DEFAULT]"),
        ("en-GB-AlfieNeural", "British English (Male) — Crisp, articulate formal voice"),
        ("en-US-GuyNeural", "US English (Male) — Deep American baritone"),
        ("en-US-ChristopherNeural", "US English (Male) — Smooth professional narrator"),
        ("en-IN-PrabhatNeural", "Indian English (Male) — Fluent natural voice"),
        ("en-GB-SoniaNeural", "British English (Female) — Clear, intelligent assistant"),
    ]
    lines = ["Active Neural Voice Core for ULTRON:\n"]
    for v, desc in voices:
        lines.append(f"- {v}: {desc}")
    return "\n".join(lines)
