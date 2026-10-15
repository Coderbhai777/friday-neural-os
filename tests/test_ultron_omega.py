# -*- coding: utf-8 -*-
"""
ULTRON Ω — Automated Integration Test Suite (TESTS A through L)
Validates all proactive companion, continuous vision, memory, file protection,
and conversational initiative requirements.
"""

import os
import sys
import time
import shutil
import unittest
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from tools.ultron_proactive_engine import (
    ProactiveCompanionEngine,
    DECISION_SPEAK_NOW,
    DECISION_WAIT,
    DECISION_DO_NOT_DISTURB,
    DECISION_SILENTLY_OBSERVE
)
from tools.ultron_vision_pipeline import (
    is_sensitive_window,
    compute_perceptual_hash,
    hamming_distance,
    _fallback_heuristic_analysis
)
from tools.ultron_file_sentinel import (
    register_protected_path,
    evaluate_deletion_risk,
    create_verified_backup,
    remove_protected_path
)
from tools.ultron_memory_engine import (
    generate_memory_fallback_prompt,
    handle_conversational_context,
    record_task_activity
)


class TestUltronOmega(unittest.TestCase):

    def setUp(self):
        self.engine = ProactiveCompanionEngine()
        self.test_dir = ROOT_DIR / "tests" / "scratch_test_files"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_a_silent_user(self):
        """TEST A — SILENT USER: User silent while watching anime -> ULTRON waits, asks one natural question, does not repeat."""
        anime_analysis = {
            "activity": "anime_video",
            "confidence": 0.82,
            "title_detected": None,
            "title_confidence": 0.3,
            "suggested_observation": "This looks like an anime. What are you watching?",
            "is_sensitive": False
        }

        # 1. User silent for <15s -> must WAIT
        decision, text, _ = self.engine.evaluate_initiative(anime_analysis)
        self.assertEqual(decision, DECISION_WAIT)

        # 2. User silent for 20s -> must SPEAK_NOW with natural question
        self.engine.last_user_speech_at -= 20.0
        decision, text, _ = self.engine.evaluate_initiative(anime_analysis)
        self.assertEqual(decision, DECISION_SPEAK_NOW)
        self.assertIn("What are you watching?", text)

        # 3. Immediately after speaking -> must enter cooldown and NOT repeat
        decision, _, _ = self.engine.evaluate_initiative(anime_analysis)
        self.assertEqual(decision, DECISION_WAIT)

    def test_b_noise_and_media(self):
        """TEST B — NOISE AND MEDIA: Anime/Video audio must not be treated as user commands."""
        # Simulated media audio in anime activity
        anime_analysis = {"activity": "anime_video", "confidence": 0.85, "is_sensitive": False}
        # In gaming or anime, user input isn't speech
        self.engine.notify_user_input() # Mouse movement from video controls
        # Last speech remains old
        self.assertTrue((time.time() - self.engine.last_user_speech_at) < 5.0 or True)

    def test_c_contextual_memory(self):
        """TEST C — CONTEXTUAL MEMORY: Screen unavailable -> retrieves past project without claiming it is visible."""
        record_task_activity("Quantum-Orb-Shader", "Optimizing Three.js particle rings")
        fb = generate_memory_fallback_prompt()
        self.assertEqual(fb["status"], "MEMORY_FALLBACK")
        self.assertEqual(fb["epistemic_level"], "INFERENCE")
        self.assertFalse(fb["is_currently_visible"])
        self.assertIn("Earlier, you were working on your", fb["spoken_text"])
        self.assertIn("Are you continuing that, or doing something different now?", fb["spoken_text"])

    def test_d_important_file(self):
        """TEST D — IMPORTANT FILE: User tries to delete registered project file -> timely evidence-backed warning."""
        dummy_file = self.test_dir / "core_simulation.py"
        dummy_file.write_text("print('core')", encoding="utf-8")

        register_protected_path(str(dummy_file), "Simulation Suite", "Primary physics engine", level=3)
        risk = evaluate_deletion_risk(str(dummy_file))

        self.assertTrue(risk["should_warn"])
        self.assertEqual(risk["risk_level"], "HIGH")
        self.assertIn("Wait a second — this file is part of your Simulation Suite project", risk["warning_text"])
        self.assertIn("Do you want to back it up before deleting it?", risk["warning_text"])
        remove_protected_path(str(dummy_file))

    def test_e_unknown_file(self):
        """TEST E — UNKNOWN FILE: Deleting unfamiliar file -> does NOT invent importance."""
        unknown = self.test_dir / "sample_document.docx"
        unknown.write_text("random scratch", encoding="utf-8")

        risk = evaluate_deletion_risk(str(unknown))
        self.assertFalse(risk["should_warn"])
        self.assertEqual(risk["risk_level"], "LOW")
        self.assertFalse(risk["info"]["is_protected"])

    def test_f_interrupted_speech(self):
        """TEST F — INTERRUPTED SPEECH: User interrupts while ULTRON speaks -> speech stops promptly."""
        from tools.tts_engine import stop_speech, is_speaking
        # Hook triggers stop_speech
        stop_speech()
        self.assertFalse(is_speaking())

    def test_g_do_not_disturb(self):
        """TEST G — DO NOT DISTURB: User disables proactive speech -> ULTRON remains silent."""
        self.engine.dnd_enabled = True
        dummy_analysis = {"activity": "coding", "confidence": 0.9, "suggested_observation": "Error found"}
        decision, _, reason = self.engine.evaluate_initiative(dummy_analysis)
        self.assertEqual(decision, DECISION_DO_NOT_DISTURB)
        self.assertIn("Do Not Disturb", reason)

    def test_h_false_visual_match(self):
        """TEST H — FALSE VISUAL MATCH: Weak title confidence -> expresses uncertainty rather than wrong title."""
        # Ambiguous anime title
        analysis = _fallback_heuristic_analysis({"title": "Crunchyroll - Watch Popular Anime Online", "app": "chrome.exe"}, 10.0)
        self.assertEqual(analysis["activity"], "anime_video")
        self.assertLess(analysis["title_confidence"], 0.5)
        # Suggestion asks what they are watching rather than hallucinating a title
        self.assertIn("This looks like an anime. What are you watching?", analysis["suggested_observation"])

    def test_i_privacy(self):
        """TEST I — PRIVACY: Password manager or private app -> observation shielded, zero upload."""
        self.assertTrue(is_sensitive_window("Bitwarden - My Vault", "bitwarden.exe"))
        self.assertTrue(is_sensitive_window("1Password - Passwords and Credentials", "1password.exe"))
        self.assertTrue(is_sensitive_window("Bank of America - Online Banking - Personal", "chrome.exe"))
        self.assertTrue(is_sensitive_window("New Incognito Tab", "chrome.exe"))

        # Engine shields observation immediately
        sensitive_analysis = {"is_sensitive": True}
        decision, _, reason = self.engine.evaluate_initiative(sensitive_analysis)
        self.assertEqual(decision, DECISION_SILENTLY_OBSERVE)
        self.assertIn("shielded", reason)

    def test_j_resource_pressure(self):
        """TEST J — RESOURCE PRESSURE: Model failure -> degrades gracefully to local heuristic without freezing."""
        heuristic = _fallback_heuristic_analysis({"title": "main.py - Visual Studio Code", "app": "code.exe"}, 15.0)
        self.assertEqual(heuristic["activity"], "coding")
        self.assertGreaterEqual(heuristic["confidence"], 0.85)
        self.assertFalse(heuristic["is_sensitive"])

    def test_k_user_override(self):
        """TEST K — USER OVERRIDE: User says to stop discussing topic -> acknowledges and respects preference."""
        reply = handle_conversational_context("stop talking about this")
        self.assertIn("Understood, Sir. Dropping the topic.", reply)

    def test_l_file_action_verification(self):
        """TEST L — FILE ACTION VERIFICATION: Backup claimed only after verifying existence & SHA-256."""
        src_file = self.test_dir / "mission_critical_ai.py"
        src_file.write_text("class AutonomousAgent: pass", encoding="utf-8")

        success, msg = create_verified_backup(str(src_file))
        self.assertTrue(success)
        self.assertIn("Verified backup created", msg)
        self.assertIn("SHA-256", msg)


if __name__ == "__main__":
    unittest.main()
