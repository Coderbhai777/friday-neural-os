"""
ULTRON Media, Audio & Knowledge Master Pack
- youtube_video_downloader_and_mp3: High-speed YouTube video and 320kbps MP3 downloader
- voice_memo_transcribe_and_summarize: Transcribes and structures audio recordings & voice memos
- smart_clipboard_history_search: Persistent indexed clipboard history search
- spotify_smart_search_and_play: Direct Spotify track/album/mood search and playback
"""

import os
import sys
import time
import json
import webbrowser
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

import pyperclip

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


DOWNLOADS_DIR = Path.home() / "Downloads"
MUSIC_DIR = Path.home() / "Music"
CLIPBOARD_LOG = Path.home() / "Documents" / "ULTRON_Data" / "clipboard_history.json"
CLIPBOARD_LOG.parent.mkdir(parents=True, exist_ok=True)


def _log_clipboard_entry(text: str):
    """Saves non-empty clipboard text to persistent history."""
    if not text or len(text.strip()) < 2:
        return
    try:
        history = []
        if CLIPBOARD_LOG.exists():
            history = json.loads(CLIPBOARD_LOG.read_text(encoding="utf-8"))
        
        # Deduplicate recent entry
        if history and history[0].get("content") == text:
            return
        
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": text[:5000],
            "chars": len(text)
        }
        history.insert(0, entry)
        # Keep last 150 items
        history = history[:150]
        CLIPBOARD_LOG.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


async def youtube_video_downloader_and_mp3(
    url: str = "",
    extract_audio: bool = False,
    audio_only: bool = False,
    quality: str = "best",
    **kwargs
) -> str:
    """
    Downloads YouTube videos (1080p/4K) or extracts high-bitrate 320kbps MP3 audio files.
    """
    actual_url = (url or kwargs.get("link") or kwargs.get("video_url") or "").strip()
    if not actual_url:
        return "[WARN] Please provide a valid YouTube video URL."

    is_audio = extract_audio or audio_only or kwargs.get("mp3", False) or ("music" in kwargs.get("type", "").lower())
    dest_folder = MUSIC_DIR if is_audio else DOWNLOADS_DIR

    if not yt_dlp:
        return "[ERROR] yt_dlp library is not installed."

    try:
        ydl_opts = {
            "outtmpl": str(dest_folder / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        if is_audio:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }] if shutil_which("ffmpeg") else []
            })
        else:
            ydl_opts.update({
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(actual_url, download=True)
            title = info.get("title", "YouTube Media")
            duration_sec = info.get("duration", 0)
            duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"

        media_type = "320kbps MP3 Audio" if is_audio else "MP4 Video"
        return (
            f"[DOWNLOAD COMPLETE]\n"
            f"• Title: {title}\n"
            f"• Type: {media_type}\n"
            f"• Duration: {duration_str}\n"
            f"• Saved To: {dest_folder}"
        )
    except Exception as e:
        return f"[ERROR] Failed to download YouTube media: {e}"


def shutil_which(cmd):
    import shutil
    return shutil.which(cmd)


async def voice_memo_transcribe_and_summarize(
    audio_file: str = "",
    file_path: str = "",
    **kwargs
) -> str:
    """
    Transcribes audio files (voice memos, lectures, meetings) and generates structured action item summaries.
    """
    actual_path = (audio_file or file_path or kwargs.get("path") or "").strip()
    if not actual_path:
        return "[WARN] Please specify the path to the audio file."

    p = Path(actual_path)
    if not p.exists():
        return f"[ERROR] Audio file not found at: {p}"

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return "[ERROR] GEMINI_API_KEY is not configured."

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)

        # Upload audio to Gemini Multimodal File API
        uploaded_file = genai.upload_file(path=str(p))

        # Wait for processing if large
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_file = genai.get_file(uploaded_file.name)

        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            "You are an expert executive transcriptionist and intelligence analyst. "
            "1. Provide a verbatim or accurate transcription of this audio. "
            "2. Provide an Executive Summary with Key Takeaways. "
            "3. Extract any Action Items, Deadlines, and Notable Quotes in bullet format."
        )

        response = model.generate_content([prompt, uploaded_file])
        if response and response.text:
            return f"[AUDIO INTELLIGENCE & TRANSCRIPT: {p.name}]\n\n{response.text.strip()}"

        return "[WARN] Gemini completed audio processing without output text."
    except Exception as e:
        return f"[ERROR] Audio transcription error: {e}"


async def smart_clipboard_history_search(
    keyword: str = "",
    query: str = "",
    limit: int = 8,
    **kwargs
) -> str:
    """
    Searches or retrieves recent entries from persistent clipboard history.
    """
    # Grab current clipboard and auto-log
    try:
        curr = pyperclip.paste()
        if curr:
            _log_clipboard_entry(curr)
    except Exception:
        pass

    search_term = (keyword or query or kwargs.get("search") or "").strip().lower()

    if not CLIPBOARD_LOG.exists():
        return "[INFO] Clipboard history is currently empty."

    try:
        history = json.loads(CLIPBOARD_LOG.read_text(encoding="utf-8"))
        if not history:
            return "[INFO] No entries in clipboard history."

        matches = []
        for item in history:
            content = item.get("content", "")
            ts = item.get("timestamp", "")
            if not search_term or (search_term in content.lower()):
                snippet = content.replace("\n", " ").strip()
                if len(snippet) > 100:
                    snippet = snippet[:97] + "..."
                matches.append(f"- [{ts}] {snippet}")
                if len(matches) >= limit:
                    break

        if not matches:
            return f"[INFO] No clipboard entries matched keyword '{search_term}'."

        header = f"[CLIPBOARD HISTORY - Matches for '{search_term}']" if search_term else "[RECENT CLIPBOARD HISTORY]"
        return f"{header}\n" + "\n".join(matches)
    except Exception as e:
        return f"[ERROR] Could not search clipboard history: {e}"


async def spotify_smart_search_and_play(
    query: str = "",
    song: str = "",
    mood: str = "",
    artist: str = "",
    **kwargs
) -> str:
    """
    Searches for tracks, artists, or mood playlists and triggers Spotify playback.
    """
    search_q = (query or song or kwargs.get("track") or "").strip()
    if mood:
        search_q = f"{search_q} {mood} vibe".strip()
    if artist:
        search_q = f"{search_q} {artist}".strip()

    if not search_q:
        search_q = "Top Hits 2026"

    # Launch Spotify via protocol handler
    spotify_uri = f"spotify:search:{search_q}"
    web_fallback = f"https://open.spotify.com/search/{requests.utils.quote(search_q)}"

    try:
        # Launch Windows Spotify client directly
        os.startfile(spotify_uri)
        return f"[SPOTIFY PLAYBACK]\n• Searching & Playing: '{search_q}'\n• Protocol: {spotify_uri}\n• Enjoy the music, Shivansh!"
    except Exception:
        try:
            webbrowser.open(web_fallback)
            return f"[SPOTIFY WEB]\n• Opened Spotify Search: '{search_q}' in browser."
        except Exception as e:
            return f"[ERROR] Could not open Spotify: {e}"
