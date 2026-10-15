"""
ULTRON Dedicated Chat Panel Interface Engine
Provides direct neural bridging between voice agent, tool execution,
and the right-side Cyber Chat Window.
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import friday_tools.conversation_history as mem
from friday_tools.ai_client import ask_ai

ATTACHMENT_LOG_PATH = Path.home() / "Documents" / "ULTRON_Data" / "latest_chat_attachment.json"


def _get_active_attachment_record() -> Optional[Dict[str, Any]]:
    if ATTACHMENT_LOG_PATH.exists():
        try:
            return json.loads(ATTACHMENT_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


async def get_chat_history(count: int = 10) -> str:
    """
    Directly retrieves the latest conversation messages exchanged in the right-side chat panel.
    Eliminates the need for screen reading or OCR.
    """
    turns = mem.load_turns()
    if not turns:
        return "💬 [CHAT PANEL] No messages have been exchanged in the chat panel yet, Sir."

    recent = turns[-count:]
    lines = ["💬 [ULTRON RIGHT-SIDE CHAT PANEL HISTORY]", "=" * 55]
    for t in recent:
        role = "👤 User (Shivansh)" if t.get("role") == "user" else "🤖 ULTRON"
        ts = t.get("timestamp", "")
        txt = t.get("text", "")
        lines.append(f"[{ts}] {role}:\n{txt}\n")

    return "\n".join(lines)


async def get_latest_chat_message() -> str:
    """
    Returns the most recent message sent by the user in the right-side chat panel.
    """
    turns = mem.load_turns()
    user_turns = [t for t in turns if t.get("role") == "user"]
    if not user_turns:
        return "💬 [CHAT PANEL] No user messages found in the active chat session."

    latest = user_turns[-1]
    return f"💬 [LATEST CHAT MESSAGE from User]\n[{latest.get('timestamp')}]: {latest.get('text')}"


async def get_latest_chat_image(prompt: str = "") -> str:
    """
    Directly inspects and analyzes the image attached or sent by the user in the right-side chat panel.
    Uses multi-modal neural vision directly on the file without requiring a full screen capture.
    """
    att = _get_active_attachment_record()
    if not att:
        # Check vision cache for latest uploaded image
        cache_dir = Path.home() / "Documents" / "ULTRON_Data" / "vision_cache"
        if cache_dir.exists():
            files = list(cache_dir.glob("*.jpg")) + list(cache_dir.glob("*.png"))
            if files:
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                latest_img = files[0]
                att = {
                    "file_path": str(latest_img),
                    "file_name": latest_img.name,
                    "instruction": "Latest image in cache"
                }

    if not att:
        return "❌ [CHAT VISION] No image or file attachment has been uploaded to the chat panel yet, Sir."

    file_path = att.get("file_path", "")
    if not os.path.exists(file_path):
        return f"❌ [CHAT VISION] The attached file '{att.get('file_name')}' could not be located at {file_path}."

    p = Path(file_path)
    if p.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif']:
        return f"ℹ️ [CHAT PANEL] The latest attached file is '{p.name}' (not an image). Use analyze_file() to inspect it."

    instruction = prompt.strip() if prompt.strip() else att.get("instruction", "Describe and analyze this uploaded image in exhaustive detail.")

    from aria_modules.vision_core import analyze_image_fast
    result = analyze_image_fast(file_path, prompt=instruction)

    try:
        from friday_tools.tts_engine import speak_text
        first_sentence = result.split(".")[0] if "." in result else result[:70]
        speak_text(f"Image analyzed from chat: {re.sub(r'[*_#`]', '', first_sentence)}")
    except Exception:
        pass

    return (
        f"🖼️ [ULTRON CHAT IMAGE ANALYSIS // {p.name}]\n"
        f"• Attached File: {file_path}\n"
        f"• Instruction: {instruction}\n"
        f"{'='*55}\n"
        f"{result}"
    )


async def send_chat_message(message: str) -> str:
    """
    Dispatches a message directly into the right-side visual chat panel and vocalizes it aloud.
    """
    try:
        from aria_modules.chat_input_section import _ACTIVE_CHAT_SECTIONS
        for section in _ACTIVE_CHAT_SECTIONS:
            try:
                section.sig_finalize_aria.emit(message)
            except Exception:
                pass
    except Exception:
        pass

    # Record in shared memory
    mem.add_conversation_turn("assistant", message, model_name="ULTRON-Chat")

    # Vocalize via TTS
    try:
        from friday_tools.tts_engine import speak_text
        spoken = re.sub(r'[*_#`\[\]]', '', message).strip()
        speak_text(spoken)
    except Exception:
        pass

    return f"✅ [MESSAGE DISPATCHED TO CHAT & VOICE]: {message}"


async def view_chat_context() -> str:
    """
    Provides a comprehensive overview of the right-side chat panel, including recent conversation turns
    and any currently attached file or image.
    """
    history = await get_chat_history(count=6)
    att = _get_active_attachment_record()
    att_str = f"📎 Current Chat Attachment: {att.get('file_name')} ({att.get('file_path')})" if att else "📎 Current Chat Attachment: None"

    return f"{history}\n\n{att_str}"
