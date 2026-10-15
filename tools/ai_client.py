"""
JARVIS / ULTRON Bounded Streaming AI Client (Production Grade)
Features:
- Enforces a REAL total request deadline across all providers (default 9.0s)
- Groq Async with timeout=min(6.0, remaining), max_retries=0
- Guaranteed client resource cleanup via try/finally
- Fallback Speech Isolation: If Groq emitted partial sentences, NEVER fall back to Gemini (prevents spliced conflicting speech)
- If Groq fails with 0 tokens, creates a fresh speech session before Gemini fallback
- Native async Gemini execution with real deadline protection
- Non-blocking sync adapter without ThreadPoolExecutor context-manager hang
"""

import os
import re
import sys
import time
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Callable
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
TOTAL_REQUEST_DEADLINE_SEC = 9.0
PRIMARY_PROVIDER_TIMEOUT_SEC = 6.0


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
    val = os.getenv("GEMINI_API_KEY", "").strip()
    return val if val else None


def take_complete_sentences(buffer: str) -> Tuple[List[str], str]:
    """Splits a streaming token buffer into completed sentences and remaining fragment."""
    parts = re.split(r"(?<=[.!?।])\s+", buffer)
    if len(parts) <= 1:
        return [], buffer
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
    Streams AI tokens with bounded latency and isolated sentence audio dispatch.
    - Total deadline: 9.0 seconds across all providers.
    - Primary: Groq Async (qwen/qwen3.8-27b) with max_retries=0.
    - Fallback: Gemini Flash 2.5 ONLY IF Groq produced 0 tokens.
    """
    from tools.runtime_diagnostics import StageLogger
    import tools.tts_engine as tts_engine

    start_time = time.time()
    deadline = start_time + TOTAL_REQUEST_DEADLINE_SEC

    req_id = request_id if request_id is not None else tts_engine.new_speech_session()
    diag = StageLogger(str(req_id), prompt)

    # 1. Immediate local acknowledgment (<50ms target)
    if on_status:
        on_status("Working…")
    diag.log_stage("ACK_RECEIVED", "OK", "Local acknowledgment displayed")

    clean_sys = system_instruction if system_instruction else ULTRON_PERSONA
    full_text = ""
    pending_buffer = ""
    chars_emitted = 0
    sentences_emitted = 0

    groq_key = _get_primary_groq_key()
    gemini_key = _get_primary_gemini_key()

    # --- PRIMARY ENGINE: GROQ (qwen/qwen3.8-27b) ---
    if groq_key:
        groq_client = None
        remaining_budget = max(1.0, deadline - time.time())
        groq_timeout = min(6.0, remaining_budget)
        try:
            from groq import AsyncGroq
            groq_client = AsyncGroq(api_key=groq_key, timeout=groq_timeout, max_retries=0)
            diag.log_stage("GROQ_REQUEST_SENT", "OK", f"Model: qwen/qwen3.8-27b, timeout: {groq_timeout:.1f}s")

            stream = await groq_client.chat.completions.create(
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
                # Check overall deadline
                if time.time() > deadline:
                    diag.log_stage("GROQ_STREAM_DEADLINE", "TIMEOUT", "Cut off by total request deadline")
                    break

                delta = chunk.choices[0].delta.content or ""
                if not delta:
                    continue

                delta_clean = re.sub(r"<think>.*?</think>", "", delta, flags=re.DOTALL)
                if not delta_clean:
                    continue

                full_text += delta_clean
                pending_buffer += delta_clean
                chars_emitted += len(delta_clean)

                if on_delta:
                    on_delta(delta_clean)

                # Split complete sentences and push to speech worker
                sentences, pending_buffer = take_complete_sentences(pending_buffer)
                for s in sentences:
                    if tts_engine.enqueue_sentence(s, req_id):
                        sentences_emitted += 1

            # Flush any remaining buffer text
            if pending_buffer.strip():
                if tts_engine.enqueue_sentence(pending_buffer.strip(), req_id):
                    sentences_emitted += 1

            if full_text.strip():
                diag.log_stage("COMPLETED", "OK", f"Groq generated {len(full_text)} chars in {round(time.time()-start_time, 2)}s")
                return full_text.strip()

        except Exception as e:
            err_str = str(e)[:80]
            diag.log_stage("GROQ_ERROR", "ERROR", err_str)
            logger.warning(f"Groq primary error: {err_str}")
        finally:
            if groq_client is not None:
                try:
                    await groq_client.close()
                except Exception:
                    pass

    # --- FALLBACK POLICY CHECK ---
    # If Groq already emitted text or sentences, DO NOT fall back to Gemini.
    # The user has already seen or heard partial speech; falling back would splice two disjoint answers.
    if chars_emitted > 0 or sentences_emitted > 0:
        if pending_buffer.strip():
            tts_engine.enqueue_sentence(pending_buffer.strip(), req_id)
        return full_text.strip()

    # --- AT MOST 1 BOUNDED FALLBACK: GEMINI FLASH 2.5 ---
    remaining = deadline - time.time()
    if gemini_key and remaining >= 2.5:
        try:
            diag.log_stage("GEMINI_FALLBACK_START", "OK", f"Switching to Gemini 2.5 Flash with {remaining:.1f}s remaining")
            # Invalidate any old speech and create a fresh speech session for fallback
            fallback_req_id = tts_engine.new_speech_session()

            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=gemini_key,
                http_options=types.HttpOptions(timeout=10000)
            )

            # Enforce remaining timeout via asyncio.wait_for
            gemini_coro = client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{clean_sys}\n\nUser: {prompt}"
            )
            response = await asyncio.wait_for(gemini_coro, timeout=min(remaining, 7.0))

            if response and response.text:
                reply = response.text.strip()
                if on_delta:
                    on_delta(reply)
                for s in tts_engine.split_into_sentences(reply):
                    tts_engine.enqueue_sentence(s, fallback_req_id)
                diag.log_stage("COMPLETED", "OK", f"Gemini fallback generated {len(reply)} chars")
                return reply

        except asyncio.TimeoutError:
            diag.log_stage("GEMINI_TIMEOUT", "ERROR", "Gemini fallback exceeded remaining budget")
        except Exception as e:
            diag.log_stage("GEMINI_ERROR", "ERROR", str(e)[:80])

    fail_msg = "I was unable to complete the request within the deadline, Sir. Please retry."
    if on_status:
        on_status(fail_msg)
    diag.log_stage("FAILED", "ERROR", f"Exhausted in {round(time.time()-start_time, 2)}s")
    return fail_msg


def generate_ai_response(prompt: str, system_instruction: str = "", **kwargs) -> str:
    """
    Synchronous fallback wrapper.
    Safely executes bounded streaming without ThreadPoolExecutor context-manager hang.
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If called from within an active asyncio loop, run in a daemon thread and wait with threading.Event
            result_box = []
            done_event = threading.Event()

            def _runner():
                try:
                    res = asyncio.run(generate_ai_response_stream(prompt, system_instruction))
                    result_box.append(res)
                except Exception as e:
                    result_box.append(f"[{_ASSISTANT_NAME} Error] {e}")
                finally:
                    done_event.set()

            t = threading.Thread(target=_runner, daemon=True)
            t.start()
            # Hard deadline on wait (10.0s)
            done_event.wait(timeout=TOTAL_REQUEST_DEADLINE_SEC + 0.5)
            if result_box:
                return result_box[0]
            return f"[{_ASSISTANT_NAME} Timeout] Request exceeded deadline."
        else:
            return asyncio.run(generate_ai_response_stream(prompt, system_instruction))
    except Exception as e:
        logger.error(f"Sync response error: {e}")
        return f"[{_ASSISTANT_NAME}] Service temporarily unavailable: {e}"


# Backward compatibility aliases
ask_ai = generate_ai_response
ask_groq = generate_ai_response
