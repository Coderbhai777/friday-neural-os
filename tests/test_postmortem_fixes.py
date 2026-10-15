# -*- coding: utf-8 -*-
"""
Verification tests for Architectural Post-Mortem fixes:
1. AI deadline enforcement & fallback speech isolation
2. Charon TTS timeout and worker thread control protocol
3. Single-audio-owner queue isolation & barge-in invalidation
4. Unified sentinel integration with ULTRON Companion Bridge
"""

import sys
import time
import unittest
import asyncio
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import tools.tts_engine as tts_engine
import tools.ai_client as ai_client
from tools.ultron_companion_bridge import _COMPANION, start_ultron_companion, stop_ultron_companion
import tools.ambient_screen_sentinel as ambient_screen_sentinel
import tools.proactive_screen_vision as proactive_screen_vision


class TestPostMortemFixes(unittest.TestCase):

    def test_1_speech_session_invalidation_and_barge_in(self):
        """Verify that barge-in stops speech and invalidates queued requests."""
        req_1 = tts_engine.new_speech_session()
        self.assertGreater(req_1, 0)

        # Enqueue text under req_1
        enqueued = tts_engine.enqueue_sentence(f"Message under request {req_1}", req_1)
        self.assertTrue(enqueued)
        
        # Stop speech (barge-in): advances request id, invalidating req_1
        tts_engine.stop_speech()
        self.assertGreater(tts_engine.get_current_request_id(), req_1)
        # Give worker a brief moment to process the STOP control command
        time.sleep(0.1)
        self.assertTrue(tts_engine._speech_queue.empty())

        # Verify new speech session gets incremented ID and matches current
        req_2 = tts_engine.new_speech_session()
        self.assertGreater(req_2, req_1)
        self.assertEqual(tts_engine.get_current_request_id(), req_2)

    def test_2_charon_voice_configuration(self):
        """Verify that Charon remains primary voice and RyanNeural is never used."""
        self.assertEqual(tts_engine.GEMINI_VOICE_NAME, "Charon")
        self.assertIn("ChristopherNeural", tts_engine.EDGE_FALLBACK_VOICE)
        self.assertNotIn("Ryan", tts_engine.EDGE_FALLBACK_VOICE)

    def test_3_unified_sentinels_delegate_to_companion(self):
        """Verify that ambient_screen_sentinel and proactive_screen_vision route to _COMPANION."""
        loop = asyncio.new_event_loop()
        try:
            # Start sentinel
            start_msg = loop.run_until_complete(ambient_screen_sentinel.start_screen_sentinel())
            self.assertIn("Unified Engine", start_msg)
            self.assertTrue(_COMPANION.running)

            # Check status
            status_msg = loop.run_until_complete(ambient_screen_sentinel.get_screen_sentinel_status())
            self.assertIn("ACTIVE", status_msg)

            # Stop sentinel
            stop_msg = loop.run_until_complete(ambient_screen_sentinel.stop_screen_sentinel())
            self.assertFalse(_COMPANION.running)

            # Start proactive vision
            pv_start = loop.run_until_complete(proactive_screen_vision.start_proactive_vision())
            self.assertIn("ACTIVE", pv_start)
            self.assertTrue(_COMPANION.running)

            # Stop proactive vision
            loop.run_until_complete(proactive_screen_vision.stop_proactive_vision())
            self.assertFalse(_COMPANION.running)
        finally:
            loop.close()

    def test_4_total_ai_deadline_constant(self):
        """Verify strict total request deadline constant is 9.0s or lower."""
        self.assertLessEqual(ai_client.TOTAL_REQUEST_DEADLINE_SEC, 9.0)
        self.assertLessEqual(ai_client.PRIMARY_PROVIDER_TIMEOUT_SEC, 6.0)

    def test_5_sync_wrapper_no_deadlock(self):
        """Verify that generate_ai_response returns cleanly without context manager deadlock."""
        t0 = time.time()
        # Call with kwargs to verify backwards compatibility and bounded deadline
        res = ai_client.generate_ai_response("Hello test", max_tokens=10)
        elapsed = time.time() - t0
        self.assertLess(elapsed, 12.0)
        self.assertIsInstance(res, str)


if __name__ == "__main__":
    unittest.main()
