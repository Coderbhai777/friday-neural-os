# -*- coding: utf-8 -*-
"""
ULTRON Ω — Central Companion Orchestration Bridge
Unifies:
1. Continuous Screen Vision & Perceptual Change Detection
2. Proactive Companion Decision Engine (15s silence policy, adaptive cooldowns)
3. Protective File Sentinel (verified backups & deletion warnings)
4. Epistemic Memory & Screen-to-Memory Fallback
5. Real-Time Conversational Voice & Barge-In Interruption
"""

import os
import time
import threading
from typing import Dict, Any, Optional

try:
    from tools.ultron_vision_pipeline import (
        capture_screen_direct,
        get_active_window_info,
        compute_perceptual_hash,
        hamming_distance,
        analyze_screen_with_ai
    )
    from tools.ultron_proactive_engine import (
        ProactiveCompanionEngine,
        DECISION_SPEAK_NOW,
        DECISION_WAIT,
        DECISION_DO_NOT_DISTURB,
        DECISION_SILENTLY_OBSERVE
    )
    from tools.ultron_file_sentinel import (
        register_protected_path,
        list_protected_paths,
        evaluate_deletion_risk,
        create_verified_backup
    )
    from tools.ultron_memory_engine import (
        generate_memory_fallback_prompt,
        record_task_activity,
        handle_conversational_context
    )
except ImportError:
    from friday_tools.ultron_vision_pipeline import (
        capture_screen_direct,
        get_active_window_info,
        compute_perceptual_hash,
        hamming_distance,
        analyze_screen_with_ai
    )
    from friday_tools.ultron_proactive_engine import (
        ProactiveCompanionEngine,
        DECISION_SPEAK_NOW,
        DECISION_WAIT,
        DECISION_DO_NOT_DISTURB,
        DECISION_SILENTLY_OBSERVE
    )
    from friday_tools.ultron_file_sentinel import (
        register_protected_path,
        list_protected_paths,
        evaluate_deletion_risk,
        create_verified_backup
    )
    from friday_tools.ultron_memory_engine import (
        generate_memory_fallback_prompt,
        record_task_activity,
        handle_conversational_context
    )


def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        try:
            clean_args = [str(a).encode("ascii", errors="replace").decode("ascii") for a in args]
            print(*clean_args, **kwargs)
        except Exception:
            pass


class UltronOmegaCompanion:
    def __init__(self):
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.proactive_engine = ProactiveCompanionEngine()

        # Telemetry & Perceptual Cache
        self.last_window_info: Dict[str, Any] = {}
        self.last_screen_hash = ""
        self.last_screen_analysis: Dict[str, Any] = {}
        self.last_capture_time = 0.0

        # Lock
        self.lock = threading.Lock()

    def start(self):
        """Starts the autonomous companion background loop."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        safe_print("[ULTRON OMEGA Companion] Proactive Presence & Continuous Vision Active.")

    def stop(self):
        """Stops the autonomous companion background loop."""
        self.running = False

    def notify_user_spoke(self):
        """Hook to notify companion when user speaks (resets cooldown & cancels pending speech)."""
        self.proactive_engine.notify_user_speech()
        try:
            from tools.tts_engine import stop_speech
            stop_speech()
        except Exception:
            pass

    def _speak_aloud(self, text: str):
        """Speaks text aloud using neural TTS with instant barge-in support."""
        if not text:
            return
        safe_print(f"\n[ULTRON OMEGA]: {text}")
        try:
            from tools.tts_engine import speak_text_sync
            threading.Thread(target=speak_text_sync, args=(text,), daemon=True).start()
        except Exception as e:
            safe_print(f"Speech output note: {e}")

    def inspect_screen_now(self) -> Dict[str, Any]:
        """Performs an immediate live desktop screen capture and visual analysis."""
        win_info = get_active_window_info()
        img = capture_screen_direct(max_dim=768)
        if not img:
            # Fallback to memory hypothesis if screen unavailable
            return generate_memory_fallback_prompt()

        idle_sec = 0.0
        try:
            from tools.proactive_screen_vision import get_system_idle_seconds
            idle_sec = get_system_idle_seconds()
        except Exception:
            pass

        analysis = analyze_screen_with_ai(img, win_info, idle_sec)
        with self.lock:
            self.last_screen_analysis = analysis
            self.last_window_info = win_info
        return analysis

    def _run_loop(self):
        """Adaptive sampling monitoring loop (8GB RAM optimized)."""
        while self.running:
            time.sleep(2.0) # Lightweight 2s metadata interval
            try:
                now = time.time()
                win_info = get_active_window_info()

                # Check if window or app changed
                win_changed = (
                    win_info.get("hwnd") != self.last_window_info.get("hwnd") or
                    win_info.get("title") != self.last_window_info.get("title")
                )

                time_since_capture = now - self.last_capture_time

                # Adaptive capture gate: every 6s or immediately on window switch
                if win_changed or time_since_capture >= 6.0:
                    self.last_window_info = win_info
                    self.last_capture_time = now

                    # 1. Direct screen capture
                    img = capture_screen_direct(max_dim=640)
                    if not img:
                        continue

                    # 2. Perceptual Hash comparison (dHash)
                    curr_hash = compute_perceptual_hash(img)
                    h_dist = hamming_distance(curr_hash, self.last_screen_hash)

                    # Only run visual inference if screen meaningfully changed or window changed
                    if win_changed or h_dist >= 8:
                        self.last_screen_hash = curr_hash

                        idle_sec = 0.0
                        try:
                            from tools.proactive_screen_vision import get_system_idle_seconds
                            idle_sec = get_system_idle_seconds()
                        except Exception:
                            pass

                        # 3. Vision analysis
                        analysis = analyze_screen_with_ai(img, win_info, idle_sec)
                        self.last_screen_analysis = analysis

                        # 4. Proactive Companion Decision
                        decision, spoken_text, reason = self.proactive_engine.evaluate_initiative(
                            screen_analysis=analysis,
                            is_user_speaking=False,
                            is_tts_speaking=False,
                            system_idle_sec=idle_sec
                        )

                        if decision == DECISION_SPEAK_NOW and spoken_text:
                            self._speak_aloud(spoken_text)

            except Exception as e:
                time.sleep(3.0)


# Global singleton instance
_COMPANION = UltronOmegaCompanion()


# =============================================================
# EXPOSED FRIDAY / ULTRON TOOL INTERFACES
# =============================================================

async def start_ultron_companion() -> str:
    """Starts the ULTRON Ω proactive companion with continuous vision and 15s silence policy."""
    _COMPANION.start()
    return "Sir, ULTRON Ω Proactive Presence and Continuous Screen Vision are now ONLINE. I am monitoring your workspace and will contribute tactical insights naturally when relevant."


async def stop_ultron_companion() -> str:
    """Pauses the ULTRON Ω proactive companion background monitor."""
    _COMPANION.stop()
    return "ULTRON Ω Proactive Companion has been paused, Sir."


async def force_screen_perception() -> str:
    """Directly inspects your desktop screen right now and returns ULTRON's observation."""
    analysis = _COMPANION.inspect_screen_now()
    if analysis.get("status") == "MEMORY_FALLBACK":
        text = analysis.get("spoken_text")
        _COMPANION._speak_aloud(text)
        return f"[MEMORY FALLBACK] {text}"

    details = analysis.get("details", "Workspace active")
    obs = analysis.get("suggested_observation")
    if obs:
        _COMPANION._speak_aloud(obs)
        return f"[OBSERVATION]: {obs} (Activity: {analysis.get('activity')}, Confidence: {analysis.get('confidence')})"
    return f"Desktop inspected: {details} (Activity: {analysis.get('activity')})"


async def protect_project(path: str, project_name: str, reason: str = "Critical source files") -> str:
    """Registers a project path in the persistent file protection registry."""
    res = register_protected_path(path, project_name, reason)
    if res.get("success"):
        return f"Sir, I have registered '{project_name}' at '{path}' into the Protection Registry. Any risky operations will be intercepted."
    return f"Could not protect path: {res.get('error')}"


async def list_protected_files() -> str:
    """Lists all files and projects currently under ULTRON active protection."""
    entries = list_protected_paths()
    if not entries:
        return "No projects or files are currently registered in the Protection Registry, Sir."
    lines = ["🛡️ [ULTRON PROJECT PROTECTION REGISTRY]:"]
    for e in entries:
        b = "✅ Backed Up" if e.get("backup_path") else "⚠️ No Backup"
        g = "🌿 Git Tracked" if e.get("git_tracked") else "❌ Untracked"
        lines.append(f"• [{e['project_name']}] {e['path']} (Level {e['protection_level']} | {g} | {b})")
    return "\n".join(lines)


async def backup_project(path: str) -> str:
    """Creates a verified, SHA-256 validated backup of a project or file."""
    ok, msg = create_verified_backup(path)
    if ok:
        return f"Sir, {msg}"
    return f"Sir, backup operation failed: {msg}"


async def set_companion_mode(mode: str) -> str:
    """Sets companion mode: 'conversational', 'focus', 'silent', or 'manual'."""
    return _COMPANION.proactive_engine.set_mode(mode)


async def be_quiet(minutes: int = 30) -> str:
    """Silences ULTRON's proactive speech for a specified number of minutes."""
    return _COMPANION.proactive_engine.set_quiet_minutes(minutes)
