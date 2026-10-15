"""
ULTRON Workspace Lens & File Intelligence Engine
Scans repositories, identifies duplicate files via SHA256 checksums, executes regex batch renames, and indexes document text.
"""

import os
import re
import sys
import time
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Set


def _sha256_file(filepath: Path, chunk_size: int = 65536) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


async def workspace_find_duplicate_files(directory: str = "~/Downloads", min_size_kb: int = 100) -> str:
    """
    Scans a folder recursively and identifies exact byte-for-byte duplicate files using SHA256 hashing.
    
    Args:
        directory: Path to scan (e.g. '~/Downloads', 'C:/Projects').
        min_size_kb: Minimum file size in KB to consider.
    """
    def _scan():
        target_dir = Path(directory).expanduser().resolve()
        if not target_dir.exists():
            return f"Directory `{target_dir}` does not exist."

        size_map: Dict[int, List[Path]] = {}
        for root, _, files in os.walk(target_dir):
            for f in files:
                p = Path(root) / f
                try:
                    if p.is_file():
                        sz = p.stat().st_size
                        if sz >= min_size_kb * 1024:
                            size_map.setdefault(sz, []).append(p)
                except Exception:
                    continue

        # For files with identical size, compute hash
        hash_map: Dict[str, List[Path]] = {}
        for sz, path_list in size_map.items():
            if len(path_list) > 1:
                for p in path_list:
                    try:
                        h = _sha256_file(p)
                        hash_map.setdefault(h, []).append(p)
                    except Exception:
                        continue

        duplicates = {k: v for k, v in hash_map.items() if len(v) > 1}

        if not duplicates:
            return f"✅ [NO DUPLICATES] No duplicate files (>{min_size_kb}KB) found in `{target_dir}`."

        total_wasted_bytes = 0
        lines = [f"📂 **DUPLICATE FILE AUDIT FOR `{target_dir}` ({len(duplicates)} Duplicate Clusters):**"]
        for idx, (h, file_list) in enumerate(duplicates.items(), 1):
            file_sz = file_list[0].stat().st_size
            wasted = file_sz * (len(file_list) - 1)
            total_wasted_bytes += wasted
            lines.append(f"\n  **Group {idx}** (Hash: `{h[:12]}...` | Size: {file_sz / (1024*1024):.2f} MB):")
            for fp in file_list:
                lines.append(f"    • `{fp.resolve()}`")

        lines.append(f"\n💾 **Total Recoverable Storage:** **{total_wasted_bytes / (1024*1024):.2f} MB**")
        return "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scan)


async def workspace_bulk_rename(directory: str, pattern: str, replacement: str, dry_run: bool = True) -> str:
    r"""
    Performs regex batch renaming on files with a safe dry-run preview before executing.
    
    Args:
        directory: Target folder path.
        pattern: Regex pattern to match in filenames (e.g. r'IMG_(\d+)', r'\s+').
        replacement: String or regex replacement (e.g. r'Photo_\1', r'_').
        dry_run: If True, only previews changes without modifying files. Set False to apply.
    """
    def _rename():
        target_dir = Path(directory).expanduser().resolve()
        if not target_dir.exists():
            return f"Directory `{target_dir}` not found."

        changes = []
        for item in target_dir.iterdir():
            if item.is_file():
                old_name = item.name
                new_name = re.sub(pattern, replacement, old_name)
                if new_name != old_name:
                    new_path = item.parent / new_name
                    changes.append((item, new_path, old_name, new_name))

        if not changes:
            return f"No files in `{target_dir}` matched the regex pattern `'{pattern}'`."

        if dry_run:
            lines = [f"🔍 **BULK RENAME PREVIEW (Dry-Run: {len(changes)} Files Matched):**"]
            for _, _, old_n, new_n in changes[:15]:
                lines.append(f"  • `{old_n}` ➔ `{new_n}`")
            if len(changes) > 15:
                lines.append(f"  ... and {len(changes) - 15} more files.")
            lines.append(f"\n💡 *To apply these renames, set `dry_run=False`.*")
            return "\n".join(lines)

        applied = 0
        errors = []
        for old_p, new_p, old_n, new_n in changes:
            try:
                old_p.rename(new_p)
                applied += 1
            except Exception as e:
                errors.append(f"Failed `{old_n}`: {e}")

        res = f"✅ [BULK RENAME EXECUTED] Successfully renamed **{applied}/{len(changes)}** files in `{target_dir}`."
        if errors:
            res += "\n⚠️ Errors encountered:\n  • " + "\n  • ".join(errors)
        return res

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _rename)


async def workspace_summarize_project_repo(repo_path: str) -> str:
    """
    Analyzes a software repository and provides an instant architecture summary, file breakdown, and Git health report.
    
    Args:
        repo_path: Root folder of the project/codebase.
    """
    def _summarize():
        p = Path(repo_path).expanduser().resolve()
        if not p.exists():
            return f"Project path `{p}` does not exist."

        # File extensions tally
        ext_count: Dict[str, int] = {}
        total_files = 0
        total_lines = 0

        ignore_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".idea", ".vscode"}

        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in files:
                ext = Path(f).suffix.lower() or "no_ext"
                ext_count[ext] = ext_count.get(ext, 0) + 1
                total_files += 1

                # Count lines for code files
                if ext in (".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".cpp", ".c", ".h", ".rs", ".go", ".java"):
                    try:
                        fp = Path(root) / f
                        with open(fp, "r", encoding="utf-8", errors="ignore") as code_f:
                            total_lines += sum(1 for _ in code_f)
                    except Exception:
                        pass

        # Git Status
        git_branch = "N/A"
        git_commits = "N/A"
        if (p / ".git").exists():
            try:
                import subprocess
                b_res = subprocess.run(["git", "branch", "--show-current"], cwd=p, capture_output=True, text=True, timeout=2)
                git_branch = b_res.stdout.strip() or "main"
                c_res = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=p, capture_output=True, text=True, timeout=2)
                git_commits = c_res.stdout.strip()
            except Exception:
                pass

        sorted_exts = sorted(ext_count.items(), key=lambda x: x[1], reverse=True)[:6]

        lines = [
            f"🏗️ **PROJECT CODEBASE RECON: `{p.name}`**",
            f"• **Root Path:** `{p}`",
            f"• **Active Git Branch:** `{git_branch}` ({git_commits} total commits)",
            f"• **Total Tracked Files:** {total_files:,}",
            f"• **Total Lines of Source Code:** ~{total_lines:,} lines",
            f"\n📊 **Primary File Types:**"
        ]
        for ext, cnt in sorted_exts:
            lines.append(f"  • `{ext}`: {cnt:,} files")

        return "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _summarize)


async def workspace_tree_structure(directory: str, max_depth: int = 2) -> str:
    """
    Renders an ASCII directory tree hierarchy for any workspace or folder.
    
    Args:
        directory: Directory to visualize.
        max_depth: Maximum folder nesting depth (default: 2).
    """
    def _tree():
        target = Path(directory).expanduser().resolve()
        if not target.exists():
            return f"Path `{target}` does not exist."

        ignore = {".git", "node_modules", ".venv", "__pycache__"}
        lines = [f"📁 {target.name}/"]

        def _walk(curr: Path, prefix: str, depth: int):
            if depth > max_depth:
                return
            try:
                items = sorted(list(curr.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
            except Exception:
                return

            items = [i for i in items if i.name not in ignore]
            for idx, item in enumerate(items):
                is_last = (idx == len(items) - 1)
                connector = "└── " if is_last else "├── "
                sub_prefix = "    " if is_last else "│   "
                if item.is_dir():
                    lines.append(f"{prefix}{connector}📁 {item.name}/")
                    _walk(item, prefix + sub_prefix, depth + 1)
                else:
                    lines.append(f"{prefix}{connector}📄 {item.name}")

        _walk(target, "", 1)
        return "```\n" + "\n".join(lines[:120]) + "\n```"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _tree)
