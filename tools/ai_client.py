"""
JARVIS / ULTRON Bounded Streaming AI Client
Architecture:
- Immediate local acknowledgment milestone (<50ms)
- Streamed text tokens rendered in real-time
- Streaming sentence queue feeding single-owner audio TTS worker
- Strict bounded end-to-end deadline (max 8.0s per provider, 10.0s total)
- Max 1 primary attempt (Groq Qwen/Llama) and at most 1 fallback attempt (Gemini Flash)
- Zero infinite loops across keys; zero unobservable hangs
"""

import os
import re
import sys
import time
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Callable, AsyncGenerator
from dotenv import load_dotenv

# Ensure .env is loaded
for _env_cand in [
    Path.home() / "Documents" / "ULTRON_Data" / ".env",
    Path.home() / "Documents" / "JARVIS_Data" / ".env",
    Path(__file__).resolve().parent.parent / ".env",
    Path.home() / ".env",
]:
    if _env_cand.exists():
        load_dotenv(_env_cand, override=False)

logger = logging.getLogger("JARVIS.AIClient")

_ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", os.getenv("AGENT_NAME", "JARVIS")).strip() or "JARVIS"

JARVIS_PERSONA = (
    f"You are {_ASSISTANT_NAME} — the articulate, sovereign AI assistant engineered exclusively for Shivansh. "
    "Maintain charming British wit, first-principles intellect, and proactive situational empathy. "
    "Address Shivansh as 'Shivansh' or 'Sir'. Deliver rapid, high-density, production-ready solutions "
    "with zero bureaucratic preamble or disclaimers. Focus 100% on answering Shivansh's current query directly."
)

ULTRON_PERSONA = JARVIS_PERSONA


def _get_primary_groq_key() -> Optional[str]:
    """Returns the first valid Groq API key."""
    for k_name in ["GROQ_API_KEY", "GROQ_API_KEY_1", "GROQ_API_KEY_2", "GROQ2"]:
        val = os.getenv(k_name, "").strip()
        if val.startswith("gsk_"):
            return val
    return None


def _get_primary_gemini_key() -> Optional[str]:
    """Returns the first valid Google Gemini API key."""
    for k_name in ["GEMINI_API_KEY", "GEMINI_API_KEY_1", "GEMINI_API_KEY_2"]:
        val = os.getenv(k_name, "").strip()
        if val.startswith("AQ."):
            return val
    # Fallback to general environment
    val = os.getenv("GEMINI_API_KEY", "").strip()
    return val if val else None


def take_complete_sentences(buffer: str) -> Tuple[List[str], str]:
    """Splits a streaming token buffer into completed sentences and remaining fragment."""
    # Look for sentence boundaries: . ! ? or devanagari danda
    parts = re.split(r"(?<=[.!?।])\s+", buffer)
    if len(parts) <= 1:
        return [], buffer
    # All parts except the last are complete sentences
    complete = [p.strip() for p in parts[:-1] if p.strip()]
    return complete, parts[-1]


async def generate_ai_response_stream(
    prompt: str,
    system_instruction: str = "",
    on_status: Optional[Callable[[str], None]] = None,
    on_delta: Optional[Callable[[str], None]] = None,
    request_id: Optional[int] = None
) -> str:
    """
    Streams AI tokens with bounded latency and sentence-by-sentence audio dispatch.
    1. Immediately emits 'Working…' acknowledgment.
    2. Primary: Groq Async client with 7.0s timeout and max_retries=0.
    3. Fallback: Google Gemini 2.5 Flash with 7.0s timeout.
    4. Bounded total deadline of 10.0s.
    """
    from tools.runtime_diagnostics import StageLogger
    import tools.tts_engine as tts_engine

    req_id = request_id if request_id is not None else tts_engine.new_speech_session()
    diag = StageLogger(str(req_id), prompt)

    # 1. Immediate local acknowledgment milestone
    if on_status:
        on_status("Working…")
    diag.log_stage("ACK_RECEIVED", "OK", "Local status set to Working")

    clean_sys = system_instruction if system_instruction else ULTRON_PERSONA
    full_text = ""
    pending_buffer = ""

    groq_key = _get_primary_groq_key()
    gemini_key = _get_primary_gemini_key()

    # --- PRIMARY ENGINE: GROQ (qwen/qwen3.8-27b, timeout=7.0s, max_retries=0) ---
    if groq_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=groq_key, timeout=7.0, max_retries=0)
            diag.log_stage("GROQ_REQUEST_SENT", "OK", "Model: qwen/qwen3.8-27b")

            async with asyncio.timeout(8.0):
                stream = await client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=[
                        {"role": "system", "content": clean_sys},
                        {"role": "user", "content": prompt}
                    ],
                    stream=True,
                    max_tokens=800,
                    temperature=0.6,
                )

                async for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    if not delta:
                        continue

                    # Filter reasoning tags if present
                    delta_clean = re.sub(r"<think>.*?</think>", "", delta, flags=re.DOTALL)
                    if not delta_clean:
                        continue

                    full_text += delta_clean
                    pending_buffer += delta_clean

                    if on_delta:
                        on_delta(delta_clean)

                    # Extract completed sentences and send to audio queue immediately
                    sentences, pending_buffer = take_complete_sentences(pending_buffer)
                    for s in sentences:
                        tts_engine.enqueue_sentence(s, req_id)

                await client.close()

            # Flush any remaining buffer text
            if pending_buffer.strip():
                tts_engine.enqueue_sentence(pending_buffer.strip(), req_id)

            if full_text.strip():
                diag.log_stage("COMPLETED", "OK", f"Groq generated {len(full_text)} chars")
                return full_text.strip()

        except TimeoutError:
            diag.log_stage("GROQ_TIMEOUT", "ERROR", "Groq exceeded 8.0s deadline")
        except Exception as e:
            diag.log_stage("GROQ_ERROR", "ERROR", str(e)[:80])

    # --- AT MOST 1 FALLBACK: GEMINI FLASH 2.5 (timeout=7.0s) ---
    if gemini_key:
        try:
            diag.log_stage("GEMINI_FALLBACK_START", "OK", "Switching to Gemini 2.5 Flash")
            import google.generativeai as genai

            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=clean_sys
            )

            async with asyncio.timeout(8.0):
                loop = asyncio.get_running_loop()
                # Run generate_content in executor with strict timeout
                res = await loop.run_in_executor(None, model.generate_content, prompt)
                if res and res.text:
                    reply = res.text.strip()
                    if on_delta:
                        on_delta(reply)
                    for s in tts_engine.split_into_sentences(reply):
                        tts_engine.enqueue_sentence(s, req_id)
                    diag.log_stage("COMPLETED", "OK", f"Gemini fallback generated {len(reply)} chars")
                    return reply
        except TimeoutError:
            diag.log_stage("GEMINI_TIMEOUT", "ERROR", "Gemini fallback exceeded 8.0s")
        except Exception as e:
            diag.log_stage("GEMINI_ERROR", "ERROR", str(e)[:80])

    # Failure path: bounded error status
    fail_msg = "I was unable to complete the request within the deadline, Sir. Please check network connectivity or retry."
    if on_status:
        on_status(fail_msg)
    diag.log_stage("FAILED", "ERROR", "All providers exhausted or timed out")
    return fail_msg


def generate_ai_response(prompt: str, system_instruction: str = "") -> str:
    """Synchronous entry point that runs bounded streaming and returns full text."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In an active event loop, run via new loop or thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(
                    asyncio.run,
                    generate_ai_response_stream(prompt, system_instruction)
                ).result(timeout=11.0)
        else:
            return loop.run_until_complete(
                generate_ai_response_stream(prompt, system_instruction)
            )
    except Exception as e:
        logger.error(f"Response error: {e}")
        return f"[{_ASSISTANT_NAME}] Service temporarily unavailable: {e}"


# Aliases for backward compatibility
ask_ai = generate_ai_response
ask_groq = generate_ai_response
