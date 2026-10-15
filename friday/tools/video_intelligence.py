"""
ULTRON YouTube & Video Intelligence Extractor
Extracts transcripts, chapters, executive summaries, downloads MP3 audio clips,
and performs natural language Q&A over video content.
"""

import os
import re
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
MEDIA_DIR = Path.home() / "Documents" / "ULTRON_Recordings"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def _get_gemini_model():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(DATA_DIR / ".env")
        api_key = os.getenv("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def _extract_video_id(url: str) -> str:
    """Extracts YouTube 11-char video ID from various URL formats."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'embed\/([0-9A-Za-z_-]{11})',
        r'shorts\/([0-9A-Za-z_-]{11})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return url.strip()


def _fetch_transcript_text(video_id: str) -> str:
    """Fetches full transcript using youtube_transcript_api with yt-dlp fallback."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item["text"] for item in transcript_list])
        return full_text
    except Exception:
        pass
        
    # Fallback via yt-dlp metadata
    try:
        import yt_dlp
        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            desc = info.get("description", "")
            title = info.get("title", "")
            return f"Title: {title}\nDescription: {desc}"
    except Exception as err:
        return f"[Error fetching transcript]: {err}"


async def youtube_summarize(url: str, detail_level: str = "comprehensive") -> str:
    """
    Summarizes any YouTube video into an executive breakdown, key insights, and actionable timestamps.
    """
    vid_id = _extract_video_id(url)
    transcript = _fetch_transcript_text(vid_id)
    
    if transcript.startswith("[Error fetching"):
        return f"Could not retrieve video subtitles or transcript: {transcript}"
        
    prompt = f"""You are an Expert Video Intelligence Analyst.
Analyze the following transcript from YouTube Video ID '{vid_id}':

TRANSCRIPT EXCERPT:
{transcript[:30000]}

Provide a {detail_level} summary formatted as follows:
1. EXECUTIVE SUMMARY (Core thesis and main takeaway in 2-3 sentences)
2. KEY HIGHLIGHTS & CHAPTER BREAKDOWN (Bullet points of main concepts)
3. NOTABLE QUOTES / CODE / DATA POINTS
4. CRITICAL ACTION ITEMS / LESSONS"""

    try:
        model = _get_gemini_model()
        summary = model.generate_content(prompt).text
        return f"### 🎬 YouTube Video Summary (ID: {vid_id})\n\n{summary}"
    except Exception as e:
        return f"Error summarizing video: {e}"


async def youtube_ask_question(url: str, question: str) -> str:
    """
    Answers specific questions regarding what was spoken in a YouTube video.
    """
    vid_id = _extract_video_id(url)
    transcript = _fetch_transcript_text(vid_id)
    
    if transcript.startswith("[Error fetching"):
        return f"Could not retrieve video text: {transcript}"
        
    prompt = f"""You are a Video Intelligence Copilot.
The user is asking a question about this YouTube video:

QUESTION: {question}

VIDEO TRANSCRIPT:
{transcript[:35000]}

Answer the user's question directly, accurately, and cite specific context or timestamps from the transcript where possible."""

    try:
        model = _get_gemini_model()
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Error answering video question: {e}"


async def youtube_download_audio(url: str, filename: str = "") -> str:
    """
    Downloads high-quality audio (MP3) from a YouTube video into ULTRON Recordings.
    """
    try:
        import yt_dlp
        
        safe_name = filename.strip() if filename else f"yt_audio_{int(time.time())}"
        out_tmpl = str(MEDIA_DIR / f"{safe_name}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_tmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        final_path = MEDIA_DIR / f"{safe_name}.mp3"
        return f"Audio downloaded successfully: {final_path}"
    except Exception as e:
        return f"Error downloading audio: {e}"
