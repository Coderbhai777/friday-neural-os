"""
ULTRON Omni-Comms Copilot (WhatsApp & Gmail Dedicated Engine)
Automated WhatsApp dispatch, Gmail IMAP/SMTP inbox triage,
smart ghostwriting, and instant OTP extraction.
"""

import os
import re
import imaplib
import smtplib
import urllib.parse
import webbrowser
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from dotenv import load_dotenv
    env_paths = [
        Path.home() / "Documents" / "ULTRON_Data" / ".env",
        Path.home() / ".env",
        Path(".env")
    ]
    for ep in env_paths:
        if ep.exists():
            load_dotenv(dotenv_path=ep, override=False)
except Exception:
    pass


def _get_gmail_credentials(account: str = "primary") -> Tuple[str, str]:
    if account == "primary":
        user = os.getenv("GMAIL_USER_2") or os.getenv("GMAIL_USER", "")
        pwd = os.getenv("GMAIL_APP_PASSWORD_2") or os.getenv("GMAIL_APP_PASSWORD", "")
    else:
        user = os.getenv("GMAIL_USER", "")
        pwd = os.getenv("GMAIL_APP_PASSWORD", "")
    return user, pwd


def _decode_mime_header(val: str) -> str:
    if not val:
        return ""
    decoded_parts = decode_header(val)
    out = []
    for part, enc in decoded_parts:
        if isinstance(part, bytes):
            try:
                out.append(part.decode(enc or "utf-8", errors="ignore"))
            except Exception:
                out.append(part.decode("latin-1", errors="ignore"))
        else:
            out.append(str(part))
    return "".join(out)


def _get_ai_text(prompt: str) -> str:
    try:
        from friday_tools.ai_client import ask_ai
        return ask_ai(prompt)
    except Exception:
        return ""


async def comms_whatsapp_send(
    contact_or_number: str,
    message_text: str,
    auto_open: bool = True
) -> str:
    """
    Prepares and dispatches a WhatsApp message.
    Cleans phone numbers, formats URL encoded deep-links, and launches WhatsApp Web or desktop client.
    """
    clean_target = contact_or_number.strip()
    digits = re.sub(r'[^0-9]', '', clean_target)
    
    # If 10-digit Indian number without country code, add 91
    if len(digits) == 10:
        digits = "91" + digits

    encoded_msg = urllib.parse.quote(message_text.strip())
    whatsapp_url = f"https://web.whatsapp.com/send?phone={digits}&text={encoded_msg}" if digits else f"https://web.whatsapp.com/"

    if auto_open:
        try:
            webbrowser.open(whatsapp_url)
        except Exception:
            pass

    try:
        from friday_tools.tts_engine import speak_text
        speak_text(f"WhatsApp message prepared for {contact_or_number}.")
    except Exception:
        pass

    return (
        f"📱 [WHATSAPP DISPATCH PREPARED]\n"
        f"• Target: {contact_or_number} (Normalized: +{digits if digits else 'Unknown'})\n"
        f"• Message: {message_text}\n"
        f"• Action: Opened WhatsApp Web client with preloaded message."
    )


async def comms_whatsapp_quick_dictate(contact_name: str, voice_note_topic: str) -> str:
    """
    Ghostwrites a high-polish, friendly or professional WhatsApp message based on bullet-point voice instructions.
    """
    prompt = f"""
    You are ULTRON's Communications Ghostwriter.
    Draft a concise, natural, modern WhatsApp message for Shivansh to send to '{contact_name}'.
    Topic / Voice notes: {voice_note_topic}

    Include appropriate emojis and clean phrasing. Output ONLY the message text.
    """
    draft = _get_ai_text(prompt)

    return (
        f"💬 [WHATSAPP GHOSTWRITE READY]\n"
        f"• Recipient: {contact_name}\n"
        f"• Draft:\n{draft}\n\n"
        f"Call comms_whatsapp_send to dispatch immediately."
    )


async def comms_gmail_triage_unread(max_count: int = 8, account: str = "primary") -> str:
    """
    Connects to Gmail via IMAP SSL, pulls unread messages, extracts sender/subject/preview,
    and uses AI to triage into Priority, Action Items, and Newsletters with spoken summary.
    """
    user, pwd = _get_gmail_credentials(account)
    if not user or not pwd:
        return "[COMMS ERROR] Gmail credentials (GMAIL_USER / GMAIL_APP_PASSWORD) not configured in .env."

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pwd)
        mail.select("INBOX")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            mail.logout()
            return f"📬 [GMAIL TRIAGE // {user}]\nNo unread emails in inbox. Inbox Zero maintained, Sir."

        msg_ids = messages[0].split()
        latest_ids = msg_ids[-max_count:]
        latest_ids.reverse()

        email_summaries = []
        for mid in latest_ids:
            res, data = mail.fetch(mid, "(RFC822.HEADER BODY.PEEK[TEXT])")
            if res != "OK":
                continue
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = _decode_mime_header(msg.get("Subject", "(No Subject)"))
            sender = _decode_mime_header(msg.get("From", "Unknown"))
            date_str = msg.get("Date", "")

            # Extract body snippet
            body_snippet = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body_snippet = part.get_payload(decode=True).decode("utf-8", errors="ignore")[:250]
                            break
                        except Exception:
                            pass
            else:
                try:
                    body_snippet = msg.get_payload(decode=True).decode("utf-8", errors="ignore")[:250]
                except Exception:
                    pass

            email_summaries.append(f"• ID: {mid.decode()} | From: {sender}\n  Subject: {subject}\n  Snippet: {body_snippet.strip()}")

        mail.logout()

        # AI Triage & Prioritization
        prompt = f"""
        You are GMAIL TRIAGE COPILOT for Shivansh.
        Analyze these unread emails:
        {chr(10).join(email_summaries)}

        Provide:
        1. 🚨 URGENT & ACTION ITEMS (if any, require attention)
        2. 📌 IMPORTANT UPDATES
        3. 🗑️ LOW PRIORITY / NOTIFICATIONS
        4. 🎙️ 1-sentence spoken voice summary
        """
        ai_triage = _get_ai_text(prompt)

        try:
            from friday_tools.tts_engine import speak_text
            speak_text(f"Inbox scanned. {len(latest_ids)} unread emails analyzed.")
        except Exception:
            pass

        return (
            f"📬 [GMAIL INTELLIGENT TRIAGE // {user}]\n"
            f"• Total Unread Fetched: {len(latest_ids)}\n"
            f"{'='*55}\n"
            f"{ai_triage}"
        )
    except Exception as e:
        return f"[COMMS ERROR] Failed to triage Gmail: {e}"


async def comms_gmail_smart_reply(
    email_index: int = 1,
    instructions: str = "Draft a concise, professional reply accepting or acknowledging",
    account: str = "primary"
) -> str:
    """
    Fetches the specified unread email, digests context, and writes a polished reply ready for transmission.
    """
    user, pwd = _get_gmail_credentials(account)
    if not user or not pwd:
        return "[COMMS ERROR] Gmail credentials not configured."

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pwd)
        mail.select("INBOX")

        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages[0]:
            mail.logout()
            return "[COMMS ERROR] Inbox empty."

        all_ids = messages[0].split()
        target_id = all_ids[-email_index]

        res, data = mail.fetch(target_id, "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        sender = _decode_mime_header(msg.get("From", "Unknown"))
        subject = _decode_mime_header(msg.get("Subject", "No Subject"))

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")[:1000]
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")[:1000]

        mail.logout()

        prompt = f"""
        Draft a high-standard email response from Shivansh to:
        Sender: {sender}
        Subject: {subject}
        Original Message:
        {body}

        Instructions: {instructions}
        Output Subject Line (Re: ...) and Body only.
        """
        reply_draft = _get_ai_text(prompt)

        return (
            f"✍️ [GMAIL SMART REPLY DRAFT]\n"
            f"• To: {sender}\n"
            f"• Regarding: {subject}\n"
            f"{'='*55}\n"
            f"{reply_draft}"
        )
    except Exception as e:
        return f"[COMMS ERROR] Failed to generate smart reply: {e}"


async def comms_gmail_instant_send(
    to_email: str,
    subject: str,
    body: str,
    account: str = "primary"
) -> str:
    """
    Sends an email via Gmail SMTP SSL.
    """
    user, pwd = _get_gmail_credentials(account)
    if not user or not pwd:
        return "[COMMS ERROR] Gmail credentials not configured."

    try:
        msg = MIMEMultipart()
        msg["From"] = user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(user, pwd)
        server.send_message(msg)
        server.quit()

        try:
            from friday_tools.tts_engine import speak_text
            speak_text(f"Email successfully dispatched to {to_email}.")
        except Exception:
            pass

        return (
            f"📧 [GMAIL DISPATCH SUCCESSFUL]\n"
            f"• Sender: {user}\n"
            f"• Recipient: {to_email}\n"
            f"• Subject: {subject}\n"
            f"• Timestamp: Sent successfully via SSL."
        )
    except Exception as e:
        return f"[COMMS ERROR] Failed to send email: {e}"


async def comms_gmail_extract_recent_otp(account: str = "primary") -> str:
    """
    Searches recent emails for OTPs, 2FA security codes, and verification pins, extracting the digits instantly.
    """
    user, pwd = _get_gmail_credentials(account)
    if not user or not pwd:
        return "[COMMS ERROR] Gmail credentials not configured."

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pwd)
        mail.select("INBOX")

        # Search subjects with security keywords
        status, messages = mail.search(None, '(OR SUBJECT "OTP" (OR SUBJECT "verification" (OR SUBJECT "code" SUBJECT "security")))')
        if status != "OK" or not messages[0]:
            mail.logout()
            return "🔐 [OTP EXTRACTOR] No recent OTP or verification emails detected."

        ids = messages[0].split()[-3:]
        ids.reverse()

        found_otps = []
        for mid in ids:
            res, data = mail.fetch(mid, "(RFC822)")
            raw = data[0][1]
            msg = email.message_from_bytes(raw)
            sender = _decode_mime_header(msg.get("From", "Unknown"))
            subject = _decode_mime_header(msg.get("Subject", "No Subject"))

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            # Extract 4-8 digit numbers
            matches = re.findall(r'\b\d{4,8}\b', body)
            if matches:
                found_otps.append(f"• Service/Sender: {sender}\n  Subject: {subject}\n  🔑 OTP Code: {matches[0]}")

        mail.logout()

        if found_otps:
            try:
                from friday_tools.tts_engine import speak_text
                code_match = re.search(r'🔑 OTP Code:\s*(\d+)', found_otps[0])
                if code_match:
                    speak_text(f"Your verification code is {' '.join(list(code_match.group(1)))}.")
            except Exception:
                pass

            return f"🔐 [GMAIL OTP / 2FA EXTRACTOR]\n{'='*55}\n" + "\n\n".join(found_otps)
        return "🔐 [OTP EXTRACTOR] No numerical OTP codes could be parsed from recent security emails."
    except Exception as e:
        return f"[COMMS ERROR] Failed to fetch OTP: {e}"
