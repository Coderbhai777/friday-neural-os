"""
JARVIS / ULTRON Neural Voice & Speech Engine
Default Voice: Google Charon (Deep, Authoritative AI Voice)

Strict Architecture Constraints:
1. Pure Single-Audio-Owner: ALL pygame.mixer calls (init, load, play, stop, unload) occur exclusively inside the speech worker thread via control messages.
2. Real Gemini HTTP Timeout: Enforces socket-level timeout via types.HttpOptions(timeout=ms).
3. Robust Cancellation & Barge-In: Invalidation of request_id, atomic queue purge, and worker STOP control message.
4. Resilient Worker Lifecycle: Safe startup error handling with self-healing restart capability.
"""

import os
import io
import re
import sys
import time
import wave
import queue
import tempfile
import threading
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from dotenv import load_dotenv

logger = logging.getLogger("JARVIS.TTS")

# Ensure .env is loaded
for env_p in [
    Path.home() / "Documents" / "ULTRON_Data" / ".env",
    Path.home() / "Documents" / "JARVIS_Data" / ".env",
    Path(__file__).resolve().parent.parent / ".env",
    Path.home() / ".env",
]:
    if env_p.exists():
        load_dotenv(env_p)

DEFAULT_VOICE = os.getenv("VOICE_NAME", "Charon")
FALLBACK_EDGE_VOICE = "en-US-ChristopherNeural"  # Authoritative baritone fallback (never Ryan)
GEMINI_VOICE_NAME = DEFAULT_VOICE
EDGE_FALLBACK_VOICE = FALLBACK_EDGE_VOICE

# Control message types: ("SPEAK", req_id, text), ("STOP", None, None), ("QUIT", None, None)
_speech_queue: "queue.Queue[Tuple[str, Optional[int], Optional[str]]]" = queue.Queue(maxsize=32)
_playback_queue: "queue.Queue[Tuple[str, Optional[int], Optional[str]]]" = queue.Queue(maxsize=32)
_current_request_id = 0
_id_lock = threading.Lock()
_worker_thread: Optional[threading.Thread] = None
_synth_thread: Optional[threading.Thread] = None
_worker_started = False
_is_speaking = False


def is_speaking() -> bool:
    global _is_speaking
    return _is_speaking


def get_current_request_id() -> int:
    with _id_lock:
        return _current_request_id


def new_speech_session() -> int:
    """
    Begins a new speech session for a user request.
    Increments request ID, flushes pending speech queue, and signals worker to halt active playback immediately.
    """
    global _current_request_id
    # Calling stop_speech() invalidates prior audio and advances _current_request_id
    stop_speech()
    with _id_lock:
        return _current_request_id


def stop_speech():
    """
    Signals the speech pipeline to immediately stop playback, clear pending synthesis,
    and invalidate current request items.
    Guaranteed thread-safe and non-racing.
    """
    global _current_request_id
    with _id_lock:
        _current_request_id += 1

    # 1. Drain pending speech text messages from synthesis queue
    while not _speech_queue.empty():
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except Exception:
            break

    # 2. Drain pending audio files from playback queue and clean up disk artifacts
    while not _playback_queue.empty():
        try:
            item = _playback_queue.get_nowait()
            _playback_queue.task_done()
            if item and len(item) == 3 and item[0] == "PLAY" and item[2] and os.path.exists(item[2]):
                try:
                    os.remove(item[2])
                except Exception:
                    pass
        except Exception:
            break

    # 3. Send STOP control message to playback thread to handle mixer stop
    try:
        _playback_queue.put_nowait(("STOP", None, None))
    except Exception:
        pass


def _clean_text_for_speech(text: str) -> str:
    """Cleans markdown, backticks, URLs, and JSON from text for natural speech."""
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"```[\s\S]*?```", " [Code output displayed on screen] ", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = re.sub(r"[#*_~>]+", "", cleaned)
    cleaned = re.sub(r"\{.*?\}", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def split_into_sentences(text: str) -> List[str]:
    """Splits text into clean, spoken sentence units."""
    cleaned = _clean_text_for_speech(text)
    if not cleaned:
        return []
    raw_sentences = re.split(r"(?<=[.!?।])\s+", cleaned)
    return [s.strip() for s in raw_sentences if len(s.strip()) > 1]


_GEMINI_CLIENT = None
_CACHED_API_KEY = None
_client_lock = threading.Lock()


def _get_gemini_client(api_key: str):
    """Returns or creates a cached, persistent Google GenAI client instance."""
    global _GEMINI_CLIENT, _CACHED_API_KEY
    with _client_lock:
        if _GEMINI_CLIENT is not None and _CACHED_API_KEY == api_key:
            return _GEMINI_CLIENT
        from google import genai
        from google.genai import types
        # Enforce minimum Google Gemini SDK deadline (10,000 ms)
        http_opts = types.HttpOptions(timeout=10000)
        orig_google = os.environ.pop("GOOGLE_API_KEY", None)
        try:
            _GEMINI_CLIENT = genai.Client(api_key=api_key, http_options=http_opts)
        finally:
            if orig_google:
                os.environ["GOOGLE_API_KEY"] = orig_google
        _CACHED_API_KEY = api_key
        return _GEMINI_CLIENT


def _synthesize_charon_gemini(text: str, output_wav: str, timeout_sec: float = 10.0) -> bool:
    """
    Synthesizes voice using Google Gemini TTS API with Charon voice.
    Strictly configures HTTP timeout via types.HttpOptions and caches client for sub-second synthesis.
    """
    try:
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
        orig_google_key = os.environ.get("GOOGLE_API_KEY")
        
        # Enforce minimum allowed Google Gemini SDK deadline (10,000 ms)
        timeout_ms = max(10000, int(timeout_sec * 1000))
        http_opts = types.HttpOptions(timeout=timeout_ms)

        try:
            # Synchronize GOOGLE_API_KEY in memory to prevent SDK credential conflict warnings
            if orig_google_key != api_key:
                os.environ["GOOGLE_API_KEY"] = api_key

            client = _get_gemini_client(api_key)
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
                    ),
                    http_options=http_opts
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
        logger.debug(f"Gemini TTS synthesis failed or timed out: {e}")
        return False


def _synthesize_edge_fallback(text: str, output_mp3: str, voice: str = FALLBACK_EDGE_VOICE, timeout_sec: float = 3.5) -> bool:
    """Synthesizes speech using Edge-TTS as emergency fallback with baritone voice."""
    try:
        import asyncio
        import edge_tts

        async def _run():
            comm = edge_tts.Communicate(text=text, voice=voice)
            await comm.save(output_mp3)

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(asyncio.wait_for(_run(), timeout=timeout_sec))
            return os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0
        finally:
            loop.close()
    except Exception as e:
        logger.debug(f"Edge-TTS fallback synthesis failed: {e}")
        return False


def _synthesizer_worker_loop():
    """
    Background worker thread dedicated to audio synthesis.
    Pulls text from _speech_queue, synthesizes audio in parallel with playback,
    and enqueues resulting audio paths to _playback_queue.
    """
    while True:
        try:
            msg = _speech_queue.get()
            if msg is None:
                break
            cmd, req_id, sentence = msg
            if cmd == "QUIT":
                _speech_queue.task_done()
                break
            if cmd == "SPEAK":
                if req_id != get_current_request_id():
                    _speech_queue.task_done()
                    continue

                cleaned = _clean_text_for_speech(sentence or "")
                if not cleaned:
                    _speech_queue.task_done()
                    continue

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp_path = tmp.name

                success = _synthesize_charon_gemini(cleaned, tmp_path, timeout_sec=10.0)

                # Fallback to Edge baritone if Gemini timed out or failed
                if not success or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_fb:
                        tmp_path = tmp_fb.name
                    _synthesize_edge_fallback(cleaned, tmp_path, timeout_sec=3.5)

                if req_id != get_current_request_id() or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
                    try:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except Exception:
                        pass
                    _speech_queue.task_done()
                    continue

                try:
                    _playback_queue.put(("PLAY", req_id, tmp_path), timeout=5.0)
                except queue.Full:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                _speech_queue.task_done()

        except Exception as e:
            logger.error(f"Synthesizer worker exception: {e}")
            time.sleep(0.05)


def _playback_worker_loop():
    """
    Dedicated single-audio-owner thread.
    Exclusively handles all Pygame mixer operations and sequential playback.
    """
    global _is_speaking, _worker_started

    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)
    except Exception as e:
        logger.error(f"Failed to initialize Pygame mixer in audio worker: {e}")
        _worker_started = False
        return

    while True:
        try:
            msg = _playback_queue.get()
            if msg is None:
                break
            cmd, req_id, audio_path = msg

            if cmd == "QUIT":
                _playback_queue.task_done()
                break

            if cmd == "STOP":
                try:
                    if pygame.mixer.get_init():
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                except Exception:
                    pass
                _is_speaking = False
                _playback_queue.task_done()
                continue

            if cmd == "PLAY":
                if req_id != get_current_request_id() or not audio_path or not os.path.exists(audio_path):
                    if audio_path and os.path.exists(audio_path):
                        try:
                            os.remove(audio_path)
                        except Exception:
                            pass
                    _playback_queue.task_done()
                    continue

                try:
                    _is_speaking = True
                    if not pygame.mixer.get_init():
                        pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)

                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()

                    start_p = time.time()
                    while pygame.mixer.music.get_busy():
                        if req_id != get_current_request_id() or (time.time() - start_p) > 25.0:
                            pygame.mixer.music.stop()
                            break
                        time.sleep(0.03)

                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                finally:
                    _is_speaking = False
                    try:
                        if audio_path and os.path.exists(audio_path):
                            os.remove(audio_path)
                    except Exception:
                        pass
                    _playback_queue.task_done()

        except Exception as e:
            _is_speaking = False
            logger.error(f"Playback worker exception: {e}")
            time.sleep(0.05)


# Backward-compatible alias for existing tests
_speech_worker_loop = _playback_worker_loop


def ensure_speech_worker() -> bool:
    """Ensures both synthesis and playback pipeline threads are running and healthy."""
    global _worker_started, _worker_thread, _synth_thread
    if not _worker_started or _worker_thread is None or not _worker_thread.is_alive():
        _worker_started = True
        _worker_thread = threading.Thread(target=_playback_worker_loop, daemon=True, name="JARVIS_PlaybackWorker")
        _worker_thread.start()

    if _synth_thread is None or not _synth_thread.is_alive():
        _synth_thread = threading.Thread(target=_synthesizer_worker_loop, daemon=True, name="JARVIS_SynthWorker")
        _synth_thread.start()

    return _worker_started


# Auto-start worker on module load
ensure_speech_worker()


def enqueue_sentence(sentence: str, request_id: Optional[int] = None) -> bool:
    """
    Enqueues a sentence for playback under request_id.
    Returns True if successfully queued, False if queue full or text invalid.
    """
    ensure_speech_worker()
    r_id = request_id if request_id is not None else get_current_request_id()
    if not sentence or not sentence.strip():
        return False

    try:
        _speech_queue.put_nowait(("SPEAK", r_id, sentence.strip()))
        return True
    except queue.Full:
        logger.warning(f"Speech queue full (32 items); dropping overflow sentence: {sentence[:30]}...")
        return False


def speak_text_sync(text: str) -> str:
    """Synchronous convenience function for announcements."""
    req_id = new_speech_session()
    sentences = split_into_sentences(text)
    if not sentences:
        return "No text to speak."
    queued = 0
    for s in sentences[:3]:
        if enqueue_sentence(s, req_id):
            queued += 1
    return f"[JARVIS Charon Voice] Queued {queued} sentence(s)."


async def speak_text(text: str) -> str:
    """Async speech convenience function."""
    return speak_text_sync(text)


speak = speak_text_sync
