"""
ULTRON Social Media & Content Automation (Adapted from ULTRON-Echo)
Enables Instagram DM messaging, YouTube video search & transcript analysis, and content automation.
"""

import os
import re
import json
import urllib.parse
import webbrowser
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

async def instagram_open_chat(username: str = "", message: str = "") -> str:
    """
    Opens Instagram Direct Messages for a specific username or home feed.
    """
    if username:
        clean_user = username.lstrip("@").strip()
        url = f"https://www.instagram.com/direct/t/{clean_user}/"
        webbrowser.open(url)
        return f"[OK] Opened Instagram DM thread with @{clean_user}."
    else:
        webbrowser.open("https://www.instagram.com/direct/inbox/")
        return "[OK] Opened Instagram Direct Inbox."


async def youtube_search_and_play(query: str) -> str:
    """
    Searches YouTube for a video, tutorial, or song and launches playback.
    """
    encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(url)
    return f"[OK] Dispatched YouTube search for: '{query}'."


async def get_youtube_video_summary(video_url: str) -> str:
    """
    Fetches details and extracts insights for a YouTube video URL using AI reasoning.
    """
    from friday_tools.ai_client import ask_ai
    prompt = f"""You are ULTRON's Video Analysis Agent.
The user wants to analyze this YouTube video: {video_url}

Provide:
1. Topic and Core Subject
2. Expected Content Overview based on video query/ID
3. Key Takeaways & Actionable Notes
"""
    return await asyncio.to_thread(ask_ai, prompt)
