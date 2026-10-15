"""
ULTRON Developer Toolkit & API Utilities Engine
Instant developer utilities: Regex debugger, JWT claim decoder, cron schedule explainer, curl-to-python translator, and JSON formatter.
"""

import re
import json
import base64
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


async def dev_regex_tester(pattern: str, test_string: str) -> str:
    r"""
    Tests and debugs regular expressions with match position and capture group breakdown.
    
    Args:
        pattern: Regex pattern (e.g. r'(\w+)@([\w\.]+)', r'\b\d{3}-\d{2}-\d{4}\b').
        test_string: Sample string to test against.
    """
    try:
        regex = re.compile(pattern)
        matches = list(regex.finditer(test_string))
        if not matches:
            return f"❌ [NO MATCH] Pattern `r'{pattern}'` found 0 matches in test string."

        lines = [f"✅ [REGEX MATCH SUCCESS] Found **{len(matches)}** match(es) for `r'{pattern}'`:"]
        for idx, m in enumerate(matches[:10], 1):
            span_str = f"span [{m.start()}:{m.end()}]"
            lines.append(f"\n  **Match {idx}** (`{m.group(0)}` at {span_str}):")
            if m.groups():
                for g_idx, g_val in enumerate(m.groups(), 1):
                    lines.append(f"    • Group {g_idx}: `{g_val}`")
            if m.groupdict():
                for k, v in m.groupdict().items():
                    lines.append(f"    • Named Group `(?P<{k}>)`: `{v}`")

        return "\n".join(lines)
    except re.error as e:
        return f"⚠️ [REGEX SYNTAX ERROR]: {e}"


async def dev_jwt_decoder(token: str) -> str:
    """
    Decodes and inspects JSON Web Tokens (JWT) headers, payload claims, and expiration timestamps.
    
    Args:
        token: Raw JWT string (header.payload.signature).
    """
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return "❌ [INVALID JWT] JWT must consist of exactly 3 dot-separated parts (Header.Payload.Signature)."

        def _b64_decode(data: str) -> dict:
            padded = data + "=" * (-len(data) % 4)
            decoded_bytes = base64.urlsafe_b64decode(padded.encode())
            return json.loads(decoded_bytes.decode())

        header = _b64_decode(parts[0])
        payload = _b64_decode(parts[1])

        # Expiry inspection
        exp_info = ""
        if "exp" in payload:
            exp_ts = payload["exp"]
            exp_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
            now_dt = datetime.now(timezone.utc)
            is_expired = now_dt > exp_dt
            diff = abs((exp_dt - now_dt).total_seconds())
            if is_expired:
                exp_info = f"\n⚠️ **STATUS: EXPIRED** (Expired {int(diff // 60)} minutes ago at `{exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}`)"
            else:
                exp_info = f"\n✅ **STATUS: VALID** (Expires in {int(diff // 60)} minutes at `{exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}`)"

        return (
            f"🔐 **JWT TOKEN INSPECTOR & CLAIM DECODER:**\n"
            f"{exp_info}\n\n"
            f"📋 **Header (Algorithm & Type):**\n```json\n{json.dumps(header, indent=2)}\n```\n\n"
            f"📦 **Payload Claims:**\n```json\n{json.dumps(payload, indent=2)}\n```"
        )
    except Exception as e:
        return f"⚠️ [JWT DECODE FAILED]: {e}"


async def dev_cron_explainer(cron_expression: str) -> str:
    """
    Translates standard 5-field cron expressions (minute hour day month day-of-week) into clear human-readable schedules.
    
    Args:
        cron_expression: 5-part cron string (e.g. '*/5 * * * *', '0 9 * * 1-5', '30 2 1 * *').
    """
    parts = cron_expression.strip().split()
    if len(parts) != 5:
        return f"Cron expression must contain 5 fields: `minute hour day month day-of-week`. Received {len(parts)} fields."

    m, h, dom, mon, dow = parts

    dow_names = {"0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed", "4": "Thu", "5": "Fri", "6": "Sat", "7": "Sun"}
    
    desc = []
    if m == "*" and h == "*":
        desc.append("Every minute")
    elif m.startswith("*/"):
        desc.append(f"Every {m[2:]} minutes")
    elif m == "0" and h == "*":
        desc.append("Every hour on the hour")
    elif h != "*" and m != "*":
        desc.append(f"At {h.zfill(2)}:{m.zfill(2)}")
    else:
        desc.append(f"At minute {m}")

    if dow != "*":
        if "-" in dow:
            s, e = dow.split("-")
            desc.append(f"Monday through Friday" if dow == "1-5" else f"from {dow_names.get(s, s)} to {dow_names.get(e, e)}")
        else:
            desc.append(f"on {dow_names.get(dow, dow)}")

    if dom != "*":
        desc.append(f"on day {dom} of the month")

    if mon != "*":
        desc.append(f"in month {mon}")

    readable = ", ".join(desc)
    return f"⏰ **CRON SCHEDULE TRANSLATION (`{cron_expression}`):**\n• **Human Meaning:** **{readable}**"


async def dev_curl_to_python(curl_command: str) -> str:
    """
    Converts raw bash/cmd `curl` commands into clean, asynchronous Python `httpx` or `requests` code.
    
    Args:
        curl_command: Full curl string.
    """
    try:
        # Extract URL
        url_match = re.search(r"curl\s+(?:-[A-Za-z\s'\"]+\s+)?['\"]?(https?://[^\s'\"]+)", curl_command)
        url = url_match.group(1) if url_match else "https://api.example.com/endpoint"

        # Extract Method
        method = "GET"
        if "-X POST" in curl_command or "--request POST" in curl_command or "-d " in curl_command:
            method = "POST"
        elif "-X PUT" in curl_command:
            method = "PUT"
        elif "-X DELETE" in curl_command:
            method = "DELETE"

        # Extract Headers
        headers = {}
        for h in re.findall(r"(?:-H|--header)\s+['\"]([^'\"]+)['\"]", curl_command):
            if ":" in h:
                k, v = h.split(":", 1)
                headers[k.strip()] = v.strip()

        # Extract Data
        data_match = re.search(r"(?:-d|--data|--data-raw)\s+['\"]([^'\"]+)['\"]", curl_command)
        data_body = data_match.group(1) if data_match else None

        code_lines = [
            "import httpx",
            "import asyncio",
            "",
            "async def make_request():",
            f"    url = '{url}'",
        ]
        if headers:
            code_lines.append(f"    headers = {json.dumps(headers, indent=8).strip()}")
        else:
            code_lines.append("    headers = {}")

        if data_body:
            try:
                json_obj = json.loads(data_body)
                code_lines.append(f"    payload = {json.dumps(json_obj, indent=8).strip()}")
                code_lines.append(f"    async with httpx.AsyncClient() as client:")
                code_lines.append(f"        response = await client.{method.lower()}(url, headers=headers, json=payload)")
            except Exception:
                code_lines.append(f"    data = '{data_body}'")
                code_lines.append(f"    async with httpx.AsyncClient() as client:")
                code_lines.append(f"        response = await client.{method.lower()}(url, headers=headers, content=data)")
        else:
            code_lines.append(f"    async with httpx.AsyncClient() as client:")
            code_lines.append(f"        response = await client.{method.lower()}(url, headers=headers)")

        code_lines.append("        return response.status_code, response.text")

        generated_code = "\n".join(code_lines)
        return f"🐍 **PYTHON HTTPX TRANSLATION:**\n```python\n{generated_code}\n```"
    except Exception as e:
        return f"⚠️ [CURL TRANSLATION FAILED]: {e}"


async def dev_hash_generator(text: str) -> str:
    """
    Generates MD5, SHA-1, SHA-256, SHA-512, and Keccak/BLAKE2b cryptographic hashes for any text string.
    
    Args:
        text: Plaintext string to hash.
    """
    b = text.encode("utf-8")
    return (
        f"🔒 **CRYPTOGRAPHIC HASH MATRIX (`{text[:30]}...`):**\n"
        f"• **MD5:** `{hashlib.md5(b).hexdigest()}`\n"
        f"• **SHA-1:** `{hashlib.sha1(b).hexdigest()}`\n"
        f"• **SHA-256:** `{hashlib.sha256(b).hexdigest()}`\n"
        f"• **SHA-512:** `{hashlib.sha512(b).hexdigest()}`\n"
        f"• **BLAKE2b:** `{hashlib.blake2b(b).hexdigest()}`"
    )
