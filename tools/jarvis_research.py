"""
ULTRON JARVIS Advanced Internet & Research Intelligence Suite
Multi-source search, technical documentation retrieval, GitHub intelligence, page distillation, and source synthesis.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import requests
except ImportError:
    requests = None


def _get_html(url: str, timeout: int = 10) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    if requests:
        res = requests.get(url, headers=headers, timeout=timeout)
        res.raise_for_status()
        return res.text
    else:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")


# ==========================================
# 1. CORE SEARCH & EXTRACTION
# ==========================================

async def web_search(query: str, max_results: int = 5) -> str:
    """
    Executes a live real-time web search and returns concise, verified information and URLs.
    """
    from friday_tools.core import search_web
    return await search_web(query, max_results=max_results)


async def open_webpage(url: str) -> str:
    """Opens a webpage in the default desktop browser or stealth web automation."""
    try:
        import webbrowser
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open(url)
        return f"[OK] Opened webpage in browser: {url}"
    except Exception as e:
        return f"[ERROR] Failed to open URL: {e}"


async def extract_webpage(url: str) -> str:
    """Extracts cleaned readable text content and removes ads/scripts from a webpage URL."""
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        html = _get_html(url)
        
        if BeautifulSoup:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.extract()
            text = soup.get_text(separator="\n", strip=True)
            # Remove excessive blank lines
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            cleaned = "\n".join(lines[:120]) # Limit to top relevant chunks
            return f"📄 [Page Content Extracted from {url}]:\n\n{cleaned[:4000]}"
        return f"[Extracted raw text from {url}]:\n{html[:2000]}"
    except Exception as e:
        return f"[ERROR] Extraction failed for {url}: {e}"


async def summarize_page(url: str) -> str:
    """Fetches a webpage and generates an executive technical summary using AI."""
    try:
        content = await extract_webpage(url)
        if "[ERROR]" in content:
            return content
        
        import friday_tools.ai_client as ai
        prompt = f"Summarize the key takeaways, architecture, specifications, or conclusions from this extracted web text:\n\n{content[:4000]}"
        summary = ai.generate_ai_response(prompt=prompt, system_instruction="You are ULTRON Research Intelligence. Provide clear, structured, bulleted summaries.")
        return f"📑 [Executive Summary for {url}]:\n\n{summary}"
    except Exception as e:
        return f"[ERROR] Summary failed: {e}"


# ==========================================
# 2. SPECIALIZED TECHNICAL RESEARCH
# ==========================================

async def search_news(query: str) -> str:
    """Searches recent breaking news and technical announcements."""
    return await web_search(f"{query} news breaking", max_results=5)


async def search_github(query: str) -> str:
    """Searches GitHub repositories, code libraries, and open-source tools."""
    try:
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=5"
        headers = {"User-Agent": "ULTRON-JARVIS-AI"}
        if requests:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                items = data.get("items", [])
                out = [f"🐙 [GitHub Open Source Repositories for '{query}']:\n"]
                for it in items:
                    stars = it.get("stargazers_count", 0)
                    desc = it.get("description", "No description provided.")
                    repo_url = it.get("html_url", "")
                    name = it.get("full_name", "")
                    out.append(f"• **{name}** (⭐ {stars})\n  URL: {repo_url}\n  Description: {desc}")
                return "\n\n".join(out)
        return await web_search(f"site:github.com {query}", max_results=5)
    except Exception as e:
        return f"[ERROR] GitHub search error: {e}"


async def search_documentation(technology: str, query: str) -> str:
    """
    Searches official technical documentation for APIs, microcontrollers (ESP32, Arduino, Raspberry Pi, Python, PyQt5, C++).
    """
    search_phrase = f"{technology} official documentation {query}"
    return await web_search(search_phrase, max_results=5)


async def download_file(url: str, save_path: str = "") -> str:
    """Downloads a file or dataset from the internet to local storage."""
    try:
        downloads_dir = Path.home() / "Downloads"
        filename = url.split("/")[-1].split("?")[0] or f"download_{int(time.time())}.dat"
        dest = Path(save_path) if save_path else (downloads_dir / filename)
        
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response, open(dest, 'wb') as out_file:
            out_file.write(response.read())
        return f"[OK] File successfully downloaded to: {dest}"
    except Exception as e:
        return f"[ERROR] File download failed: {e}"


async def compare_sources(query: str, urls: list) -> str:
    """Synthesizes and compares information across multiple online sources."""
    try:
        snippets = []
        for u in urls[:3]:
            txt = await extract_webpage(u)
            snippets.append(f"--- SOURCE: {u} ---\n{txt[:1500]}")
            
        import friday_tools.ai_client as ai
        prompt = f"Compare the perspectives, data points, and technical differences between these sources regarding '{query}':\n\n" + "\n\n".join(snippets)
        return ai.generate_ai_response(prompt=prompt, system_instruction="You are ULTRON Multi-Source Synthesis Engine.")
    except Exception as e:
        return f"[ERROR] Comparison error: {e}"
