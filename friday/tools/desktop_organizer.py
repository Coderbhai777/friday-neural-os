"""
ULTRON Smart Desktop & Folder Organizer (Adapted from ULTRON-Echo)
Categorizes and organizes cluttered folders (Desktop, Downloads, Documents) into clean semantic directories.
"""

import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List

CATEGORIES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".pptx", ".ppt", ".xlsx", ".xls", ".csv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"],
    "Audio_Music": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
    "Archives_Zips": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code_Scripts": [".py", ".js", ".ts", ".html", ".css", ".json", ".cpp", ".java", ".sql", ".sh", ".bat", ".ps1"],
    "Executables_Installers": [".exe", ".msi", ".iso"]
}

def _organize_folder(folder_path: str) -> str:
    target_dir = Path(folder_path).expanduser().resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        return f"[ERROR] Directory does not exist: {folder_path}"

    moved_counts: Dict[str, int] = {}
    total_moved = 0

    for item in target_dir.iterdir():
        if item.is_dir() or item.name.startswith("."):
            continue

        ext = item.suffix.lower()
        destination_cat = "Miscellaneous"
        for cat, ext_list in CATEGORIES.items():
            if ext in ext_list:
                destination_cat = cat
                break

        cat_dir = target_dir / destination_cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        dest_file = cat_dir / item.name
        # Avoid overwrite
        if dest_file.exists():
            stem = item.stem
            dest_file = cat_dir / f"{stem}_{int(os.path.getmtime(item))}{ext}"

        try:
            shutil.move(str(item), str(dest_file))
            moved_counts[destination_cat] = moved_counts.get(destination_cat, 0) + 1
            total_moved += 1
        except Exception:
            pass

    if total_moved == 0:
        return f"[ORGANIZER] No loose files found to organize in '{target_dir.name}'."

    summary = [f"[ORGANIZED {total_moved} FILES in {target_dir.name}]:"]
    for cat, count in moved_counts.items():
        summary.append(f" - {cat}: {count} file(s)")
    return "\n".join(summary)


async def organize_folder_files(folder_name: str = "Desktop") -> str:
    """
    Cleans up and sorts loose files in 'Desktop' or 'Downloads' into structured category folders.
    """
    folder = folder_name.lower().strip()
    if folder in ("desktop", "desk"):
        path = str(Path.home() / "Desktop")
    elif folder in ("downloads", "download"):
        path = str(Path.home() / "Downloads")
    elif folder in ("documents", "docs"):
        path = str(Path.home() / "Documents")
    else:
        path = folder_name

    return await asyncio.to_thread(_organize_folder, path)
