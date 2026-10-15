import os
import subprocess
import time
import webbrowser
import requests
import re
import urllib.request
from typing import Optional

# ==============================
# MEDIA CONTROL
# ==============================

# Monkeypatch for youtubesearchpython compatibility with newer httpx

# Monkeypatch for youtubesearchpython compatibility with newer httpx (0.28.0+)
try:
    import httpx
    # Patch Client.request which is used by most httpx methods (get, post, etc.)
    _orig_client_request = httpx.Client.request
    def _patched_client_request(self, method, url, **kwargs):
        if 'proxies' in kwargs:
            del kwargs['proxies']
        return _orig_client_request(self, method, url, **kwargs)
    httpx.Client.request = _patched_client_request

    # Patch AsyncClient.request just in case
    if hasattr(httpx, 'AsyncClient'):
        _orig_async_request = httpx.AsyncClient.request
        async def _patched_async_request(self, method, url, **kwargs):
            if 'proxies' in kwargs:
                del kwargs['proxies']
            return await _orig_async_request(self, method, url, **kwargs)
        httpx.AsyncClient.request = _patched_async_request

    # Patch top-level functions too for safety
    _orig_post = httpx.post
    def _patched_post(url, **kwargs):
        if 'proxies' in kwargs:
            del kwargs['proxies']
        return _orig_post(url, **kwargs)
    httpx.post = _patched_post
except (ImportError, Exception):
    pass


async def play_music(song: str) -> str:
    # "Web browser dot open trick" -> Finding the exact video and opening it
    try:
        from youtubesearchpython import VideosSearch
        videosSearch = VideosSearch(song, limit=1)
        results = videosSearch.result()['result']
        
        if results:
            first_video = results[0]
            url = first_video['link']
            title = first_video['title']
            webbrowser.open(url)
            return f"✅ Playing '{title}' on YouTube: {url}"
        else:
            # Fallback to search results if no specific video found
            query = song.replace(" ", "+")
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            return f"No direct video found. Opened search results for {song}"
            
    except Exception as e:
        # Fallback to simple search on error
        query = song.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        return f"Error: {e}. Opening search instead."

async def share_youtube_video_background(query: str, phone: str) -> str:
    """
    Searches for a YouTube video and shares the link via WhatsApp in the background.
    """
    try:
        from youtubesearchpython import VideosSearch
        videosSearch = VideosSearch(query, limit=1)
        results = videosSearch.result()['result']
        
        if results:
            video = results[0]
            link = video['link']
            title = video['title']
            
            # Use background WhatsApp tool
            from .communication import send_whatsapp_message_background
            # Note: We need to handle this call properly since it's also a tool
            # But here we can call it directly as a function or use ADB
            
            # Construct message
            message = f"Hey, check out this video: {title} - {link}"
            
            # Direct ADB call for background execution
            from .communication import adb_cmd
            adb_cmd(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", f"https://api.whatsapp.com/send?phone={phone}&text={message}"])
            time.sleep(3)
            adb_cmd(["shell", "input", "tap", "1000", "2100"]) 
            
            return f"✅ Shared '{title}' to {phone} in the background."
        else:
            return f"❌ Could not find a video for '{query}'"
    except Exception as e:
        return f"❌ Error sharing video: {e}"

async def get_youtube_video_link(query: str) -> str:
    """
    Searches YouTube and returns only the link of the first result.
    Useful for 'Friday, get me the link for [video]'.
    """
    try:
        from youtubesearchpython import VideosSearch
        videosSearch = VideosSearch(query, limit=1)
        results = videosSearch.result()['result']
        if results:
            video = results[0]
            return f"🔗 Link for '{video['title']}': {video['link']}"
        return f"❌ Could not find a link for '{query}'"
    except Exception as e:
        return f"❌ Error: {e}"

# Global cache for video selection
LAST_SEARCH_RESULTS = []

async def youtube_search_results(query: str) -> str:
    global LAST_SEARCH_RESULTS
    try:
        from youtubesearchpython import VideosSearch
        videosSearch = VideosSearch(query, limit=5)
        results = videosSearch.result()['result']
        
        LAST_SEARCH_RESULTS = results
        
        output = []
        for i, video in enumerate(results):
            # Explicitly formatting the response to highlight links as requested
            title = video['title']
            link = video['link']
            duration = video.get('duration', 'N/A')
            output.append(f"{i+1}. {title} ({duration})\n   🔗 {link}")
        
        return "📺 Search Results:\n" + "\n".join(output)
    except Exception as e:
        return f"Error searching YouTube: {e}"

async def select_video_by_index(index: int) -> str:
    global LAST_SEARCH_RESULTS
    if not LAST_SEARCH_RESULTS:
        return "❌ No recent search results found. Please search for a video first."
    
    try:
        # The user said: "When I say open the second video, it's doing the first video"
        # This implies index alignment. If LLM extracts "2", index=2.
        # Python list is 0-indexed. So index 1 = element 0 (first), index 2 = element 1 (second).
        # My previous code was `idx = index - 1`.
        # If user says "open video 2", index=2. idx = 1. LAST_SEARCH_RESULTS[1] is the SECOND video.
        # This logic IS correct for standard 1-based lists.
        # However, the user claims it opens the FIRST video.
        # This means `idx` became 0.
        # This implies `index` was passed as 1 when user said "second"? OR `index` passed as 2 but logic failed?
        # Or maybe the list order is confusing.
        # I will add logging/debugging output to the response string to be transparent.
        
        target_idx = index - 1
        
        if 0 <= target_idx < len(LAST_SEARCH_RESULTS):
            video = LAST_SEARCH_RESULTS[target_idx]
            url = video['link']
            webbrowser.open(url)
            return f"✅ Opening video #{index}: {video['title']} ({url})"
        else:
            return f"❌ Invalid index {index}. Please choose between 1 and {len(LAST_SEARCH_RESULTS)}."
    except Exception as e:
        return f"Error selecting video: {e}"

async def click_youtube_video(video_index: int = 2) -> str:
    """
    Clicks on a specific YouTube video from search results on screen (1st, 2nd, 3rd, etc.).
    Uses calibrated coordinates based on primary display resolution to prevent clicking blank areas.
    """
    try:
        import pyautogui
        sw, sh = pyautogui.size()
        # If we have cached search results, open the exact link directly for 100% precision
        global LAST_SEARCH_RESULTS
        if LAST_SEARCH_RESULTS and 0 <= (video_index - 1) < len(LAST_SEARCH_RESULTS):
            video = LAST_SEARCH_RESULTS[video_index - 1]
            webbrowser.open(video['link'])
            return f"✅ Opened video #{video_index} directly: '{video['title']}'"
            
        # Otherwise, calculate screen coordinates for YouTube search list
        base_y = int(sh * 0.30)
        gap = int(sh * 0.19)
        target_x = int(sw * 0.40)
        target_y = base_y + (video_index - 1) * gap
        
        if target_y > int(sh * 0.85):
            pyautogui.scroll(-500)
            time.sleep(0.5)
            target_y = int(sh * 0.50)
            
        pyautogui.moveTo(target_x, target_y, duration=0.3)
        pyautogui.click()
        return f"✅ Clicked video #{video_index} on screen at ({target_x}, {target_y})."
    except Exception as e:
        return f"❌ Error clicking video #{video_index}: {e}"


async def get_youtube_subscribers(channel_name: str = "Code x Play") -> str:
    api_key = os.getenv("YOUTUBE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key: return "No API Key"
    try:
        # Simplified search
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={api_key}"
        res = requests.get(url).json()
        cid = res["items"][0]["id"]["channelId"]
        stats_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={cid}&key={api_key}"
        stats = requests.get(stats_url).json()["items"][0]["statistics"]
        return f"Subscribers: {stats['subscriberCount']} | Views: {stats['viewCount']}"
    except Exception as e: return f"Error: {e}"

async def open_youtube_studio(action: str = "dashboard") -> str:
    webbrowser.open(f"https://studio.youtube.com/")
    return "Studio Opened"


async def generate_image(prompt: str, style: str = "photorealistic, cinematic, high detail, 4k", save_folder: str = "") -> str:
    """
    Generates a high-definition AI image for FREE using Pollinations AI Engine.
    No API keys needed, zero cost, unlimited generation.
    """
    import requests, os, time
    from pathlib import Path
    from urllib.parse import quote

    out_dir = Path(save_folder) if save_folder else (Path.home() / "Pictures" / "ULTRON_Images")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    clean_prompt = prompt.strip()
    full_prompt = f"{clean_prompt}, {style}" if style else clean_prompt
    encoded = quote(full_prompt)
    
    urls = [
        f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true",
        f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true&model=turbo",
        f"https://image.pollinations.ai/prompt/{encoded}?nologo=true"
    ]
    
    filename = f"ultron_{int(time.time())}.jpg"
    file_path = out_dir / filename
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=25)
            if resp.status_code == 200 and len(resp.content) > 1000:
                file_path.write_bytes(resp.content)
                try:
                    os.startfile(str(file_path))
                except Exception:
                    pass
                msg = f"🎨 Image generated successfully!\n📁 Saved to: {file_path}\n🌐 Prompt: {clean_prompt}"
                return msg
        except Exception:
            continue
            
    return "❌ Image generation service is currently busy. Please try again in a few seconds."

async def analyze_screen_content(prompt: str = "Describe everything you see on the screen.") -> str:
    """Takes a screenshot and analyzes screen content using Ultron Vision."""
    import pyautogui
    from pathlib import Path
    from aria_modules.vision_core import analyze_image_fast

    out_dir = Path.home() / "Documents" / "ULTRON_Data" / "Screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_path = out_dir / "screen_vision.png"
    
    try:
        shot = pyautogui.screenshot()
        shot.save(str(temp_path))
        res = analyze_image_fast(temp_path, prompt)
        return f"👁️ Screen Analysis:\n{res}"
    except Exception as e:
        return f"❌ Screen Analysis Error: {e}"

