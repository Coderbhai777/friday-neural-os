"""
Unit & Integration Test Suite for JARVIS Persistent Scheduler & Reminder System
Created for Shivansh Sagar Pancholi
"""

import os
import sys
import time
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.scheduler_service import (
    JarvisScheduler,
    init_db,
    get_db_connection,
    parse_natural_time,
    compute_next_recurrence,
    format_friendly_time,
    get_utc_now
)
from tools.jarvis_reminder_daemon import (
    is_process_running,
    get_running_daemon_pid,
    write_pid_file,
    remove_pid_file,
    PID_FILE
)
from tools.jarvis_alarm_announcer import AlarmAnnouncer
import tools.productivity as prod


class TestJarvisScheduler(unittest.TestCase):

    def setUp(self):
        init_db()
        # Clean test table
        conn = get_db_connection()
        with conn:
            conn.execute("DELETE FROM scheduled_events WHERE id LIKE 'TEST-%' OR title LIKE 'Test %';")
        conn.close()

    def tearDown(self):
        conn = get_db_connection()
        with conn:
            conn.execute("DELETE FROM scheduled_events WHERE id LIKE 'TEST-%' OR title LIKE 'Test %';")
        conn.close()

    def test_01_create_and_query_timer(self):
        """Test timer creation, deadline calculation, and status query."""
        res = JarvisScheduler.create_timer(30, "Test Tea")
        self.assertIn("TMR-", res["id"])
        self.assertEqual(res["title"], "Test Tea")
        self.assertEqual(res["duration_seconds"], 30)

        # Check status
        status = JarvisScheduler.get_timer_status(res["id"])
        self.assertTrue(status["found"])
        self.assertGreaterEqual(status["remaining_seconds"], 28)
        self.assertLessEqual(status["remaining_seconds"], 31)

        # List active timers
        active = JarvisScheduler.list_active_timers()
        timer_ids = [t["id"] for t in active]
        self.assertIn(res["id"], timer_ids)

    def test_02_cancel_timer(self):
        """Test timer cancellation."""
        res = JarvisScheduler.create_timer(120, "Test Cooking")
        cancel_res = JarvisScheduler.cancel_timer(res["id"])
        self.assertTrue(cancel_res["cancelled"])

        # Check it is no longer active
        status = JarvisScheduler.get_timer_status(res["id"])
        self.assertFalse(status["found"])

    def test_03_create_one_time_reminder(self):
        """Test one-time reminder creation with relative and absolute expressions."""
        rem1 = JarvisScheduler.create_reminder("Test Meeting", "in 10 minutes")
        self.assertIn("REM-", rem1["id"])
        self.assertEqual(rem1["title"], "Test Meeting")
        self.assertIsNone(rem1["recurrence"])

        # Query pending reminders
        pending = JarvisScheduler.list_reminders(status_filter="pending")
        titles = [r["title"] for r in pending]
        self.assertIn("Test Meeting", titles)

    def test_04_recurring_reminder_computation(self):
        """Test recurring reminder logic (daily, weekdays, weekly)."""
        now_utc = get_utc_now()
        # Daily
        next_daily = compute_next_recurrence(now_utc, "daily")
        self.assertGreater(next_daily, now_utc)
        self.assertLessEqual((next_daily - now_utc).total_seconds(), 86400 * 2)

        # Weekdays
        next_wd = compute_next_recurrence(now_utc, "weekdays")
        self.assertGreater(next_wd, now_utc)

        # Create recurring event in DB
        rec_rem = JarvisScheduler.create_reminder("Test Daily Exercise", "every day at 7 AM")
        self.assertEqual(rec_rem["recurrence"], "daily")

    def test_05_snooze_reminder(self):
        """Test snoozing an active alarm."""
        rem = JarvisScheduler.create_reminder("Test Doctor", "in 1 minute")
        snooze_res = JarvisScheduler.snooze_reminder(rem["id"], minutes=10)
        self.assertTrue(snooze_res["snoozed"])
        self.assertEqual(snooze_res["snooze_count"], 1)

        # Check status in DB
        conn = get_db_connection()
        row = conn.execute("SELECT status, snooze_count FROM scheduled_events WHERE id = ?", (rem["id"],)).fetchone()
        conn.close()
        self.assertEqual(row["status"], "snoozed")
        self.assertEqual(row["snooze_count"], 1)

    def test_06_dismiss_alarm_one_time_and_recurring(self):
        """Test dismissing one-time vs recurring alarms."""
        # One-time
        rem1 = JarvisScheduler.create_reminder("Test Pill", "in 1 minute")
        dis1 = JarvisScheduler.dismiss_alarm(rem1["id"])
        self.assertTrue(dis1["dismissed"])
        self.assertFalse(dis1["recurring"])

        conn = get_db_connection()
        row1 = conn.execute("SELECT status FROM scheduled_events WHERE id = ?", (rem1["id"],)).fetchone()
        conn.close()
        self.assertEqual(row1["status"], "completed")

        # Recurring
        rem2 = JarvisScheduler.create_reminder("Test Standup", "every weekday at 9 AM")
        dis2 = JarvisScheduler.dismiss_alarm(rem2["id"])
        self.assertTrue(dis2["dismissed"])
        self.assertTrue(dis2["recurring"])

        conn = get_db_connection()
        row2 = conn.execute("SELECT status FROM scheduled_events WHERE id = ?", (rem2["id"],)).fetchone()
        conn.close()
        self.assertEqual(row2["status"], "pending")  # Reset to pending with next due date

    def test_07_overdue_recovery_policy(self):
        """Test that events expiring in the past (e.g. during sleep/reboot) are recovered and marked missed."""
        conn = get_db_connection()
        past_utc = (get_utc_now() - timedelta(hours=3)).isoformat()
        test_id = "TEST-OVERDUE"
        with conn:
            conn.execute("""
                INSERT INTO scheduled_events
                (id, event_type, title, created_at, due_at, timezone, status, snooze_count)
                VALUES (?, 'reminder', 'Test Missed Medication', ?, ?, 'UTC', 'pending', 0)
            """, (test_id, past_utc, past_utc))
        conn.close()

        # Process due events with threshold of 60 mins
        due = JarvisScheduler.process_due_events(max_missed_threshold_minutes=60)
        overdue_items = [d for d in due if d["id"] == test_id]
        self.assertEqual(len(overdue_items), 1)
        self.assertTrue(overdue_items[0]["missed"])

    def test_08_announcer_queue_non_blocking(self):
        """Test that the announcer queue accepts events without blocking."""
        announcer = AlarmAnnouncer()
        fake_event = {
            "id": "TEST-EVENT-01",
            "type": "timer",
            "title": "Test Instant Timer",
            "duration_seconds": 10,
            "missed": False
        }
        start = time.time()
        announcer.enqueue_alert(fake_event)
        elapsed = time.time() - start
        self.assertLess(elapsed, 0.1)  # Enqueue must be virtually instantaneous

    def test_09_daemon_pid_and_lockfile(self):
        """Test PID writing, validation, and cleanup."""
        write_pid_file()
        self.assertTrue(PID_FILE.exists())
        self.assertEqual(get_running_daemon_pid(), os.getpid())
        remove_pid_file()
        self.assertFalse(PID_FILE.exists())

    def test_10_productivity_backward_compatible_functions(self):
        """Test async functions in productivity.py."""
        import asyncio

        async def run_async_tests():
            t_msg = await prod.set_timer(duration_seconds=45, task="Test Focus Timer")
            self.assertIn("Test Focus Timer", t_msg)

            q_msg = await prod.get_timer("Test Focus Timer")
            self.assertIn("Test Focus Timer", q_msg)

            l_msg = await prod.list_active_timers()
            self.assertIn("Test Focus Timer", l_msg)

            c_msg = await prod.cancel_timer("Test Focus Timer")
            self.assertIn("cancelled", c_msg)

            r_msg = await prod.create_reminder("Test Workout", "in 30 minutes")
            self.assertIn("Test Workout", r_msg)

        asyncio.run(run_async_tests())


if __name__ == "__main__":
    unittest.main()
