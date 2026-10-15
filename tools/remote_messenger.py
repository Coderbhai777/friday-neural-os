"""
ULTRON Remote Messaging Bridge (Telegram & WhatsApp Web / Twilio)
Enables 2-way remote control of ULTRON: send commands, execute tools, flash ESP32, or chat from mobile.
"""

import os
import time
import json
import asyncio
import threading
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser(r"~\.env"))
    load_dotenv(os.path.expanduser(r"~\Documents\ULTRON_Data\.env"))
    load_dotenv()
except ImportError:
    pass

_TELEGRAM_RUNNING = False
_TELEGRAM_THREAD = None
_LAST_UPDATE_ID = 0


def _get_telegram_creds():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    return token, chat_id


async def send_telegram_message(message: str, chat_id: str = "") -> str:
    """
    Sends a direct alert, status update, or briefing message to your Telegram account.
    """
    try:
        token, default_chat_id = _get_telegram_creds()
        target_chat = chat_id.strip() or default_chat_id
        if not token:
            return "[CONFIG REQUIRED] Please set TELEGRAM_BOT_TOKEN in your .env file."
        if not target_chat:
            return "[CONFIG REQUIRED] Please set TELEGRAM_CHAT_ID in your .env or pass chat_id."

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({"chat_id": target_chat, "text": message, "parse_mode": "Markdown"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return f"[OK] Telegram message sent to chat {target_chat}!"
            return f"[ERROR] Telegram API response: {data}"
    except Exception as e:
        return f"[ERROR] Failed to send Telegram message: {e}"


async def send_whatsapp_message(phone_number: str, message: str) -> str:
    """
    Dispatches a WhatsApp message via WhatsApp Web protocol or local desktop client.
    """
    try:
        clean_phone = phone_number.replace("+", "").replace("-", "").replace(" ", "").strip()
        encoded_msg = urllib.parse.quote(message)
        wa_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        
        import webbrowser
        webbrowser.open(wa_url)
        return f"[OK] WhatsApp Web opened for +{clean_phone} with your message pre-filled. Press Enter to send."
    except Exception as e:
        return f"[ERROR] Failed to dispatch WhatsApp message: {e}"


def _telegram_polling_worker():
    global _TELEGRAM_RUNNING, _LAST_UPDATE_ID
    token, authorized_chat = _get_telegram_creds()
    if not token:
        return

    from friday_tools.ai_client import generate_ai_response
    import friday_tools.ultron_memory as mem

    while _TELEGRAM_RUNNING:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={_LAST_UPDATE_ID + 1}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("ok"):
                    for update in data.get("result", []):
                        _LAST_UPDATE_ID = update.get("update_id", _LAST_UPDATE_ID)
                        msg = update.get("message", {})
                        text = msg.get("text", "").strip()
                        chat_id = str(msg.get("chat", {}).get("id", ""))
                        user_name = msg.get("from", {}).get("first_name", "Sir")

                        if text:
                            # Auto-save to memory
                            mem.auto_detect_and_store(text)
                            
                            # Process with ULTRON Dual-Engine (Qwen / GPT-120B / Gemini)
                            reply = generate_ai_response(
                                prompt=f"Message received via Telegram from {user_name}: {text}",
                                system_instruction="You are ULTRON operating remotely via Telegram Bridge. Provide concise, direct, tactical answers to Sir."
                            )
                            
                            # Send response back
                            reply_url = f"https://api.telegram.org/bot{token}/sendMessage"
                            reply_data = json.dumps({"chat_id": chat_id, "text": f"🤖 *[ULTRON Remote]*\n{reply}"}).encode("utf-8")
                            r_req = urllib.request.Request(reply_url, data=reply_data, headers={"Content-Type": "application/json"})
                            urllib.request.urlopen(r_req, timeout=10)
        except Exception:
            time.sleep(3)


async def start_telegram_bridge() -> str:
    """
    Starts the 2-way background Telegram Remote Control Bridge for ULTRON.
    Allows you to text ULTRON from your phone and receive instant AI answers & system actions.
    """
    global _TELEGRAM_RUNNING, _TELEGRAM_THREAD
    token, _ = _get_telegram_creds()
    if not token:
        return "[CONFIG REQUIRED] Set TELEGRAM_BOT_TOKEN in your .env file to enable 2-way Telegram chat."

    if _TELEGRAM_RUNNING:
        return "[STATUS] Telegram 2-way bridge is already active and listening for your messages."

    _TELEGRAM_RUNNING = True
    _TELEGRAM_THREAD = threading.Thread(target=_telegram_polling_worker, daemon=True)
    _TELEGRAM_THREAD.start()
    return "[OK] ULTRON 2-Way Telegram Remote Control Bridge is now ACTIVE! You can message your bot on Telegram anytime."


async def stop_telegram_bridge() -> str:
    """
    Stops the background Telegram bridge listener.
    """
    global _TELEGRAM_RUNNING
    _TELEGRAM_RUNNING = False
    return "[OK] Telegram Remote Bridge has been stopped."
