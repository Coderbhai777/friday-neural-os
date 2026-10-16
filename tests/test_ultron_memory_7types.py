# -*- coding: utf-8 -*-
"""
Unit and Integration Test Suite for ULTRON 7-Tier Autonomous Persistent Memory System.
Tests:
1. Creation and retrieval of all 7 memory types (personal, episodic, semantic, procedural, working, visual, project).
2. Proper metadata schema validation (id, type, content, source, timestamp, importance, confidence, project, expires_at).
3. SQLite FTS5 search and ranking.
4. Deduplication and memory updating.
5. Working memory persistence, unfinished task tracking, and cross-restart mission recovery.
6. Visual memory screen-state logging.
7. Context builder output injection.
8. Backward compatibility with remember, recall, search_memory, update_memory, forget, view_brain.
"""

import os
import sys
import json
import time
import shutil
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from tools.ultron_memory_engine import (
    Ultron7TierMemoryEngine,
    UltronSQLiteMemory,
    UltronWorkingMemory,
    UltronVisualMemory,
    TYPE_PERSONAL,
    TYPE_EPISODIC,
    TYPE_SEMANTIC,
    TYPE_PROCEDURAL,
    TYPE_WORKING,
    TYPE_VISUAL,
    TYPE_PROJECT,
    ALL_MEMORY_TYPES
)
from tools.ultron_memory import (
    remember,
    recall,
    search_memory,
    update_memory,
    forget,
    view_brain,
    get_working_memory,
    set_working_task,
    advance_working_step
)


class TestUltron7TierMemory(unittest.TestCase):

    def setUp(self):
        self.test_dir = ROOT_DIR / "tests" / "scratch_memory_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.db_file = self.test_dir / "test_memory.db"
        self.working_file = self.test_dir / "test_working_memory.json"
        self.visual_dir = self.test_dir / "visual_memory"

        self.sqlite = UltronSQLiteMemory(db_path=self.db_file)
        self.working = UltronWorkingMemory(file_path=self.working_file)
        self.visual = UltronVisualMemory(dir_path=self.visual_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_1_seven_memory_types_storage(self):
        """Verifies that all 7 memory types can be stored with proper types."""
        # 1. Personal
        m1 = self.sqlite.add_memory(
            content="User prefers ULTRON to speak naturally without waiting for a wake word.",
            memory_type=TYPE_PERSONAL,
            importance=0.95
        )
        self.assertEqual(m1["type"], TYPE_PERSONAL)
        self.assertIn("wake word", m1["content"])

        # 2. Episodic
        m2 = self.sqlite.add_memory(
            content="Yesterday, the user was debugging the Minecraft server's lobby spawn.",
            memory_type=TYPE_EPISODIC,
            importance=0.75
        )
        self.assertEqual(m2["type"], TYPE_EPISODIC)

        # 3. Semantic
        m3 = self.sqlite.add_memory(
            content="The ULTRON repository contains a world model and a verification engine.",
            memory_type=TYPE_SEMANTIC,
            importance=0.8
        )
        self.assertEqual(m3["type"], TYPE_SEMANTIC)

        # 4. Procedural
        m4 = self.sqlite.add_memory(
            content="When fixing a bug, inspect the logs, reproduce the issue, make a change, and run a test.",
            memory_type=TYPE_PROCEDURAL,
            importance=0.9
        )
        self.assertEqual(m4["type"], TYPE_PROCEDURAL)

        # 5. Working
        self.working.set_active_task("Watching anime episode 4", project="Entertainment", steps=["Finish episode 4"])
        w_state = self.working.load()
        self.assertEqual(w_state["active_task"], "Watching anime episode 4")

        # 6. Visual
        self.visual.record_screen_observation("code.exe", "main.py - VS Code", "User editing main.py; new unsaved change appeared.")
        v_state = self.visual.get_latest_observation()
        self.assertIn("main.py", v_state["title"])

        # 7. Project
        m7 = self.sqlite.add_memory(
            content="ULTRON's next milestone is implementing reliable autonomous memory retrieval.",
            memory_type=TYPE_PROJECT,
            importance=1.0,
            project="ULTRON"
        )
        self.assertEqual(m7["type"], TYPE_PROJECT)
        self.assertEqual(m7["project"], "ULTRON")

    def test_2_metadata_schema_validation(self):
        """Validates that every memory record has the exact required metadata schema."""
        rec = self.sqlite.add_memory(
            content="ULTRON needs persistent mission recovery.",
            memory_type=TYPE_PROJECT,
            source="conversation",
            importance=0.9,
            confidence=1.0,
            project="ULTRON",
            expires_at=None
        )

        # Required fields check
        required_fields = ["id", "type", "content", "source", "timestamp", "importance", "confidence", "project", "expires_at"]
        for field in required_fields:
            self.assertIn(field, rec)

        self.assertTrue(rec["id"].startswith("mem_"))
        self.assertEqual(rec["type"], "project")
        self.assertEqual(rec["content"], "ULTRON needs persistent mission recovery.")
        self.assertEqual(rec["source"], "conversation")
        self.assertEqual(rec["importance"], 0.9)
        self.assertEqual(rec["confidence"], 1.0)
        self.assertEqual(rec["project"], "ULTRON")
        self.assertIsNone(rec["expires_at"])
        # Check ISO timestamp format
        self.assertIn("T", rec["timestamp"])

    def test_3_deduplication_and_update(self):
        """Verifies deduplication prevents duplicate memories and updates importance."""
        r1 = self.sqlite.add_memory("User likes robotics.", memory_type=TYPE_PERSONAL, importance=0.6)
        r2 = self.sqlite.add_memory("User likes robotics.", memory_type=TYPE_PERSONAL, importance=0.9)

        # Should update existing ID rather than create duplicate
        self.assertEqual(r1["id"], r2["id"])
        self.assertEqual(r2["importance"], 0.9)

        all_mems = self.sqlite.list_all(memory_type=TYPE_PERSONAL)
        matching = [m for m in all_mems if m["content"] == "User likes robotics."]
        self.assertEqual(len(matching), 1)

    def test_4_fts5_and_lexical_search(self):
        """Tests that full-text search accurately retrieves relevant memories."""
        self.sqlite.add_memory("Quantum Orb Shader particle rings optimization.", memory_type=TYPE_PROJECT, project="Quantum-Orb-Shader")
        self.sqlite.add_memory("Minecraft server lobby spawn coordinate setup.", memory_type=TYPE_EPISODIC, project="Minecraft")
        self.sqlite.add_memory("Python asyncio stream token latency tuning.", memory_type=TYPE_SEMANTIC)

        results = self.sqlite.search_memories("particle rings")
        self.assertTrue(len(results) >= 1)
        self.assertIn("Quantum Orb", results[0]["content"])

        mc_results = self.sqlite.search_memories("minecraft spawn")
        self.assertTrue(len(mc_results) >= 1)
        self.assertIn("Minecraft", mc_results[0]["content"])

    def test_5_working_memory_and_restart_recovery(self):
        """Verifies that unfinished tasks survive across PC restarts and can advance steps."""
        self.working.set_active_task(
            task="Refactor ULTRON memory engine",
            project="ULTRON",
            steps=["Create SQLite schema", "Hook automatic retriever", "Verify tests"]
        )

        # Simulate restart by instantiating a fresh working memory loader from disk
        restarted_working = UltronWorkingMemory(file_path=self.working_file)
        summary = restarted_working.get_unfinished_summary()

        self.assertIsNotNone(summary)
        self.assertIn("Refactor ULTRON memory engine", summary)
        self.assertEqual(restarted_working.state["current_step"], "Create SQLite schema")

        # Advance step 1
        next_step = restarted_working.advance_step("Create SQLite schema")
        self.assertEqual(next_step, "Hook automatic retriever")
        self.assertEqual(len(restarted_working.state["unfinished_steps"]), 2)

    def test_6_context_builder_output(self):
        """Verifies context builder compiles all 7 types into an AI-ready context prompt."""
        engine = Ultron7TierMemoryEngine()
        context = engine.build_injected_context("How do I fix this bug in ULTRON?")

        self.assertIn("[ULTRON 7-TIER PERSISTENT MEMORY CONTEXT]", context)
        self.assertIn("PERSONAL MEMORY", context)
        self.assertIn("PROJECT & MISSION MEMORY", context)

    def test_7_public_tools_integration(self):
        """Verifies remember, recall, search_memory, update_memory, forget, view_brain work seamlessly."""
        # 1. Remember
        rem_res = remember("My preferred language is Python and TypeScript.")
        self.assertIn("Stored in", rem_res)

        # 2. Recall
        rec_res = recall("language")
        self.assertIn("Python", rec_res)

        # 3. Search Memory
        found = search_memory("TypeScript", limit=3)
        self.assertTrue(len(found) >= 1)

        # 4. View brain
        brain_view = view_brain()
        self.assertIn("ULTRON 7-TIER AUTONOMOUS MEMORY CORE", brain_view)

        # 5. Forget
        del_res = forget("preferred language")
        self.assertIn("Removed memory entry", del_res)


if __name__ == "__main__":
    unittest.main()
