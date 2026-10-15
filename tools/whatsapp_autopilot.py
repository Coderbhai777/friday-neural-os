"""
ULTRON WhatsApp & Smart Messaging Autopilot
Automates message scheduling, group broadcasts, and AI-powered smart replies.
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"


def _get_gemini_model():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(DATA_DIR / ".env")
        api_key = os.getenv("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


async def whatsapp_schedule_message(recipient: str, message: str, delay_minutes: int = 1) -> str:
    """
    Schedules a WhatsApp message to be sent after a specified delay in minutes.
    """
    from friday_tools.communication import send_whatsapp_to_contact
    
    async def _delayed_send():
        await asyncio.sleep(delay_minutes * 60)
        await send_whatsapp_to_contact(recipient, message)
        
    asyncio.create_task(_delayed_send())
    return f"WhatsApp message to '{recipient}' scheduled to send in {delay_minutes} minute(s)."


async def whatsapp_broadcast(recipients: List[str], message: str) -> str:
    """
    Broadcasts a message to multiple contacts or groups with safe staggered delays.
    """
    from friday_tools.communication import send_whatsapp_to_contact
    
    results = []
    for contact in recipients:
        try:
            res = await send_whatsapp_to_contact(contact.strip(), message)
            results.append(f"✓ {contact}: Sent")
            await asyncio.sleep(2)  # Avoid rate throttling
        except Exception as e:
            results.append(f"✗ {contact}: Failed ({e})")
            
    return "Broadcast Results:\n" + "\n".join(results)


async def whatsapp_smart_reply(contact: str, tone: str = "friendly and concise") -> str:
    """
    Reads the last message from a contact and drafts an AI smart reply.
    """
    from friday_tools.communication import whatsapp_read_last_message
    
    last_msg = await whatsapp_read_last_message(contact)
    if "Error" in last_msg or not last_msg.strip():
        return f"Could not read last message from {contact}."
        
    prompt = f"""You are a Personal WhatsApp Copilot.
The user received this message from {contact}:
"{last_msg}"

Draft a {tone} reply. Return ONLY the ready-to-send reply text."""

    try:
        model = _get_gemini_model()
        reply_draft = model.generate_content(prompt).text.strip()
        return f"Incoming from {contact}: \"{last_msg}\"\n\nDrafted Smart Reply:\n\"{reply_draft}\""
    except Exception as e:
        return f"Error generating reply: {e}"
