"""
ULTRON File Indexer & Smart Search Opener
Searches for and opens files with fuzzy matching, auto window focusing, and multi-drive indexing.
"""

import os
import sys
import asyncio
import logging
import subprocess
from typing import List, Dict, Any, Optional

try:
    from fuzzywuzzy import process
except ImportError:
    process = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

logger = logging.getLogger(__name__)


async def focus_window(title_keyword: str) -> bool:
    """
    Finds and focuses the window matching the title keyword.
    Restores if minimized and brings to the foreground.
    """
    if not gw:
        logger.warning("pygetwindow is not available.")
        return False

    await asyncio.sleep(1.5)
    clean_keyword = title_keyword.lower().strip()

    try:
        for window in gw.getAllWindows():
            if clean_keyword in window.title.lower():
                if window.isMinimized:
                    window.restore()
                window.activate()
                logger.info(f"Window focused: {window.title}")
                return True
    except Exception as e:
        logger.warning(f"Error focusing window: {e}")

    logger.warning("Window to focus not found.")
    return False


async def index_files(base_dirs: List[str]) -> List[Dict[str, str]]:
    """
    Recursively scans base directories and builds a file index.
    """
    file_index = []
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            continue
        try:
            for root, _, files in os.walk(base_dir):
                for f in files:
                    file_index.append({
                        "name": f,
                        "path": os.path.join(root, f),
                        "type": "file"
                    })
        except Exception as e:
            logger.warning(f"Error scanning directory {base_dir}: {e}")

    logger.info(f"Indexed {len(file_index)} files from {base_dirs}.")
    return file_index


async def search_file(query: str, index: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    Fuzzy matches query against indexed filenames.
    """
    choices = [item["name"] for item in index]
    if not choices:
        logger.warning("No files available in index.")
        return None

    if process:
        best_match, score = process.extractOne(query, choices)
        logger.info(f"Matched '{query}' to '{best_match}' (Score: {score})")
        if score > 60:
            for item in index:
                if item["name"] == best_match:
                    return item
    else:
        # Fallback substring / difflib
        import difflib
        matches = difflib.get_close_matches(query, choices, n=1, cutoff=0.5)
        if matches:
            for item in index:
                if item["name"] == matches[0]:
                    return item

    return None


async def open_file(item: Dict[str, str]) -> str:
    """
    Launches the file using default system viewer and focuses the window.
    """
    try:
        logger.info(f"Opening file: {item['path']}")
        if os.name == 'nt':
            os.startfile(item["path"])
        else:
            subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', item["path"]])

        await focus_window(item["name"])
        return f"File opened successfully: {item['name']}"
    except Exception as e:
        logger.error(f"Error opening file: {e}")
        return f"Failed to open file: {e}"


async def handle_command(command: str, index: List[Dict[str, str]]) -> str:
    """
    Searches for the requested file in the index and opens it.
    """
    item = await search_file(command, index)
    if item:
        return await open_file(item)
    else:
        logger.warning(f"File not found for query: '{command}'")
        return f"File '{command}' not found."


async def play_file(name: str) -> str:
    """
    Searches for and opens a file by name across drives (D:/, C:/Users/shiva/Downloads, Documents, Desktop).
    Useful for opening videos, PDFs, documents, audio, or images by name.
    """
    user_home = os.path.expanduser("~")
    folders_to_index = [
        "D:/",
        os.path.join(user_home, "Downloads"),
        os.path.join(user_home, "Documents"),
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Videos"),
        os.path.join(user_home, "Music")
    ]
    # Keep only folders that exist
    valid_folders = [f for f in folders_to_index if os.path.exists(f)]
    index = await index_files(valid_folders)
    command = name.strip()
    return await handle_command(command, index)


async def Play_file(name: str) -> str:
    """Alias for play_file."""
    return await play_file(name)
