"""
ULTRON Email Copilot Tool Module
Intelligent email management using SHIVAMOGH account as PRIMARY.
"""

import os
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils
import smtplib
import re
import json
import time
import html
from typing import Dict, Any, Tuple, List, Optional

# Load .env fallback if not already in environment
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser(r"~\.env"))
    load_dotenv(os.path.expanduser(r"~\Documents\ULTRON_Data\.env"))
    load_dotenv()
except ImportError:
    pass


# ==============================
# HELPER FUNCTIONS
# ==============================

def _get_email_creds(account='primary') -> Tuple[str, str]:
    """
    Retrieve credentials for primary or secondary email account.
    Primary: GMAIL_USER_2 (shivamogh.12@gmail.com)
    Secondary: GMAIL_USER (fridayjarvis919@gmail.com)
    """
    if str(account).strip().lower() in ('primary', '1', 'shivamogh'):
        return os.getenv('GMAIL_USER_2', ''), os.getenv('GMAIL_APP_PASSWORD_2', '')
    return os.getenv('GMAIL_USER', ''), os.getenv('GMAIL_APP_PASSWORD', '')


def _decode_mime_header(header_val: Any) -> str:
    """Safely decode RFC2047 MIME-encoded headers into a plain string."""
    if not header_val:
        return ""
    try:
        decoded_parts = decode_header(str(header_val))
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or "utf-8", errors="replace"))
                except Exception:
                    result.append(part.decode("latin1", errors="replace"))
            else:
                result.append(str(part))
        return "".join(result).strip()
    except Exception:
        return str(header_val).strip()


def _extract_body_and_urls(msg: email.message.Message) -> Tuple[str, List[str]]:
    """Extract plain text body (or converted HTML) and all URLs from email message."""
    body_text = ""
    body_html = ""

    try:
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get("Content-Disposition", ""))
                if "attachment" in cdispo.lower():
                    continue
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                charset = part.get_content_charset() or "utf-8"
                try:
                    decoded = payload.decode(charset, errors="replace")
                except Exception:
                    decoded = payload.decode("latin1", errors="replace")

                if ctype == "text/plain" and not body_text:
                    body_text = decoded
                elif ctype == "text/html" and not body_html:
                    body_html = decoded
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                try:
                    decoded = payload.decode(charset, errors="replace")
                except Exception:
                    decoded = payload.decode("latin1", errors="replace")
                if msg.get_content_type() == "text/html":
                    body_html = decoded
                else:
                    body_text = decoded
    except Exception:
        pass

    if not body_text and body_html:
        cleaned = re.sub(r'<style.*?>.*?</style>', '', body_html, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<script.*?>.*?</script>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        cleaned = html.unescape(cleaned)
        body_text = re.sub(r'\s+', ' ', cleaned).strip()

    combined = (body_text or "") + " " + (body_html or "")
    urls = re.findall(r'https?://[^\s<>"\']+', combined)
    seen = set()
    clean_urls = []
    for u in urls:
        u_clean = u.rstrip(".,;)>]")
        if u_clean not in seen:
            seen.add(u_clean)
            clean_urls.append(u_clean)

    return (body_text.strip(), clean_urls)


def _fetch_email_by_index(user: str, pwd: str, index: int = 1) -> Dict[str, Any]:
    """
    Connect to IMAP SSL, fetch email at reverse index (1 = newest),
    return dict with sender, subject, body, date, message_id, urls, headers.
    """
    if not user or not pwd:
        return {"error": "Gmail credentials missing."}

    mail = None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=20)
        mail.login(user, pwd)
        status, _ = mail.select("inbox")
        if status != "OK":
            return {"error": "Failed to select inbox."}

        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages or not messages[0]:
            return {"error": "No messages found in inbox."}

        mail_ids = messages[0].split()
        total_emails = len(mail_ids)
        if index < 1 or index > total_emails:
            return {"error": f"Index {index} out of range (total emails available: {total_emails})."}

        target_id = mail_ids[-index]
        status, data = mail.fetch(target_id, "(RFC822)")
        if status != "OK" or not data:
            return {"error": f"Failed to fetch email data for index {index}."}

        msg = None
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                break

        if not msg:
            return {"error": "Failed to parse email message bytes."}

        sender = _decode_mime_header(msg.get("From", "Unknown Sender"))
        subject = _decode_mime_header(msg.get("Subject", "No Subject"))
        date = msg.get("Date", "")
        message_id = msg.get("Message-ID", "")
        body, urls = _extract_body_and_urls(msg)

        headers = {}
        for h in ["From", "To", "Subject", "Date", "Reply-To", "Return-Path", "Received", "Authentication-Results", "Message-ID"]:
            val = msg.get(h)
            if val:
                headers[h] = _decode_mime_header(str(val))

        return {
            "sender": sender,
            "subject": subject,
            "date": date,
            "body": body,
            "message_id": message_id,
            "urls": urls,
            "headers": headers,
            "raw_msg": msg
        }
    except Exception as e:
        return {"error": f"IMAP Error: {str(e)}"}
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass


def _gemini_ask(prompt: str) -> str:
    """Send prompt to universal AI client (Gemini with automatic Groq failover)."""
    try:
        from friday_tools.ai_client import ask_ai
        res = ask_ai(prompt)
        if res:
            return res.strip()
        return "No response received from AI engine."
    except Exception as e:
        return f"AI Engine Error: {str(e)}"


def _send_smtp_email(user: str, pwd: str, to: str, subject: str, body: str, in_reply_to: str = "") -> str:
    """Send plain text email via Gmail SMTP with port 587 and 465 fallback and recipient guards."""
    if not to or "@" not in to:
        return "ERROR: Recipient address is invalid."

    blocked_domains = ["noreply", "no-reply", "google-noreply", "example.com", "test.com"]
    if any(b in to.lower() for b in blocked_domains):
        return f"BLOCKED: Refusing to send email to automated address '{to}'."

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to
    msg['Subject'] = subject
    if in_reply_to:
        msg['In-Reply-To'] = in_reply_to
        msg['References'] = in_reply_to
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(user, pwd)
            server.send_message(msg)
        return "SUCCESS"
    except Exception as e1:
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
                server.login(user, pwd)
                server.send_message(msg)
            return "SUCCESS"
        except Exception as e2:
            return f"SMTP Failure (587: {e1} | 465: {e2})"


# ==============================
# ASYNC TOOL FUNCTIONS
# ==============================

async def email_inbox_summary(count: int = 10, account: str = 'primary') -> str:
    """
    1. Connect to IMAP SSL imap.gmail.com
    2. Use GMAIL_USER_2/GMAIL_APP_PASSWORD_2 for 'primary', GMAIL_USER/GMAIL_APP_PASSWORD for 'secondary'
    3. Fetch last count emails from inbox
    4. For each: extract sender, subject, date, and first 100 chars of body
    5. Compile into a formatted summary
    6. Send the summary to Gemini for AI analysis
    7. Return AI-enhanced summary
    """
    user, pwd = _get_email_creds(account)
    if not user or not pwd:
        return f"Error: Credentials missing for account '{account}'."

    mail = None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=30)
        mail.login(user, pwd)
        status, _ = mail.select("inbox")
        if status != "OK":
            return "Error: Could not access inbox."

        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages or not messages[0]:
            return f"Inbox for {user} is empty."

        mail_ids = messages[0].split()
        total_emails = len(mail_ids)
        if total_emails == 0:
            return f"Inbox for {user} is empty."

        fetch_count = min(count, total_emails)
        selected_ids = mail_ids[-fetch_count:]

        summaries = []
        for idx, mail_id in enumerate(reversed(selected_ids), 1):
            try:
                status, data = mail.fetch(mail_id, "(RFC822)")
                if status == "OK" and data:
                    for response_part in data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            sender = _decode_mime_header(msg.get("From", "Unknown Sender"))
                            subject = _decode_mime_header(msg.get("Subject", "No Subject"))
                            date = msg.get("Date", "Unknown Date")
                            body, _ = _extract_body_and_urls(msg)
                            preview = (body[:100].replace('\n', ' ').strip() if body else "No text preview")
                            summaries.append(
                                f"Email #{idx}:\n"
                                f"From: {sender}\n"
                                f"Subject: {subject}\n"
                                f"Date: {date}\n"
                                f"Preview: {preview}"
                            )
                            break
            except Exception as e:
                summaries.append(f"Email #{idx}: [Failed to fetch: {e}]")

        compiled_text = "\n\n".join(summaries)

        prompt = (
            f"Summarize these emails. Flag any urgent ones. Categorize them (Personal, Work, Newsletters, Promotions, Important).\n\n"
            f"Email Inbox List ({len(summaries)} emails from {user}):\n\n{compiled_text}"
        )
        ai_analysis = _gemini_ask(prompt)

        return (
            f"📬 **Inbox Summary ({account.capitalize()} - {user})**\n\n"
            f"{ai_analysis}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 **Email Digest ({len(summaries)} emails):**\n\n{compiled_text}"
        )
    except Exception as e:
        return f"Error in email_inbox_summary: {str(e)}"
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass


async def email_draft_reply(index: int = 1, tone: str = 'professional', account: str = 'primary') -> str:
    """
    1. Fetch the email at reverse index (1=newest)
    2. Extract sender, subject, body
    3. Send to Gemini: Draft a tone reply
    4. Return the drafted reply (don't send it yet)
    """
    user, pwd = _get_email_creds(account)
    if not user or not pwd:
        return f"Error: Credentials missing for account '{account}'."

    try:
        fetched = _fetch_email_by_index(user, pwd, index=index)
        if "error" in fetched:
            return f"Error fetching email #{index}: {fetched['error']}"

        sender = fetched.get("sender", "Unknown")
        subject = fetched.get("subject", "No Subject")
        body = fetched.get("body", "")

        prompt = (
            f"Draft a {tone} reply to this email. Original from {sender} about: {subject}. "
            f"Body: {body[:500]}. Write a complete reply."
        )
        drafted_reply = _gemini_ask(prompt)
        return drafted_reply
    except Exception as e:
        return f"Error drafting reply: {str(e)}"


async def email_send_reply(index: int = 1, reply_text: str = '', account: str = 'primary') -> str:
    """
    1. Fetch original email at index to get sender address and subject
    2. Compose reply with 'Re: ' prefix on subject
    3. Send via SMTP using the account credentials
    4. Return confirmation
    """
    user, pwd = _get_email_creds(account)
    if not user or not pwd:
        return f"Error: Credentials missing for account '{account}'."

    if not reply_text or not reply_text.strip():
        return "Error: reply_text cannot be empty."

    try:
        fetched = _fetch_email_by_index(user, pwd, index=index)
        if "error" in fetched:
            return f"Error fetching email #{index}: {fetched['error']}"

        sender_header = fetched.get("sender", "")
        _, recipient_email = email.utils.parseaddr(sender_header)
        if not recipient_email:
            return f"Error: Could not determine recipient address from '{sender_header}'."

        orig_subject = fetched.get("subject", "No Subject").strip()
        if orig_subject.lower().startswith("re:"):
            reply_subject = orig_subject
        else:
            reply_subject = f"Re: {orig_subject}"

        message_id = fetched.get("message_id", "")

        res = _send_smtp_email(
            user=user,
            pwd=pwd,
            to=recipient_email,
            subject=reply_subject,
            body=reply_text,
            in_reply_to=message_id
        )

        if res == "SUCCESS":
            return f"✅ Reply sent successfully to {recipient_email} with subject '{reply_subject}'."
        return f"Error sending reply: {res}"
    except Exception as e:
        return f"Error in email_send_reply: {str(e)}"


async def email_smart_compose(to: str, about: str, tone: str = 'professional', account: str = 'primary') -> str:
    """
    1. Send to Gemini: Compose a tone email to to about: about. Write subject line and body.
    2. Parse subject and body from response
    3. Send via SMTP
    4. Return confirmation with the composed email
    """
    user, pwd = _get_email_creds(account)
    if not user or not pwd:
        return f"Error: Credentials missing for account '{account}'."

    if not to or not to.strip():
        return "Error: Recipient email ('to') is required."

    try:
        prompt = (
            f"Compose a {tone} email to {to} about: {about}. Write subject line and body.\n\n"
            f"Format requirements:\n"
            f"Subject: <Subject line here>\n\n"
            f"<Email body here>"
        )
        ai_response = _gemini_ask(prompt)
        if not ai_response or ai_response.startswith("Gemini Error:"):
            return f"Error generating email with Gemini: {ai_response}"

        subject = f"Regarding {about}"
        body = ai_response.strip()

        lines = body.splitlines()
        for idx, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean.lower().startswith("subject:"):
                subj_val = line_clean[8:].strip()
                if subj_val:
                    subject = subj_val
                body = "\n".join(lines[idx+1:]).strip()
                break

        res = _send_smtp_email(
            user=user,
            pwd=pwd,
            to=to,
            subject=subject,
            body=body
        )

        if res == "SUCCESS":
            return (
                f"✅ Email successfully composed and sent to {to}!\n\n"
                f"**From:** {user}\n"
                f"**Subject:** {subject}\n\n"
                f"**Body:**\n{body}"
            )
        return f"Error sending composed email: {res}\n\nComposed draft:\nSubject: {subject}\n\n{body}"
    except Exception as e:
        return f"Error in email_smart_compose: {str(e)}"


async def email_extract_otp(account: str = 'primary') -> str:
    """
    1. Connect IMAP
    2. Search for recent emails with subjects containing 'OTP', 'verification', 'code', 'confirm'
    3. Fetch latest 5 matching
    4. Regex extract 4-8 digit codes from body
    5. Return all found OTPs with their sources
    """
    user, pwd = _get_email_creds(account)
    if not user or not pwd:
        return f"Error: Credentials missing for account '{account}'."

    mail = None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=25)
        mail.login(user, pwd)
        status, _ = mail.select("inbox")
        if status != "OK":
            return "Error: Could not access inbox."

        search_terms = ['OTP', 'verification', 'code', 'confirm']
        matching_ids = set()

        for term in search_terms:
            try:
                typ, data = mail.search(None, f'(SUBJECT "{term}")')
                if typ == "OK" and data and data[0]:
                    for id_str in data[0].split():
                        try:
                            matching_ids.add(int(id_str))
                        except ValueError:
                            pass
            except Exception:
                pass

        if not matching_ids:
            return "❌ No emails found with subjects containing 'OTP', 'verification', 'code', or 'confirm'."

        sorted_ids = sorted(list(matching_ids))
        latest_ids = sorted_ids[-5:]
        latest_ids.reverse()

        results = []
        for mail_id in latest_ids:
            try:
                status, data = mail.fetch(str(mail_id), "(RFC822)")
                if status == "OK" and data:
                    for response_part in data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            sender = _decode_mime_header(msg.get("From", "Unknown Sender"))
                            subject = _decode_mime_header(msg.get("Subject", "No Subject"))
                            date = msg.get("Date", "Unknown Date")
                            body, _ = _extract_body_and_urls(msg)

                            targeted = re.findall(
                                r'(?:otp|code|verification|passcode|pin|confirm)[:\s\-\#]*([0-9]{4,8})\b',
                                body,
                                re.IGNORECASE
                            )
                            all_digits = re.findall(r'\b[0-9]{4,8}\b', body)

                            codes = []
                            candidates = targeted if targeted else all_digits
                            for c in candidates:
                                if c not in codes:
                                    codes.append(c)

                            if codes:
                                results.append(
                                    f"🔑 **Code(s):** {', '.join(codes)}\n"
                                    f"   • **Source:** {sender}\n"
                                    f"   • **Subject:** {subject}\n"
                                    f"   • **Date:** {date}"
                                )
                            else:
                                results.append(
                                    f"⚠️ **No numeric code detected**\n"
                                    f"   • **Source:** {sender}\n"
                                    f"   • **Subject:** {subject}\n"
                                    f"   • **Date:** {date}"
                                )
                            break
            except Exception as e:
                results.append(f"❌ Error reading message ID {mail_id}: {e}")

        if not results:
            return "No OTP or verification codes could be extracted."

        return f"🔐 **Extracted OTP / Verification Codes ({account.capitalize()} - {user}):**\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Error extracting OTP: {str(e)}"
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass


async def email_search(query: str, count: int = 5, account: str = 'primary') -> str:
    """
    1. IMAP search with query as subject filter
    2. Return matching emails (sender, subject, date, preview)
    """
    user, pwd = _get_email_creds(account)
    if not user or not pwd:
        return f"Error: Credentials missing for account '{account}'."

    if not query or not query.strip():
        return "Error: Search query cannot be empty."

    mail = None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=25)
        mail.login(user, pwd)
        status, _ = mail.select("inbox")
        if status != "OK":
            return "Error: Could not access inbox."

        clean_query = query.replace('"', '')
        status, data = mail.search(None, f'SUBJECT "{clean_query}"')
        if status != "OK" or not data or not data[0]:
            return f"No emails found matching subject '{query}'."

        mail_ids = [int(x) for x in data[0].split() if x.isdigit()]
        if not mail_ids:
            return f"No emails found matching subject '{query}'."

        target_ids = sorted(mail_ids)[-count:]
        target_ids.reverse()

        matches = []
        for idx, mail_id in enumerate(target_ids, 1):
            try:
                status, fetch_data = mail.fetch(str(mail_id), "(RFC822)")
                if status == "OK" and fetch_data:
                    for response_part in fetch_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            sender = _decode_mime_header(msg.get("From", "Unknown Sender"))
                            subject = _decode_mime_header(msg.get("Subject", "No Subject"))
                            date = msg.get("Date", "Unknown Date")
                            body, _ = _extract_body_and_urls(msg)
                            preview = (body[:150].replace('\n', ' ').strip() if body else "No text preview")

                            matches.append(
                                f"[{idx}] From: {sender}\n"
                                f"    Subject: {subject}\n"
                                f"    Date: {date}\n"
                                f"    Preview: {preview}..."
                            )
                            break
            except Exception as e:
                matches.append(f"[{idx}] Error reading email: {e}")

        return (
            f"🔍 **Search Results for '{query}' ({len(matches)} matching email(s) in {user}):**\n\n"
            + "\n\n".join(matches)
        )
    except Exception as e:
        return f"Error searching emails: {str(e)}"
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass


async def email_detect_phishing(index: int = 1, account: str = 'primary') -> str:
    """
    1. Fetch email at index
    2. Extract all URLs, sender domain, headers
    3. Send to Gemini for phishing indicators analysis
    4. Return Gemini's phishing analysis
    """
    user, pwd = _get_email_creds(account)
    if not user or not pwd:
        return f"Error: Credentials missing for account '{account}'."

    try:
        fetched = _fetch_email_by_index(user, pwd, index=index)
        if "error" in fetched:
            return f"Error fetching email #{index}: {fetched['error']}"

        sender = fetched.get("sender", "Unknown")
        subject = fetched.get("subject", "No Subject")
        body = fetched.get("body", "")
        urls = fetched.get("urls", [])
        headers = fetched.get("headers", {})

        _, sender_email = email.utils.parseaddr(sender)
        sender_domain = sender_email.split('@')[-1] if '@' in sender_email else 'Unknown'

        headers_str = "\n".join(f"{k}: {v}" for k, v in headers.items())
        urls_str = "\n".join(urls) if urls else "None detected"

        prompt = (
            f"Analyze this email for phishing indicators. Check: sender domain legitimacy, suspicious URLs, "
            f"urgency language, grammar errors, requesting credentials.\n\n"
            f"Sender Domain: {sender_domain}\n"
            f"Extracted URLs:\n{urls_str}\n\n"
            f"Headers Summary:\n{headers_str}\n\n"
            f"Email from: {sender}, Subject: {subject}, Body: {body[:1000]}.\n\n"
            f"Verdict: SAFE / SUSPICIOUS / DANGEROUS"
        )
        analysis = _gemini_ask(prompt)

        return (
            f"🛡️ **Phishing Security Analysis (Email #{index} in {user})**\n\n"
            f"• **Sender:** {sender}\n"
            f"• **Domain:** {sender_domain}\n"
            f"• **Subject:** {subject}\n"
            f"• **Links Found ({len(urls)}):** {', '.join(urls[:3]) if urls else 'None'}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**AI Security Assessment:**\n{analysis}"
        )
    except Exception as e:
        return f"Error in email_detect_phishing: {str(e)}"


__all__ = [
    "email_inbox_summary",
    "email_draft_reply",
    "email_send_reply",
    "email_smart_compose",
    "email_extract_otp",
    "email_search",
    "email_detect_phishing",
]
