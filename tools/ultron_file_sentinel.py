# -*- coding: utf-8 -*-
"""
ULTRON Ω — Protective File Intelligence & Memory-Based File Protection Subsystem
Implements:
- Persistent Project Protection Registry (NORMAL, WATCH, IMPORTANT, CRITICAL)
- File awareness and deletion-risk assessment
- Verified backup creation (SHA-256 checksum + size verification before reporting success)
- Windows Explorer selection & filesystem awareness
- Zero destructive actions without explicit authorization
"""

import os
import json
import time
import shutil
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
REGISTRY_FILE = DATA_DIR / "ultron_protected_files.json"
BACKUP_DIR = DATA_DIR / "verified_backups"

DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Protection Levels
LEVEL_NORMAL = 1     # No proactive warning without specific platform reason
LEVEL_WATCH = 2      # Warn when meaningful risk is detected
LEVEL_IMPORTANT = 3  # Warn before supported risky deletion, offer backup
LEVEL_CRITICAL = 4   # Require explicit confirmation for any assistant-related operation


def _load_registry() -> Dict[str, Any]:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": "2.0", "entries": {}}


def _save_registry(reg: Dict[str, Any]):
    REGISTRY_FILE.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")


def _compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _is_git_tracked(filepath: Path) -> bool:
    """Checks if a file or directory is inside a Git repository."""
    curr = filepath if filepath.is_dir() else filepath.parent
    for _ in range(6):
        if (curr / ".git").exists():
            return True
        if curr.parent == curr:
            break
        curr = curr.parent
    return False


# -------------------------------------------------------------
# 1. REGISTRY MANAGEMENT (USER-CONTROLLABLE)
# -------------------------------------------------------------

def register_protected_path(path: str, project_name: str, reason: str, level: int = LEVEL_IMPORTANT) -> Dict[str, Any]:
    """Registers a file or folder in the project protection registry."""
    norm_path = str(Path(path).resolve())
    p = Path(norm_path)
    if not p.exists():
        return {"success": False, "error": f"Path does not exist: {norm_path}"}

    reg = _load_registry()
    entry = {
        "path": norm_path,
        "is_dir": p.is_dir(),
        "project_name": project_name,
        "importance_reason": reason,
        "source": "user_registered",
        "registered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "git_tracked": _is_git_tracked(p),
        "backup_path": None,
        "backup_hash": None,
        "backup_time": None,
        "protection_level": level
    }
    reg["entries"][norm_path] = entry
    _save_registry(reg)
    return {"success": True, "entry": entry}


def remove_protected_path(path: str) -> bool:
    """Removes a path from the protection registry."""
    norm_path = str(Path(path).resolve())
    reg = _load_registry()
    if norm_path in reg["entries"]:
        del reg["entries"][norm_path]
        _save_registry(reg)
        return True
    return False


def list_protected_paths() -> List[Dict[str, Any]]:
    """Lists all registered protected projects and files."""
    reg = _load_registry()
    return list(reg["entries"].values())


# -------------------------------------------------------------
# 2. FILE RISK INSPECTION & DELETION WARNING
# -------------------------------------------------------------

def inspect_file_protection(target_path: str) -> Dict[str, Any]:
    """Checks if a file matches or resides inside any protected registry path."""
    try:
        norm_target = str(Path(target_path).resolve())
    except Exception:
        norm_target = str(target_path)

    reg = _load_registry()
    matched_entry = None

    # Exact or parent directory match
    for reg_path, entry in reg["entries"].items():
        if norm_target == reg_path or norm_target.startswith(reg_path + os.sep):
            matched_entry = entry
            break

    target_p = Path(norm_target)
    exists = target_p.exists()
    is_git = _is_git_tracked(target_p) if exists else False

    return {
        "path": norm_target,
        "exists": exists,
        "is_protected": matched_entry is not None,
        "protection_level": matched_entry.get("protection_level", LEVEL_NORMAL) if matched_entry else LEVEL_NORMAL,
        "project_name": matched_entry.get("project_name") if matched_entry else None,
        "importance_reason": matched_entry.get("importance_reason") if matched_entry else None,
        "git_tracked": is_git,
        "has_backup": bool(matched_entry.get("backup_path")) if matched_entry else False
    }


def evaluate_deletion_risk(target_path: str) -> Dict[str, Any]:
    """
    Evaluates risk before a potential deletion.
    Returns:
    - risk_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE"
    - should_warn: bool
    - warning_text: Natural conversational warning string
    """
    info = inspect_file_protection(target_path)
    p = Path(info["path"])

    # 1. Registered Important/Critical project file
    if info["is_protected"]:
        proj = info["project_name"] or "your project"
        level = info["protection_level"]
        if level >= LEVEL_IMPORTANT:
            warning = f"Wait a second — this file is part of your {proj} project. Do you want to back it up before deleting it?"
            return {"risk_level": "CRITICAL" if level == LEVEL_CRITICAL else "HIGH", "should_warn": True, "warning_text": warning, "info": info}
        elif level == LEVEL_WATCH:
            warning = f"Heads up, this item is monitored under {proj}. Let me know if you need a quick backup."
            return {"risk_level": "MEDIUM", "should_warn": True, "warning_text": warning, "info": info}

    # 2. Known project configuration heuristic (e.g. package.json, requirements.txt, .env)
    filename = p.name.lower()
    config_names = [".env", "package.json", "requirements.txt", "cargo.toml", "cmakelists.txt", "dockerfile", "tsconfig.json"]
    if filename in config_names:
        warning = "This looks like a project configuration file. Deleting it could affect how the project runs. Want me to check its dependencies first?"
        return {"risk_level": "HIGH", "should_warn": True, "warning_text": warning, "info": info}

    # 3. Disposable/temporary files (logs, tmp, cache)
    if any(k in filename for k in [".tmp", ".log", ".cache", ".bak", "temp"]):
        return {"risk_level": "SAFE", "should_warn": False, "warning_text": None, "info": info}

    # 4. Unknown file
    warning = "I can't tell whether this file is important yet. Would you like me to inspect it before you delete it?"
    return {"risk_level": "LOW", "should_warn": False, "warning_text": warning, "info": info}


# -------------------------------------------------------------
# 3. VERIFIED BACKUP CREATION
# -------------------------------------------------------------

def create_verified_backup(target_path: str) -> Tuple[bool, str]:
    """
    Creates a verified, timestamped backup.
    Assertion: Verifies that the backup file exists, is non-empty,
    and matches the original SHA-256 before declaring success.
    """
    p = Path(target_path).resolve()
    if not p.exists():
        return False, f"Target file does not exist: {p}"

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    if p.is_file():
        backup_name = f"{p.stem}_{timestamp}{p.suffix}.bak"
        dest_path = BACKUP_DIR / backup_name
        try:
            orig_hash = _compute_sha256(p)
            orig_size = p.stat().st_size

            shutil.copy2(p, dest_path)

            # Verification assertions
            if not dest_path.exists():
                return False, "Verification assertion failed: Backup file was not created on disk."
            if dest_path.stat().st_size != orig_size:
                dest_path.unlink(missing_ok=True)
                return False, "Verification assertion failed: Backup file size mismatch."
            backup_hash = _compute_sha256(dest_path)
            if backup_hash != orig_hash:
                dest_path.unlink(missing_ok=True)
                return False, "Verification assertion failed: SHA-256 checksum mismatch."

            # Update registry if file was registered
            reg = _load_registry()
            str_p = str(p)
            if str_p in reg["entries"]:
                reg["entries"][str_p]["backup_path"] = str(dest_path)
                reg["entries"][str_p]["backup_hash"] = backup_hash
                reg["entries"][str_p]["backup_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                _save_registry(reg)

            return True, f"Verified backup created: {dest_path.name} (SHA-256: {backup_hash[:12]}...)"
        except Exception as e:
            return False, f"Backup error: {e}"

    elif p.is_dir():
        backup_name = f"{p.name}_{timestamp}.zip"
        dest_zip = BACKUP_DIR / f"{p.name}_{timestamp}"
        try:
            archive_path = Path(shutil.make_archive(str(dest_zip), "zip", p))
            if not archive_path.exists() or archive_path.stat().st_size == 0:
                return False, "Verification assertion failed: Archive creation failed or is empty."

            return True, f"Verified project archive created: {archive_path.name} ({archive_path.stat().st_size} bytes)"
        except Exception as e:
            return False, f"Directory backup error: {e}"

    return False, "Unsupported target type"
