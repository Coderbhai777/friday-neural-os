# -*- coding: utf-8 -*-
"""
ULTRON Ω — Central Companion Orchestration Bridge (Event-Driven & Silence-by-Default Architecture)
Unifies:
1. Event-Driven Desktop Observation (Win32 window focus & title changes, debounced)
2. Silence as Default: Zero continuous periodic cloud vision polling; zero rate-limit waste
3. Local Roadblock Triggers: Invokes multimodal inspection ONLY on active errors/crashes or explicit user request
4. Single-Audio-Owner Speech Integration: Dispatches remarks to tts_engine without mixer collisions
5. Full Barge-In Interruption Support
"""

import os
import sys
import time
import threading
from typing import Dict, Any, Optional

try:
    from tools.ultron_vision_pipeline import (
        capture_screen_direct,
        get_active_window_info,
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
    import tools.tts_engine as tts_engine
except ImportError:
    from friday_tools.ultron_vision_pipeline import (
        capture_screen_direct,
        get_active_window_info,
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
    import friday_tools.tts_engine as tts_engine


class UltronOmegaCompanion:
    """
    Event-driven desktop companion.
    Monitors OS focus events, debounces bursts, and maintains silence by default.
    """

    def __init__(self):
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.proactive_engine = ProactiveCompanionEngine()

        self.last_window_info: Dict[str, Any] = {}
        self.last_window_change_time = 0.0
        self.last_screen_analysis: Dict[str, Any] = {}
        self.lock = threading.Lock()

    def start(self):
        """Starts the event-driven companion background monitor."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="ULTRON_CompanionLoop")
        self._thread.start()
        print("[ULTRON OMEGA Companion] Event-driven desktop observer online (Silence-by-Default active).")

    def stop(self):
        """Stops the companion background monitor."""
        self.running = False

    def notify_user_spoke(self):
        """Notifies companion when user speaks (cancels ongoing speech and resets cooldown)."""
        self.proactive_engine.notify_user_speech()
        tts_engine.stop_speech()

    def _speak_aloud(self, text: str):
        """Dispatches text to the single-owner speech worker."""
        if not text:
            return
        print(f"\n[ULTRON OMEGA]: {text}")
        tts_engine.speak_text_sync(text)

    def inspect_screen_now(self) -> Dict[str, Any]:
        """Performs on-demand live desktop screen capture and visual analysis."""
        win_info = get_active_window_info()
        img = capture_screen_direct(max_dim=768)
        if not img:
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

    def _has_local_roadblock(self, win_info: Dict[str, Any]) -> bool:
        """
        Fast zero-API heuristic: checks if active window title or app indicates an error/crash.
        Prevents wasting cloud multimodal API calls on ordinary browsing or coding.
        """
        title = (win_info.get("title") or "").lower()
        app = (win_info.get("app") or "").lower()

        roadblock_keywords = [
            "error", "exception", "traceback", "crash", "failed",
            "not responding", "syntaxerror", "build failed", "fatal",
            "compilation error", "runtime error"
        ]
        return any(kw in title for kw in roadblock_keywords)

    def _run_loop(self):
        """Lightweight event-driven loop. Zero cloud polling on normal operations."""
        while self.running:
            time.sleep(1.5)  # 1.5s local metadata poll
            try:
                now = time.time()
                win_info = get_active_window_info()

                hwnd_changed = win_info.get("hwnd") != self.last_window_info.get("hwnd")
                title_changed = win_info.get("title") != self.last_window_info.get("title")

                if hwnd_changed or title_changed:
                    self.last_window_info = win_info
                    self.last_window_change_time = now

                # Debounce window switch bursts (wait until stable for at least 3 seconds)
                if now - self.last_window_change_time < 3.0:
                    continue

                # SILENCE IS DEFAULT:
                # Only trigger visual inference if a concrete local roadblock/error is observed in window metadata
                if self._has_local_roadblock(win_info):
                    cooldown = self.proactive_engine.get_current_cooldown()
                    if now - self.proactive_engine.last_proactive_spoken_at >= cooldown:
                        img = capture_screen_direct(max_dim=640)
                        if img:
                            analysis = analyze_screen_with_ai(img, win_info, idle_sec=0.0)
                            self.last_screen_analysis = analysis

                            decision, spoken_text, reason = self.proactive_engine.evaluate_initiative(
                                screen_analysis=analysis,
                                is_user_speaking=False,
                                is_tts_speaking=tts_engine.is_speaking(),
                                system_idle_sec=0.0
                            )

                            if decision == DECISION_SPEAK_NOW and spoken_text:
                                self._speak_aloud(spoken_text)

            except Exception as e:
                time.sleep(2.0)


# Global singleton instance
_COMPANION = UltronOmegaCompanion()


async def start_ultron_companion() -> str:
    """Starts the ULTRON Ω event-driven proactive companion."""
    _COMPANION.start()
    return "ULTRON Ω Event-Driven Companion Online (Silence-by-Default active, zero cloud polling)."


async def stop_ultron_companion() -> str:
    """Pauses the ULTRON Ω proactive companion."""
    _COMPANION.stop()
    return "ULTRON Ω Proactive Companion paused, Sir."


async def force_screen_perception() -> str:
    """Explicitly triggers on-demand screen inspection and returns observation."""
    analysis = _COMPANION.inspect_screen_now()
    obs = analysis.get("suggested_observation")
    if obs:
        _COMPANION._speak_aloud(obs)
        return f"[OBSERVATION]: {obs}"
    return f"Desktop inspected: {analysis.get('details', 'Active')}"
