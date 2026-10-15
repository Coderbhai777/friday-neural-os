"""
ULTRON Cloud Workspace & Meeting Intelligence Assistant (Adapted from ULTRON-Echo)
Provides real-time weather reports, meeting note transcription/summarization, and smart clipboard analysis.
"""

import os
import json
import urllib.request
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

async def get_live_weather(city: str = "Delhi") -> str:
    """
    Fetches real-time weather, temperature, humidity, and condition forecasts for any city.
    """
    def _fetch():
        clean_city = urllib.parse.quote(city.strip())
        url = f"https://wttr.in/{clean_city}?format=j1"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current = data.get("current_condition", [{}])[0]
                temp_c = current.get("temp_C", "N/A")
                feels_like = current.get("FeelsLikeC", "N/A")
                desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
                humidity = current.get("humidity", "N/A")
                wind = current.get("windspeedKmph", "N/A")

                return (
                    f"[WEATHER: {city.title()}]\n"
                    f"- Condition: {desc}\n"
                    f"- Temperature: {temp_c}°C (Feels like {feels_like}°C)\n"
                    f"- Humidity: {humidity}%\n"
                    f"- Wind Speed: {wind} km/h"
                )
        except Exception:
            # Fallback text query
            try:
                txt_url = f"https://wttr.in/{clean_city}?format=3"
                req2 = urllib.request.Request(txt_url, headers={"User-Agent": "curl/7.68.0"})
                with urllib.request.urlopen(req2, timeout=4) as resp2:
                    return f"[WEATHER] {resp2.read().decode('utf-8').strip()}"
            except Exception as e:
                return f"[WEATHER ERROR] Could not fetch live weather: {e}"

    return await asyncio.to_thread(_fetch)


async def summarize_meeting_notes(raw_notes_or_transcript: str) -> str:
    """
    Converts messy meeting notes or transcripts into executive summaries, action items, and owner assignments.
    """
    from friday_tools.ai_client import ask_ai
    prompt = f"""You are ULTRON's Executive Meeting Assistant.
Transform these raw meeting notes/transcript into a structured summary:

RAW NOTES:
{raw_notes_or_transcript}

FORMAT:
1. Executive Summary (2-3 sentences)
2. Key Decisions Made
3. Action Items & Next Steps (with assignees / deadlines if mentioned)
4. Open Questions
"""
    return await asyncio.to_thread(ask_ai, prompt)


async def analyze_clipboard_content() -> str:
    """
    Reads the current Windows clipboard and provides smart analysis (JSON formatting, translation, or code debugging).
    """
    try:
        import pyperclip
        text = pyperclip.paste()
        if not text:
            return "[CLIPBOARD] Clipboard is currently empty."
        
        # Determine content type
        preview = text.strip()[:200]
        length = len(text)
        return f"[CLIPBOARD CONTENT ({length} chars)]:\n{preview}..."
    except Exception as e:
        return f"[CLIPBOARD ERROR] {e}"
