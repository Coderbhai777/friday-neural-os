# -*- coding: utf-8 -*-
"""
ULTRON Ω — Autonomous Computer Agent Integration & Acceptance Test Suite
Validates Section 10 Requirements:
TEST A — YouTube Navigation (General browser search & video playback verification)
TEST B — Channel Subscription (Auth detection & refusal to fake unauthenticated success)
TEST C — Control Panel & Programs and Features (OS discovery & window verification)
TEST D — Unfamiliar File Task (Sandbox file generation, organization by extension, verification)
TEST E — Error Recovery (Bounded retry, re-observation, and failure reporting)
TEST F — Persistent Memory & Task Recovery Across Restarts (SQLite working memory restoration)
TEST G — Safety Policy & Emergency Stop (Risk tier gates and immediate halting)
"""

import os
import sys
import time
import shutil
import unittest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from tools.ultron_universal_engine import (
    UNIVERSAL_ENGINE,
    VisualDesktopExecutor,
    BrowserExecutor,
    OSExecutor,
    SkillForge,
    SANDBOX_DIR
)
from tools.ultron_autonomous_agent import (
    UltronAutonomousAgent,
    TaskState,
    TaskStep,
    STEP_COMPLETED,
    STEP_FAILED,
    STEP_BLOCKED,
    STEP_PENDING,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_BLOCKED,
    TASK_STOPPED
)
from tools.security_policy import (
    evaluate_action_risk,
    check_action_permitted,
    trigger_emergency_stop,
    reset_emergency_stop,
    is_emergency_stopped,
    RISK_LOW,
    RISK_MEDIUM,
    RISK_HIGH,
    RISK_BLOCKED
)


class TestUltronAutonomousAgent(unittest.TestCase):

    def setUp(self):
        self.agent = UltronAutonomousAgent()
        reset_emergency_stop()
        self.test_dir = ROOT_DIR / "tests" / "scratch_autonomous_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        reset_emergency_stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.agent.clear_checkpoint()

    # -----------------------------------------------------------------
    # TEST A: YOUTUBE NAVIGATION & PLAYBACK
    # -----------------------------------------------------------------
    def test_a_youtube_navigation_and_playback(self):
        """TEST A — Goal: 'go to the TechGPT YouTube channel and play its latest video'"""
        goal = "go to the TechGPT YouTube channel and play its latest video"
        steps = self.agent.decompose_goal(goal)
        
        # Verify no hardcoded TechGPT tool was used
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0].capability, "BROWSER")
        self.assertIn("search_query=TechGPT", steps[0].parameters["url"])
        self.assertEqual(steps[2].action_type, "PLAY_VIDEO")

        # Mock browser execution to simulate navigation and playback verification
        loop = asyncio.new_event_loop()
        try:
            with patch.object(self.agent.engine.browser, "navigate", return_value={"status": "SUCCESS", "url": "https://www.youtube.com/results?search_query=TechGPT", "title": "TechGPT - YouTube"}), \
                 patch.object(self.agent.engine.browser, "detect_auth_or_captcha", return_value={"captcha_detected": False}), \
                 patch.object(self.agent.engine.browser, "find_and_click_element", return_value={"status": "SUCCESS", "method": "text_xpath"}), \
                 patch.object(self.agent.engine.browser, "play_video", return_value={"status": "SUCCESS", "playback_active": True, "details": {"paused": False}}):
                
                result = loop.run_until_complete(self.agent.execute_goal(goal))
                self.assertEqual(result["status"], TASK_COMPLETED)
                self.assertEqual(result["steps_completed"], 3)
                self.assertIn("playback verified active", result["evidence"][2].lower())
        finally:
            loop.close()

    # -----------------------------------------------------------------
    # TEST B: CHANNEL SUBSCRIPTION & AUTH CHECK
    # -----------------------------------------------------------------
    def test_b_channel_subscription_auth_check(self):
        """TEST B — Goal: 'Subscribe to the TechGPT YouTube channel.' Must pause/block when unauthenticated."""
        goal = "Subscribe to the TechGPT YouTube channel."
        steps = self.agent.decompose_goal(goal)
        self.assertGreaterEqual(len(steps), 2)
        self.assertEqual(steps[1].action_type, "SUBSCRIBE_CHANNEL")

        loop = asyncio.new_event_loop()
        try:
            # Simulate unauthenticated browser state (Sign in button present)
            mock_driver = MagicMock()
            mock_button = MagicMock()
            mock_button.is_displayed.return_value = True
            mock_driver.find_elements.return_value = [mock_button]

            with patch.object(self.agent.engine.browser, "navigate", return_value={"status": "SUCCESS"}), \
                 patch.object(self.agent.engine.browser, "detect_auth_or_captcha", return_value={"auth_required": True}), \
                 patch.object(self.agent.engine.browser, "_get_or_create_driver", return_value=mock_driver), \
                 patch.object(self.agent.engine.browser, "driver", mock_driver):

                result = loop.run_until_complete(self.agent.execute_goal(goal))
                
                # Must NEVER claim success when blocked by authentication!
                self.assertEqual(result["status"], TASK_BLOCKED)
                self.assertIn("authentication", result["blocker_reason"].lower())
        finally:
            loop.close()

    # -----------------------------------------------------------------
    # TEST C: CONTROL PANEL NAVIGATION
    # -----------------------------------------------------------------
    def test_c_control_panel_navigation(self):
        """TEST C — Goal: 'Open Windows Control Panel and navigate to the Programs and Features page.'"""
        goal = "Open Windows Control Panel and navigate to the Programs and Features page."
        steps = self.agent.decompose_goal(goal)
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0].action_type, "DISCOVER_AND_LAUNCH")
        self.assertEqual(steps[1].action_type, "VERIFY_WINDOW")

        loop = asyncio.new_event_loop()
        try:
            with patch.object(self.agent.engine.os, "discover_and_open", return_value={"status": "SUCCESS", "mechanism": "system_applet_launch", "discovered_command": "control.exe appwiz.cpl"}), \
                 patch.object(self.agent.engine.desktop, "get_foreground_window", return_value={"hwnd": 12345, "title": "Programs and Features", "app": "explorer.exe"}):

                result = loop.run_until_complete(self.agent.execute_goal(goal))
                self.assertEqual(result["status"], TASK_COMPLETED)
                self.assertEqual(result["steps_completed"], 2)
                self.assertIn("programs and features", result["evidence"][1].lower())
        finally:
            loop.close()

    # -----------------------------------------------------------------
    # TEST D: UNFAMILIAR FILE TASK (ORGANIZING BY EXTENSION)
    # -----------------------------------------------------------------
    def test_d_unfamiliar_file_organization(self):
        """TEST D — Goal: 'Create a small Python program that organizes sample files by extension.'"""
        # Create real test directory with sample unorganized files
        sandbox_test = self.test_dir / "sandbox_test"
        sandbox_test.mkdir(parents=True, exist_ok=True)
        (sandbox_test / "notes.txt").write_text("sample note", encoding="utf-8")
        (sandbox_test / "photo.jpg").write_text("sample image", encoding="utf-8")
        (sandbox_test / "data.csv").write_text("a,b,c\n1,2,3", encoding="utf-8")

        # Execute OS general file organization capability directly
        os_exec = OSExecutor()
        res = os_exec.organize_files_by_extension(sandbox_test)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["total_files_organized"], 3)

        # Verify filesystem state
        self.assertTrue((sandbox_test / "txt" / "notes.txt").exists())
        self.assertTrue((sandbox_test / "jpg" / "photo.jpg").exists())
        self.assertTrue((sandbox_test / "csv" / "data.csv").exists())

    # -----------------------------------------------------------------
    # TEST E: ERROR RECOVERY & BOUNDED RETRIES
    # -----------------------------------------------------------------
    def test_e_error_recovery_and_bounded_retry(self):
        """TEST E — Detect failure, apply bounded retries, report blocker if recovery fails."""
        failed_step = TaskStep(
            id="step_fail",
            description="Attempt unavailable operation",
            capability="OS_CMD",
            action_type="DISCOVER_AND_LAUNCH",
            parameters={"target": "nonexistent_system_utility_999"},
            expected_outcome="Interface open"
        )
        task = TaskState(
            task_id="test_fail_task",
            goal="test recovery",
            status="EXECUTING",
            steps=[failed_step]
        )
        self.agent.save_checkpoint(task)

        loop = asyncio.new_event_loop()
        try:
            with patch.object(self.agent.engine.os, "discover_and_open", return_value={"status": "FAILED", "reason": "No executable found"}):
                result = loop.run_until_complete(self.agent.execute_goal("open nonexistent_system_utility_999"))
                # Bounded retries exhausted -> Reports clear failure
                self.assertEqual(result["status"], TASK_FAILED)
                self.assertIn("failed_step", result)
        finally:
            loop.close()

    # -----------------------------------------------------------------
    # TEST F: PERSISTENT MEMORY & TASK RESTORATION ACROSS RESTARTS
    # -----------------------------------------------------------------
    def test_f_task_recovery_across_restarts(self):
        """TEST F — Complete part of task, restart agent instance, resume from verified checkpoint."""
        step_1 = TaskStep(
            id="s1",
            description="Step 1 completed",
            capability="OS_CMD",
            action_type="DISCOVER_AND_LAUNCH",
            parameters={"target": "taskmgr"},
            expected_outcome="Task Manager open",
            status=STEP_COMPLETED,
            evidence="Task Manager launched"
        )
        step_2 = TaskStep(
            id="s2",
            description="Step 2 pending",
            capability="DESKTOP_UI",
            action_type="VERIFY_WINDOW",
            parameters={"expected_title": "Task Manager"},
            expected_outcome="Task Manager verified",
            status=STEP_PENDING
        )
        original_task = TaskState(
            task_id="task_recover_test",
            goal="Open and verify Task Manager",
            status="EXECUTING",
            steps=[step_1, step_2],
            current_step_index=1
        )
        self.agent.save_checkpoint(original_task)

        # Simulate agent restart by creating new agent instance
        new_agent_instance = UltronAutonomousAgent()
        restored_task = new_agent_instance.load_checkpoint()

        self.assertIsNotNone(restored_task)
        self.assertEqual(restored_task.task_id, "task_recover_test")
        self.assertEqual(restored_task.current_step_index, 1)
        self.assertEqual(restored_task.steps[0].status, STEP_COMPLETED)
        self.assertEqual(restored_task.steps[1].status, STEP_PENDING)

    # -----------------------------------------------------------------
    # TEST G: SAFETY POLICY & EMERGENCY STOP
    # -----------------------------------------------------------------
    def test_g_safety_policy_and_emergency_stop(self):
        """TEST G — Refuse high-risk actions without auth; immediately halt on emergency stop."""
        # 1. High risk action without authorization must be blocked
        permitted, msg = check_action_permitted("delete_file", {"path": "C:/Windows/important.dll"}, is_authorized=False)
        self.assertFalse(permitted)
        self.assertIn("AUTHORIZATION REQUIRED", msg)

        # 2. Low risk action must be permitted
        permitted_low, msg_low = check_action_permitted("search_web")
        self.assertTrue(permitted_low)

        # 3. Emergency stop must immediately halt and block all actions
        trigger_emergency_stop("Safety boundary test")
        self.assertTrue(is_emergency_stopped())

        permitted_after_stop, msg_stop = check_action_permitted("search_web")
        self.assertFalse(permitted_after_stop)
        self.assertIn("Emergency Stop is ACTIVE", msg_stop)

        # Reset emergency stop
        reset_emergency_stop()
        self.assertFalse(is_emergency_stopped())


if __name__ == "__main__":
    unittest.main()
