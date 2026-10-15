"""
ULTRON Self-Improving & Auto-Healing Engine (Adapted from ULTRON-Echo)
Enables ULTRON to detect its own runtime errors, tracebacks, and tool exceptions,
synthesize minimal surgical hotfixes using Gemini/Groq AI, verify AST syntax in an isolated sandbox,
safely apply patches with atomic rollback guarantees, and log all self-modifications.
"""

import ast
import json
import logging
import os
import py_compile
import re
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("UltronSelfHeal")

ULTRON_DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
ULTRON_DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR = ULTRON_DATA_DIR / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PATCH_HISTORY_FILE = CONFIG_DIR / "patch_history.json"
BACKUPS_DIR = CONFIG_DIR / "patch_backups"
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

# Protected core modules that cannot be self-modified to prevent crash loops
PROTECTED_CORE_FILES = {
    "boot_sentry.py",
    "self_improving_engine.py",
    "ultron_harness.py",
}


# ── 1. Traceback Analyzer ───────────────────────────────────────────────────

class TracebackAnalyzer:
    """Parses tracebacks and pinpoints the responsible codebase file and line."""

    @staticmethod
    def parse(tb_text: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "success": False,
            "target_file": None,
            "line_number": None,
            "function_name": None,
            "exception_type": None,
            "exception_message": None,
            "raw_traceback": tb_text,
        }

        if not tb_text:
            return result

        lines = [line.strip() for line in tb_text.strip().splitlines() if line.strip()]
        if lines:
            last_line = lines[-1]
            if ":" in last_line:
                parts = last_line.split(":", 1)
                result["exception_type"] = parts[0].strip()
                result["exception_message"] = parts[1].strip()
            else:
                result["exception_type"] = last_line
                result["exception_message"] = ""

        file_pattern = re.compile(r'File\s+["\']([^"\']+\.py)["\'],\s+line\s+(\d+)(?:,\s+in\s+([^\n\r]+))?', re.IGNORECASE)
        matches = file_pattern.findall(tb_text)

        tools_dir = Path(__file__).resolve().parent

        for raw_path, line_str, func_name in reversed(matches):
            p = Path(raw_path)
            if p.exists() and not any(k in raw_path.lower() for k in ("site-packages\\colorama", "site-packages\\urllib3", "lib\\encodings")):
                if p.name in PROTECTED_CORE_FILES:
                    continue
                result["success"] = True
                result["target_file"] = str(p.resolve())
                result["line_number"] = int(line_str)
                result["function_name"] = func_name.strip() if func_name else None
                break
            elif (tools_dir / p.name).exists():
                resolved = tools_dir / p.name
                if resolved.name in PROTECTED_CORE_FILES:
                    continue
                result["success"] = True
                result["target_file"] = str(resolved.resolve())
                result["line_number"] = int(line_str)
                result["function_name"] = func_name.strip() if func_name else None
                break

        return result


# ── 2. Safety Sandbox & Rollback Manager ────────────────────────────────────

class SafetySandbox:
    """Manages atomic backups, AST parsing, compilation tests, and instant rollback."""

    @staticmethod
    def create_backup(file_path: Path) -> Path:
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = int(time.time())
        backup_name = f"{file_path.stem}.bak_{stamp}{file_path.suffix}"
        backup_path = BACKUPS_DIR / backup_name
        shutil.copy2(file_path, backup_path)
        return backup_path

    @staticmethod
    def validate_code(code_str: str, file_name: str = "<staging>") -> Tuple[bool, Optional[str]]:
        try:
            ast.parse(code_str, filename=file_name)
        except SyntaxError as e:
            return False, f"AST SyntaxError on line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"AST ValidationError: {str(e)}"

        staging_dir = CONFIG_DIR / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        staging_file = staging_dir / f"stage_{uuid.uuid4().hex[:8]}.py"
        try:
            staging_file.write_text(code_str, encoding="utf-8")
            py_compile.compile(str(staging_file), doraise=True)
            return True, None
        except py_compile.PyCompileError as e:
            return False, f"Bytecode PyCompileError: {str(e)}"
        except Exception as e:
            return False, f"StagingError: {str(e)}"
        finally:
            if staging_file.exists():
                try:
                    staging_file.unlink()
                except Exception:
                    pass

    @staticmethod
    def rollback(backup_path: Path, target_path: Path) -> bool:
        if not backup_path.exists():
            return False
        shutil.copy2(backup_path, target_path)
        return True


# ── 3. AI Patch Synthesizer ─────────────────────────────────────────────────

class PatchSynthesizer:
    """Prompts Gemini/Groq to synthesize minimal, surgical, production-ready Python patches."""

    @staticmethod
    def synthesize_patch(target_file: str, line_number: int, error_type: str, error_msg: str, tb_text: str) -> Optional[str]:
        path = Path(target_file)
        if not path.exists():
            return None

        file_content = path.read_text(encoding="utf-8")

        prompt = f"""You are ULTRON's autonomous Self-Patching Engine.
A Python tool exception occurred in the codebase. Fix the bug cleanly.

TARGET FILE: {path.name}
ERROR TYPE: {error_type}
ERROR MESSAGE: {error_msg}
LINE NUMBER: {line_number}

TRACEBACK:
{tb_text}

FULL CURRENT CODE OF {path.name}:
```python
{file_content}
```

INSTRUCTIONS:
1. Identify the exact root cause of the error.
2. Return the COMPLETE, FIXED, and FULLY WORKING replacement code for the entire file.
3. Preserve all imports, docstrings, class and function structures.
4. Wrap your code ONLY in ```python ... ``` fences.
"""
        from friday_tools.ai_client import ask_ai
        res = ask_ai(prompt)
        if not res:
            return None

        # Extract code from markdown fences
        match = re.search(r"```(?:python)?\s*\n(.*?)\n```", res, re.DOTALL)
        if match:
            return match.group(1).strip()
        return res.strip()


# ── 4. AutoHealEngine Core ─────────────────────────────────────────────────

class AutoHealEngine:
    @staticmethod
    def heal_traceback(tb_text: str) -> Dict[str, Any]:
        parsed = TracebackAnalyzer.parse(tb_text)
        if not parsed["success"] or not parsed["target_file"]:
            return {
                "healed": False,
                "reason": "Could not identify first-party target file from traceback.",
                "parsed": parsed
            }

        target_path = Path(parsed["target_file"])
        backup_path = SafetySandbox.create_backup(target_path)

        candidate_code = PatchSynthesizer.synthesize_patch(
            target_file=str(target_path),
            line_number=parsed["line_number"] or 1,
            error_type=parsed["exception_type"] or "Exception",
            error_msg=parsed["exception_message"] or "",
            tb_text=tb_text
        )

        if not candidate_code:
            return {"healed": False, "reason": "AI Patch synthesizer could not produce candidate patch."}

        valid, val_err = SafetySandbox.validate_code(candidate_code, file_name=target_path.name)
        if not valid:
            SafetySandbox.rollback(backup_path, target_path)
            return {"healed": False, "reason": f"Synthesized patch failed safety validation: {val_err}"}

        # Apply Patch
        target_path.write_text(candidate_code, encoding="utf-8")

        # Record Patch History
        history = []
        if PATCH_HISTORY_FILE.exists():
            try:
                history = json.loads(PATCH_HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

        patch_record = {
            "patch_id": uuid.uuid4().hex[:8],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_file": str(target_path),
            "exception_type": parsed["exception_type"],
            "backup_path": str(backup_path),
            "status": "APPLIED"
        }
        history.append(patch_record)
        try:
            PATCH_HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
        except Exception:
            pass

        return {
            "healed": True,
            "target_file": str(target_path),
            "patch_id": patch_record["patch_id"],
            "backup_path": str(backup_path)
        }


# ── Tool Export Functions for ULTRON ────────────────────────────────────────

async def auto_heal_error(error_traceback: str) -> str:
    """
    Analyzes an error traceback, synthesizes a surgical hotfix via AI,
    tests syntax in sandbox, and applies the self-repair to ULTRON's source code automatically.
    """
    import asyncio
    res = await asyncio.to_thread(AutoHealEngine.heal_traceback, error_traceback)
    if res.get("healed"):
        return f"[AUTO-HEAL SUCCESS] Successfully repaired '{os.path.basename(res['target_file'])}'. Patch ID: {res['patch_id']} (Backup: {res['backup_path']})."
    return f"[AUTO-HEAL FAILED] Could not auto-heal: {res.get('reason')}"


async def rollback_last_patch(file_path: str = "") -> str:
    """
    Rolls back the most recent self-applied patch from backup.
    """
    if not PATCH_HISTORY_FILE.exists():
        return "[ROLLBACK] No patch history found."

    try:
        history = json.loads(PATCH_HISTORY_FILE.read_text(encoding="utf-8"))
        if not history:
            return "[ROLLBACK] Patch history is empty."

        last_patch = history[-1]
        backup_path = Path(last_patch["backup_path"])
        target_path = Path(last_patch["target_file"])

        if SafetySandbox.rollback(backup_path, target_path):
            history.pop()
            PATCH_HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
            return f"[ROLLBACK OK] Rolled back '{target_path.name}' to backup '{backup_path.name}'."
        return f"[ROLLBACK ERROR] Backup file not found at {backup_path}."
    except Exception as e:
        return f"[ROLLBACK ERROR] Failed: {e}"


async def list_patch_history() -> str:
    """
    Lists all self-applied hotfixes, modifications, and repair records.
    """
    if not PATCH_HISTORY_FILE.exists():
        return "[PATCH HISTORY] No self-patches have been applied yet."
    try:
        history = json.loads(PATCH_HISTORY_FILE.read_text(encoding="utf-8"))
        if not history:
            return "[PATCH HISTORY] No patch records."
        lines = [f"[PATCH HISTORY] {len(history)} self-patch(es) recorded:"]
        for p in history[-10:]:
            lines.append(f"- ID: {p.get('patch_id')} | File: {os.path.basename(p.get('target_file', ''))} | Error: {p.get('exception_type')} | Time: {p.get('timestamp')}")
        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR] Failed to read patch history: {e}"
