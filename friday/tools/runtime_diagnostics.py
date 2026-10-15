"""
Runtime Diagnostics & Telemetry for JARVIS / ULTRON Neural OS
Logs executable path, PID, loaded package paths, git commit, and active configurations.
Prevents ghost processes and environment desync.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path

DIAGNOSTICS_DIR = Path.home() / "Documents" / "ULTRON_Data"
DIAGNOSTICS_FILE = DIAGNOSTICS_DIR / "runtime_diagnostics.log"

logger = logging.getLogger("JARVIS.Diagnostics")


def log_runtime_identity(component_name: str = "Assistant"):
    """Logs the exact process, python executable, environment, and file sources."""
    try:
        DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
        
        info = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "component": component_name,
            "pid": os.getpid(),
            "executable": sys.executable,
            "cwd": os.getcwd(),
            "python_version": sys.version.split()[0],
            "module_file": __file__,
            "sys_path_head": sys.path[:4],
        }

        # Check git commit if available
        try:
            repo_dir = Path(__file__).resolve().parent.parent
            head_file = repo_dir / ".git" / "HEAD"
            if head_file.exists():
                head_ref = head_file.read_text().strip()
                if head_ref.startswith("ref:"):
                    ref_path = repo_dir / ".git" / head_ref.split()[1]
                    if ref_path.exists():
                        info["git_commit"] = ref_path.read_text().strip()[:8]
                else:
                    info["git_commit"] = head_ref[:8]
        except Exception:
            pass

        log_line = json.dumps(info)
        with open(DIAGNOSTICS_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        print(f"🔍 [Runtime Identity] PID {info['pid']} | {info['executable']} | Root: {Path(__file__).parent.parent}")
        return info
    except Exception as e:
        print(f"⚠️ Diagnostics logging note: {e}")
        return {}


class StageLogger:
    """Structured, observable latency and stage tracker for requests."""

    def __init__(self, request_id: str, prompt: str):
        self.request_id = request_id
        self.prompt_preview = prompt[:40].replace("\n", " ")
        self.start_time = time.time()
        self.stages = []

    def log_stage(self, stage: str, status: str = "OK", detail: str = ""):
        elapsed = round(time.time() - self.start_time, 3)
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "req_id": self.request_id,
            "stage": stage,
            "elapsed_sec": elapsed,
            "status": status,
            "detail": detail
        }
        self.stages.append(entry)
        
        # Append to telemetry log
        try:
            with open(DIAGNOSTICS_DIR / "request_stages.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
        
        if status != "OK":
            print(f"⏱️ [{self.request_id}] {stage} -> {status} ({elapsed}s): {detail}")
