"""
JARVIS Neural Voice & Speech Engine
Default Voice: Google Charon (Deep, Authoritative AI Voice) / Edge-TTS RyanNeural Fallback
Features:
- Instant barge-in interruption (stop_speech)
- Multi-lingual & Hinglish speech support
- 30-second hard playback safety cap
- Dynamic Google Gemini Charon TTS + Edge Neural fallback
"""

import os
import io
import re
import sys
import time
import wave
import asyncio
import tempfile
import threading
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure .env is loaded
for env_p in [
    Path.home() / "Documents" / "ULTRON_Data" / ".env",
    Path.home() / "Documents" / "JARVIS_Data" / ".env",
    Path.home() / ".env",
]:
    if env_p.exists():
        load_dotenv(env_p)

DEFAULT_VOICE = os.getenv("VOICE_NAME", "Charon")
if os.getenv("ASSISTANT_NAME", "").lower() == "simran":
    FALLBACK_EDGE_VOICE = "en-IN-NeerjaNeural"
    DEFAULT_VOICE = "Aoede"
else:
    FALLBACK_EDGE_VOICE = "en-US-ChristopherNeural"  # Deep authoritative baritone fallback (never Ryan)
    DEFAULT_VOICE = os.getenv("VOICE_NAME", "Charon")
DEFAULT_PITCH = "+0Hz"
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

    if len(cleaned) > 280:
        sentences = re.split(r'(?<=[.!?।])\s+', cleaned)
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

        if not cleaned.endswith((".", "!", "?", "।")):
            cleaned += "."

    return cleaned


def _synthesize_charon_gemini(text: str, output_wav: str) -> bool:
    """Synthesizes voice using Google Gemini TTS API with Charon voice."""
    try:
        # Prioritize true Gemini key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or not api_key.startswith("AQ."):
            for i in range(1, 10):
                k = os.getenv(f"GEMINI_API_KEY_{i}")
                if k and k.startswith("AQ."):
                    api_key = k
                    break
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return False

        from google import genai
        from google.genai import types

        voice_to_use = os.getenv("VOICE_NAME", "Charon")
        # Ensure google-genai SDK does not fall back to an invalid search GOOGLE_API_KEY
        orig_google_key = os.environ.get("GOOGLE_API_KEY")
        try:
            if api_key.startswith("AQ."):
                os.environ["GOOGLE_API_KEY"] = api_key

            client = genai.Client(api_key=api_key)
            # Instruct Gemini TTS explicitly to speak the exact transcript verbatim
            tts_prompt = f"Please read the following text aloud verbatim:\n\n{text}"
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=tts_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_to_use
                            )
                        )
                    )
                )
            )

            if response and response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        data = part.inline_data.data
                        with wave.open(output_wav, "wb") as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(24000)
                            wf.writeframes(data)
                        return True
            return False
        finally:
            if orig_google_key is not None:
                os.environ["GOOGLE_API_KEY"] = orig_google_key
            elif "GOOGLE_API_KEY" in os.environ and api_key.startswith("AQ."):
                del os.environ["GOOGLE_API_KEY"]
    except Exception as e:
        return False


def _synthesize_edge_fallback(text: str, output_mp3: str, voice: str = FALLBACK_EDGE_VOICE) -> bool:
    """Synthesizes speech using Edge-TTS as fallback."""
    try:
        import edge_tts

        async def _run():
            comm = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=DEFAULT_RATE,
                pitch=DEFAULT_PITCH,
            )
            await comm.save(output_mp3)

        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(asyncio.wait_for(_run(), timeout=8.0))
            loop.close()
            return os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0
        except Exception:
            return False
    except Exception:
        return False


def speak_text_sync(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
    volume: str = DEFAULT_VOLUME,
) -> str:
    """
    Synchronously speaks text aloud using Google Charon voice (with Edge-TTS fallback).
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
        import pygame

        # 1. Primary: Try Google Charon voice
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name

        success = _synthesize_charon_gemini(cleaned, tmp_path)

        # 2. Fallback to Edge Neural voice if Gemini offline
        if not success or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_fb:
                tmp_path = tmp_fb.name
            _synthesize_edge_fallback(cleaned, tmp_path, FALLBACK_EDGE_VOICE)

        if not tmp_path or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            return "Failed to synthesize speech audio file."

        with _lock:
            _stop_requested = False
            _is_speaking = True

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()

        # Playback loop with 30s safety cap
        start_time = time.time()
        while pygame.mixer.music.get_busy() and not _stop_requested:
            if time.time() - start_time > 30.0:
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
        return f"[JARVIS Charon Voice] Spoke: '{cleaned[:80]}...'"

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
    """Speaks text aloud using JARVIS Charon voice with barge-in interruption."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, speak_text_sync, text, voice, rate, pitch, volume)


speak = speak_text_sync


async def generate_speech_audio(
    text: str,
    output_path: str = "",
    voice: str = DEFAULT_VOICE,
) -> str:
    """Generates a high-fidelity audio voice file from text using Charon voice."""
    if not output_path:
        out_dir = Path.home() / "Documents" / "ULTRON_Data" / "Voice_Recordings"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f"jarvis_speech_{int(time.time())}.wav")

    cleaned = _clean_text_for_speech(text)
    if _synthesize_charon_gemini(cleaned, output_path):
        return f"[OK] JARVIS speech audio generated: {output_path}"
    return f"[ERROR] Could not generate audio."


async def list_neural_voices() -> str:
    """Lists available neural voices for JARVIS."""
    return (
        "Active Voice Core for JARVIS:\n"
        "- Charon: Google Gemini Live Deep Baritone (Default / Active)\n"
        "- en-GB-RyanNeural: British English (Male) — Refined High-Performance Fallback\n"
        "- Fenrir: Google Gemini Deep Dynamic Voice\n"
        "- Puck: Google Gemini Conversational Voice\n"
    )
