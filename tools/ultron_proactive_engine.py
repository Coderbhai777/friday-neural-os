# -*- coding: utf-8 -*-
"""
ULTRON Ω — Proactive Companion Engine & 15-Second Silence Policy
Evaluates:
- What the user is currently doing & visible context
- Application & activity classification
- Time since last user speech, keyboard/mouse input, and last proactive statement
- Strict 15-second silence evaluation threshold (never speaks automatically every 15s)
- Cooldown & backoff policy (45–90s baseline, exponential when ignored)
- Decision State: SPEAK_NOW | WAIT | ASK_PERMISSION | SILENTLY_OBSERVE | DO_NOT_DISTURB
- Voice commands: 'stop talking', 'be quiet for X minutes', 'only speak when I ask', 'resume proactive'
"""

import time
import threading
from typing import Dict, Any, Optional, Tuple, List
try:
    from tools.ultron_vision_pipeline import get_active_window_info
except ImportError:
    from friday_tools.ultron_vision_pipeline import get_active_window_info

# Decision States
DECISION_SPEAK_NOW = "SPEAK_NOW"
DECISION_WAIT = "WAIT"
DECISION_ASK_PERMISSION = "ASK_PERMISSION"
DECISION_SILENTLY_OBSERVE = "SILENTLY_OBSERVE"
DECISION_DO_NOT_DISTURB = "DO_NOT_DISTURB"

# Modes
MODE_CONVERSATIONAL = "conversational"
MODE_FOCUS = "focus"
MODE_SILENT = "silent"
MODE_MANUAL = "manual_only"

APP_POLICIES = {
    # Games -> Always silent
    "games": ["steam.exe", "valorant.exe", "minecraft.exe", "genshinimpact.exe", "epicgames.exe", "gta5.exe"],
    # Meetings / Calls -> Always quiet
    "meetings": ["zoom.exe", "teams.exe", "discord.exe", "slack.exe", "skype.exe"],
    # Coding -> Focus mode
    "coding": ["code.exe", "devenv.exe", "pycharm64.exe", "clion64.exe", "sublime_text.exe", "windowsterminal.exe"]
}


class ProactiveCompanionEngine:
    def __init__(self):
        self.mode = MODE_CONVERSATIONAL
        self.dnd_enabled = False
        self.quiet_until = 0.0

        # Timing telemetry
        self.last_user_speech_at = time.time()
        self.last_user_input_at = time.time()
        self.last_proactive_spoken_at = 0.0
        self.consecutive_ignored_turns = 0

        # Cooldown parameters
        self.silence_threshold = 15.0       # 15 seconds without user speech before evaluating
        self.base_cooldown = 60.0           # 60 seconds baseline cooldown between proactive remarks
        self.max_cooldown = 300.0           # 5 minutes maximum backoff
        self.recent_remarks: List[str] = [] # Prevents repetitive remarks

        self.lock = threading.Lock()

    # ---------------------------------------------------------
    # Telemetry Hooks
    # ---------------------------------------------------------

    def notify_user_speech(self):
        """Call when user speaks or sends an instruction."""
        with self.lock:
            self.last_user_speech_at = time.time()
            self.consecutive_ignored_turns = 0

    def notify_user_input(self):
        """Call when keyboard or mouse movement is detected."""
        with self.lock:
            self.last_user_input_at = time.time()

    def get_current_cooldown(self) -> float:
        """Calculates current cooldown with exponential backoff if ignored."""
        if self.consecutive_ignored_turns <= 0:
            return self.base_cooldown
        # 60s, 90s, 135s, 202s up to max_cooldown
        multiplier = 1.5 ** min(self.consecutive_ignored_turns, 4)
        return min(self.max_cooldown, self.base_cooldown * multiplier)

    # ---------------------------------------------------------
    # Decision Evaluation Logic
    # ---------------------------------------------------------

    def evaluate_initiative(
        self,
        screen_analysis: Dict[str, Any],
        is_user_speaking: bool = False,
        is_tts_speaking: bool = False,
        system_idle_sec: float = 0.0
    ) -> Tuple[str, Optional[str], str]:
        """
        Determines whether ULTRON should speak aloud.
        Returns:
            (DecisionState, SpokenText, Reason)
        """
        with self.lock:
            now = time.time()

            # 1. Check Do Not Disturb & Quiet Timer
            if self.dnd_enabled:
                return DECISION_DO_NOT_DISTURB, None, "Do Not Disturb is active."

            if now < self.quiet_until:
                remaining_mins = int((self.quiet_until - now) / 60) + 1
                return DECISION_DO_NOT_DISTURB, None, f"Quiet mode active for another {remaining_mins} min(s)."

            if self.mode == MODE_MANUAL:
                return DECISION_SILENTLY_OBSERVE, None, "Manual assistant mode active: only speaks when summoned."

            # 2. Check if either user or TTS is currently speaking
            if is_user_speaking:
                return DECISION_WAIT, None, "User is currently speaking; barge-in guard active."

            if is_tts_speaking:
                return DECISION_WAIT, None, "ULTRON is already speaking."

            # 3. Privacy Shield
            if screen_analysis.get("is_sensitive", False):
                return DECISION_SILENTLY_OBSERVE, None, "Sensitive window active; observation shielded."

            # 4. Application-specific policies
            win_info = get_active_window_info()
            app = win_info.get("app", "").lower()

            if any(game_app in app for game_app in APP_POLICIES["games"]):
                return DECISION_SILENTLY_OBSERVE, None, f"Gaming in {app}; silent observation policy."

            if any(call_app in app for call_app in APP_POLICIES["meetings"]):
                return DECISION_SILENTLY_OBSERVE, None, f"Meeting/call in {app}; silent policy."

            # 5. 15-Second Silence Policy
            # Evaluate only after >= 15 seconds of silence from the user
            silence_duration = now - self.last_user_speech_at
            if silence_duration < self.silence_threshold:
                return DECISION_WAIT, None, f"User was active recently ({int(silence_duration)}s < 15s threshold)."

            # 6. Cooldown Policy
            cooldown = self.get_current_cooldown()
            time_since_last_proactive = now - self.last_proactive_spoken_at
            if time_since_last_proactive < cooldown:
                remaining = int(cooldown - time_since_last_proactive)
                return DECISION_WAIT, None, f"Cooling down ({remaining}s remaining of {int(cooldown)}s window)."

            # 7. Check if there is a genuinely useful, concrete observation
            observation = screen_analysis.get("suggested_observation")
            confidence = float(screen_analysis.get("confidence", 0.0))

            if not observation or confidence < 0.65:
                return DECISION_SILENTLY_OBSERVE, None, "No high-confidence, useful remark available."

            # 8. Prevent duplicate or repetitive remarks
            clean_obs = observation.strip().lower()
            if any(clean_obs == prev.lower() for prev in self.recent_remarks[-6:]):
                return DECISION_SILENTLY_OBSERVE, None, "Observation already spoken recently; suppressing duplicate."

            # All gates passed -> SPEAK_NOW
            self.last_proactive_spoken_at = now
            self.consecutive_ignored_turns += 1
            self.recent_remarks.append(observation)
            if len(self.recent_remarks) > 20:
                self.recent_remarks.pop(0)

            return DECISION_SPEAK_NOW, observation, f"Confidence {confidence:.2f} with verified context: {screen_analysis.get('activity')}."

    # ---------------------------------------------------------
    # Voice Control Commands
    # ---------------------------------------------------------

    def set_quiet_minutes(self, minutes: int) -> str:
        """Sets quiet mode for specified number of minutes."""
        with self.lock:
            self.quiet_until = time.time() + (minutes * 60)
            return f"Understood, Sir. I will remain quiet for the next {minutes} minutes."

    def stop_talking(self) -> str:
        """Cancels proactive speech and mutes ongoing voice."""
        with self.lock:
            self.last_proactive_spoken_at = time.time() + 60.0 # Delay next evaluation by 60s
            try:
                from tools.tts_engine import stop_speech
                stop_speech()
            except Exception:
                pass
            return "Understood. Standing by silently."

    def set_mode(self, mode_name: str) -> str:
        """Changes companion mode: conversational, focus, silent, or manual_only."""
        with self.lock:
            m = mode_name.lower().strip()
            if "manual" in m or "ask" in m:
                self.mode = MODE_MANUAL
                return "Manual mode engaged. I will only speak when you ask directly."
            elif "silent" in m:
                self.mode = MODE_SILENT
                self.dnd_enabled = True
                return "Silent mode active. All proactive voice is disabled."
            elif "focus" in m or "code" in m:
                self.mode = MODE_FOCUS
                self.dnd_enabled = False
                self.base_cooldown = 120.0
                return "Focus mode enabled. Proactive frequency dialed down for deep work."
            else:
                self.mode = MODE_CONVERSATIONAL
                self.dnd_enabled = False
                self.base_cooldown = 60.0
                return "Conversational companion mode restored."
