"""
JARVIS Persistent Scheduler Service & Database Engine
Created for Shivansh Sagar Pancholi

Features:
- Deterministic SQLite database persistence with WAL mode & atomic transactions.
- UTC canonical timestamps with local timezone presentation and daylight saving support.
- Accurate deadline-based countdown timers (not tick decrementing).
- One-time, relative, specific-time, and recurring reminders (daily, weekdays, weekly, custom days).
- Recovery of missed/overdue reminders after system reboot or sleep.
- Snooze, dismiss, cancellation, and remaining time calculation.
- Background process safety with inter-process database locking.
- Automatic migration from legacy reminders.json if present.
"""

import os
import sys
import json
import uuid
import sqlite3
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import dateutil.parser
from dateutil import tz


# ==============================================================================
# CONFIGURATION & PATH RESOLUTION
# ==============================================================================

def get_data_dir() -> Path:
    """Returns the persistent JARVIS Data directory."""
    path = Path.home() / "Documents" / "JARVIS_Data"
    path.mkdir(parents=True, exist_ok=True)
    return path


DB_PATH = get_data_dir() / "jarvis_reminders.db"
_DB_LOCK = threading.RLock()


def get_db_connection(timeout: float = 10.0) -> sqlite3.Connection:
    """Creates a configured SQLite connection with WAL mode and row factory."""
    conn = sqlite3.connect(str(DB_PATH), timeout=timeout)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn


def init_db():
    """Initializes the database schema if not already present."""
    with _DB_LOCK:
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS scheduled_events (
                        id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,          -- 'timer', 'reminder', 'alarm'
                        title TEXT NOT NULL,
                        duration_seconds INTEGER,          -- original duration for timers
                        created_at TEXT NOT NULL,          -- ISO 8601 UTC
                        due_at TEXT NOT NULL,              -- ISO 8601 UTC
                        timezone TEXT NOT NULL,            -- e.g. 'Asia/Kolkata', 'UTC'
                        status TEXT NOT NULL,              -- 'pending', 'ringing', 'completed', 'cancelled', 'snoozed', 'dismissed'
                        recurrence TEXT,                   -- NULL, 'daily', 'weekdays', 'weekly', etc.
                        snooze_count INTEGER DEFAULT 0,
                        snooze_until TEXT,                 -- ISO 8601 UTC
                        last_notified_at TEXT,             -- ISO 8601 UTC
                        missed INTEGER DEFAULT 0,          -- 1 if deadline passed while system was offline
                        metadata TEXT                      -- Optional JSON string
                    );
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_status_due
                    ON scheduled_events(status, due_at);
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_type_status
                    ON scheduled_events(event_type, status);
                """)
        finally:
            conn.close()

    # Perform legacy migration from reminders.json if found
    _migrate_legacy_reminders()


def _migrate_legacy_reminders():
    """Migrates existing items from reminders.json into the SQLite database exactly once."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, migrated_at TEXT);")
            migrated = conn.execute("SELECT name FROM schema_migrations WHERE name = 'legacy_reminders'").fetchone()
            if migrated:
                return

        search_paths = [
            Path.cwd() / "reminders.json",
            Path.home() / "Desktop" / "JARVIS_Portable" / "JARVIS_Portable" / "reminders.json",
            Path.home() / "Desktop" / "JARVIS-AI-Assistant" / "reminders.json",
        ]
        for p in search_paths:
            if not p.exists():
                continue
            try:
                with open(p, "r", encoding="utf-8") as f:
                    legacy_items = json.load(f)
                if not isinstance(legacy_items, list):
                    continue

                with conn:
                    for item in legacy_items:
                        if not isinstance(item, dict):
                            continue
                        task = item.get("task", "Reminder")
                        itype = item.get("type", "reminder")
                        notified = item.get("notified", False)
                        if notified:
                            continue  # Skip already notified items

                        # Check if already in DB
                        cur = conn.execute(
                            "SELECT id FROM scheduled_events WHERE title = ?",
                            (task,)
                        )
                        if cur.fetchone():
                            continue

                        now_utc = datetime.now(timezone.utc)
                        expiry_ts = item.get("expiry")
                        time_str = item.get("time")
                        date_str = item.get("date", now_utc.strftime("%Y-%m-%d"))

                        if expiry_ts:
                            due_utc = datetime.fromtimestamp(expiry_ts, tz=timezone.utc)
                            duration = int(max(0, expiry_ts - now_utc.timestamp()))
                        elif time_str:
                            try:
                                combined = f"{date_str} {time_str}"
                                local_tz = tz.gettz()
                                local_dt = datetime.strptime(combined, "%Y-%m-%d %H:%M").replace(tzinfo=local_tz)
                                due_utc = local_dt.astimezone(timezone.utc)
                            except Exception:
                                due_utc = now_utc + timedelta(minutes=5)
                            duration = None
                        else:
                            due_utc = now_utc + timedelta(minutes=5)
                            duration = None

                        event_id = str(uuid.uuid4())[:8]
                        conn.execute("""
                            INSERT INTO scheduled_events
                            (id, event_type, title, duration_seconds, created_at, due_at, timezone, status, recurrence, snooze_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', NULL, 0)
                        """, (
                            event_id,
                            itype,
                            task,
                            duration,
                            now_utc.isoformat(),
                            due_utc.isoformat(),
                            str(tz.gettz() or "UTC"),
                        ))

                    # Record migration complete
                    conn.execute(
                        "INSERT OR REPLACE INTO schema_migrations (name, migrated_at) VALUES ('legacy_reminders', ?)",
                        (datetime.now(timezone.utc).isoformat(),)
                    )
            except Exception:
                pass
    finally:
        conn.close()


# ==============================================================================
# TIME PARSING & RECURRENCE UTILITIES
# ==============================================================================

def get_local_now() -> datetime:
    """Returns the current aware datetime in the system's local timezone."""
    return datetime.now(tz.gettz())


def get_utc_now() -> datetime:
    """Returns the current aware datetime in UTC."""
    return datetime.now(timezone.utc)


def parse_natural_time(expression: str) -> Tuple[datetime, Optional[str]]:
    """
    Parses a natural language time expression into an aware UTC datetime and recurrence rule.
    Handles:
    - Relative: 'in 5 minutes', 'in 30 seconds', 'in 2 hours', 'in 1 hour 15 minutes'
    - Time-of-day: '9 PM', '21:00', '8:30 AM', 'at 15:45'
    - Specific day: 'tomorrow at 8 AM', 'on Friday at 5 PM'
    - Recurring: 'every day at 7 AM', 'every weekday at 8 AM', 'every Monday at 10 AM'
    """
    expr = expression.strip().lower()
    local_tz = tz.gettz()
    now_local = datetime.now(local_tz)
    recurrence = None

    # Detect recurrence patterns
    if "every weekday" in expr or "weekdays" in expr:
        recurrence = "weekdays"
        expr = expr.replace("every weekday", "").replace("weekdays", "").strip()
    elif "every day" in expr or "daily" in expr:
        recurrence = "daily"
        expr = expr.replace("every day", "").replace("daily", "").strip()
    elif "every week" in expr or "weekly" in expr:
        recurrence = "weekly"
        expr = expr.replace("every week", "").replace("weekly", "").strip()
    else:
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            if f"every {day}" in expr:
                recurrence = f"every {day}"
                expr = expr.replace(f"every {day}", "").strip()
                break

    # Clean prefixes
    for prefix in ["at ", "for ", "on ", "in "]:
        if expr.startswith(prefix):
            # Keep 'in ' for relative check
            if prefix != "in ":
                expr = expr[len(prefix):].strip()

    # Relative time: e.g. "in 10 minutes", "in 45 seconds", "20 mins", "1 hour"
    import re
    rel_match = re.search(r'(?:in\s+)?(?:(\d+)\s*(?:hour|hr|h))?\s*(?:(\d+)\s*(?:min|m))?\s*(?:(\d+)\s*(?:sec|s))?', expr)
    hours = int(rel_match.group(1)) if (rel_match and rel_match.group(1)) else 0
    minutes = int(rel_match.group(2)) if (rel_match and rel_match.group(2)) else 0
    seconds = int(rel_match.group(3)) if (rel_match and rel_match.group(3)) else 0

    if (hours or minutes or seconds) and ("min" in expr or "sec" in expr or "hour" in expr or "hr" in expr):
        total_seconds = hours * 3600 + minutes * 60 + seconds
        target_local = now_local + timedelta(seconds=total_seconds)
        return target_local.astimezone(timezone.utc), recurrence

    # Tomorrow check
    is_tomorrow = "tomorrow" in expr
    if is_tomorrow:
        expr = expr.replace("tomorrow", "").strip()
        expr = expr.replace("at ", "").strip()

    # Parse absolute time string (e.g. "9 PM", "21:00", "08:30 am", "5:00")
    try:
        # If user provided a short hour like "9" or "9pm"
        parsed = dateutil.parser.parse(expr, default=now_local)
        target_local = parsed.replace(tzinfo=local_tz)

        if is_tomorrow:
            target_local = target_local + timedelta(days=1)
        elif target_local <= now_local and not recurrence:
            # If the time is earlier today and not explicitly yesterday/tomorrow, assume tomorrow
            target_local = target_local + timedelta(days=1)

        return target_local.astimezone(timezone.utc), recurrence
    except Exception:
        # Fallback: 5 minutes from now
        fallback = now_local + timedelta(minutes=5)
        return fallback.astimezone(timezone.utc), recurrence


def compute_next_recurrence(current_due_utc: datetime, recurrence: str) -> datetime:
    """Computes the next occurrence for a recurring event in UTC."""
    local_tz = tz.gettz()
    current_local = current_due_utc.astimezone(local_tz)
    now_local = datetime.now(local_tz)

    next_local = current_local
    if recurrence == "daily":
        while next_local <= now_local:
            next_local += timedelta(days=1)
    elif recurrence == "weekdays":
        while next_local <= now_local:
            next_local += timedelta(days=1)
            # 5 is Saturday, 6 is Sunday
            while next_local.weekday() >= 5:
                next_local += timedelta(days=1)
    elif recurrence == "weekly":
        while next_local <= now_local:
            next_local += timedelta(days=7)
    elif recurrence and recurrence.startswith("every "):
        day_name = recurrence.replace("every ", "").strip().lower()
        days_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        target_day = days_map.get(day_name)
        if target_day is not None:
            while next_local <= now_local or next_local.weekday() != target_day:
                next_local += timedelta(days=1)
    else:
        # Default 24 hours
        while next_local <= now_local:
            next_local += timedelta(days=1)

    return next_local.astimezone(timezone.utc)


def format_friendly_time(utc_iso: str) -> str:
    """Converts a UTC ISO string to a friendly readable local format."""
    try:
        dt_utc = dateutil.parser.isoparse(utc_iso)
        dt_local = dt_utc.astimezone(tz.gettz())
        now_local = datetime.now(tz.gettz())

        if dt_local.date() == now_local.date():
            return dt_local.strftime("Today at %I:%M %p")
        elif dt_local.date() == (now_local + timedelta(days=1)).date():
            return dt_local.strftime("Tomorrow at %I:%M %p")
        else:
            return dt_local.strftime("%b %d at %I:%M %p")
    except Exception:
        return utc_iso


# ==============================================================================
# SCHEDULER SERVICE API
# ==============================================================================

class JarvisScheduler:
    """Thread-safe and process-safe scheduling engine for JARVIS."""

    @staticmethod
    def create_timer(duration_seconds: int, title: str = "Timer") -> Dict[str, Any]:
        """Creates a persistent countdown timer."""
        init_db()
        now_utc = get_utc_now()
        due_utc = now_utc + timedelta(seconds=max(1, duration_seconds))
        event_id = f"TMR-{uuid.uuid4().hex[:6].upper()}"

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO scheduled_events
                        (id, event_type, title, duration_seconds, created_at, due_at, timezone, status, recurrence, snooze_count)
                        VALUES (?, 'timer', ?, ?, ?, ?, ?, 'pending', NULL, 0)
                    """, (
                        event_id,
                        title,
                        duration_seconds,
                        now_utc.isoformat(),
                        due_utc.isoformat(),
                        str(tz.gettz() or "UTC"),
                    ))
            finally:
                conn.close()

        # Format human-friendly duration
        mins, secs = divmod(duration_seconds, 60)
        hrs, mins = divmod(mins, 60)
        dur_str = []
        if hrs: dur_str.append(f"{hrs} hour{'s' if hrs > 1 else ''}")
        if mins: dur_str.append(f"{mins} minute{'s' if mins > 1 else ''}")
        if secs: dur_str.append(f"{secs} second{'s' if secs > 1 else ''}")
        dur_text = " and ".join(dur_str) if dur_str else f"{duration_seconds} seconds"

        return {
            "id": event_id,
            "type": "timer",
            "title": title,
            "duration_seconds": duration_seconds,
            "duration_text": dur_text,
            "due_at": due_utc.isoformat(),
            "friendly_time": format_friendly_time(due_utc.isoformat()),
            "status": "pending",
            "message": f"Sir, your {title} timer is set for {dur_text}."
        }

    @staticmethod
    def create_reminder(
        title: str,
        due_expression: str,
        recurrence: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a one-time or recurring reminder from natural language."""
        init_db()
        due_utc, parsed_rec = parse_natural_time(due_expression)
        effective_rec = recurrence or parsed_rec
        now_utc = get_utc_now()
        event_id = f"REM-{uuid.uuid4().hex[:6].upper()}"

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO scheduled_events
                        (id, event_type, title, duration_seconds, created_at, due_at, timezone, status, recurrence, snooze_count)
                        VALUES (?, 'reminder', ?, NULL, ?, ?, ?, 'pending', ?, 0)
                    """, (
                        event_id,
                        title,
                        now_utc.isoformat(),
                        due_utc.isoformat(),
                        str(tz.gettz() or "UTC"),
                        effective_rec,
                    ))
            finally:
                conn.close()

        friendly = format_friendly_time(due_utc.isoformat())
        rec_text = f" ({effective_rec})" if effective_rec else ""
        return {
            "id": event_id,
            "type": "reminder",
            "title": title,
            "due_at": due_utc.isoformat(),
            "friendly_time": friendly,
            "recurrence": effective_rec,
            "status": "pending",
            "message": f"Reminder set for '{title}' for {friendly}{rec_text}, Sir."
        }

    @staticmethod
    def get_timer_status(identifier: str) -> Dict[str, Any]:
        """Returns the status and remaining time for a timer by ID or matching label."""
        init_db()
        now_utc = get_utc_now()

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                row = conn.execute("""
                    SELECT * FROM scheduled_events
                    WHERE event_type = 'timer'
                      AND (id = ? OR LOWER(title) LIKE ?)
                      AND status IN ('pending', 'snoozed')
                    ORDER BY due_at ASC LIMIT 1
                """, (identifier, f"%{identifier.lower()}%")).fetchone()

                if not row:
                    return {
                        "found": False,
                        "message": f"No active timer found matching '{identifier}', Sir."
                    }

                due_dt = dateutil.parser.isoparse(row["due_at"])
                remaining = int((due_dt - now_utc).total_seconds())

                if remaining <= 0:
                    rem_text = "due right now"
                else:
                    mins, secs = divmod(remaining, 60)
                    hrs, mins = divmod(mins, 60)
                    parts = []
                    if hrs: parts.append(f"{hrs} hour{'s' if hrs > 1 else ''}")
                    if mins: parts.append(f"{mins} minute{'s' if mins > 1 else ''}")
                    if secs: parts.append(f"{secs} second{'s' if secs > 1 else ''}")
                    rem_text = " and ".join(parts) if parts else f"{remaining} seconds"

                return {
                    "found": True,
                    "id": row["id"],
                    "title": row["title"],
                    "remaining_seconds": max(0, remaining),
                    "remaining_text": rem_text,
                    "duration_seconds": row["duration_seconds"],
                    "status": row["status"],
                    "message": f"Sir, there is {rem_text} left on your '{row['title']}' timer."
                }
            finally:
                conn.close()

    @staticmethod
    def list_active_timers() -> List[Dict[str, Any]]:
        """Lists all currently active countdown timers."""
        init_db()
        now_utc = get_utc_now()
        results = []

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                rows = conn.execute("""
                    SELECT * FROM scheduled_events
                    WHERE event_type = 'timer' AND status IN ('pending', 'snoozed')
                    ORDER BY due_at ASC
                """).fetchall()

                for r in rows:
                    due_dt = dateutil.parser.isoparse(r["due_at"])
                    rem = int((due_dt - now_utc).total_seconds())
                    results.append({
                        "id": r["id"],
                        "title": r["title"],
                        "duration_seconds": r["duration_seconds"],
                        "remaining_seconds": max(0, rem),
                        "due_at": r["due_at"],
                        "friendly_time": format_friendly_time(r["due_at"]),
                        "status": r["status"]
                    })
            finally:
                conn.close()

        return results

    @staticmethod
    def cancel_timer(identifier: str) -> Dict[str, Any]:
        """Cancels an active timer by ID or title."""
        init_db()
        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    # Search target
                    row = conn.execute("""
                        SELECT id, title FROM scheduled_events
                        WHERE event_type = 'timer'
                          AND (id = ? OR LOWER(title) LIKE ?)
                          AND status IN ('pending', 'snoozed', 'ringing')
                        LIMIT 1
                    """, (identifier, f"%{identifier.lower()}%")).fetchone()

                    if not row:
                        return {
                            "cancelled": False,
                            "message": f"Could not find an active timer matching '{identifier}', Sir."
                        }

                    conn.execute(
                        "UPDATE scheduled_events SET status = 'cancelled' WHERE id = ?",
                        (row["id"],)
                    )
                    return {
                        "cancelled": True,
                        "id": row["id"],
                        "title": row["title"],
                        "message": f"Sir, your {row['title']} timer has been cancelled."
                    }
            finally:
                conn.close()

    @staticmethod
    def list_reminders(status_filter: str = "pending", limit: int = 50) -> List[Dict[str, Any]]:
        """Lists scheduled reminders filtered by status."""
        init_db()
        results = []
        with _DB_LOCK:
            conn = get_db_connection()
            try:
                query = "SELECT * FROM scheduled_events WHERE event_type != 'timer'"
                params = []

                if status_filter != "all":
                    query += " AND status = ?"
                    params.append(status_filter)

                query += " ORDER BY due_at ASC LIMIT ?"
                params.append(limit)

                rows = conn.execute(query, params).fetchall()
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "type": r["event_type"],
                        "title": r["title"],
                        "due_at": r["due_at"],
                        "friendly_time": format_friendly_time(r["due_at"]),
                        "recurrence": r["recurrence"],
                        "status": r["status"],
                        "snooze_count": r["snooze_count"],
                        "missed": bool(r["missed"])
                    })
            finally:
                conn.close()

        return results

    @staticmethod
    def snooze_reminder(identifier: str, minutes: int = 5) -> Dict[str, Any]:
        """Snoozes an active or ringing event for a given number of minutes."""
        init_db()
        now_utc = get_utc_now()
        new_due = now_utc + timedelta(minutes=max(1, minutes))

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    # Find candidate
                    row = conn.execute("""
                        SELECT * FROM scheduled_events
                        WHERE (id = ? OR LOWER(title) LIKE ?)
                          AND status IN ('ringing', 'pending', 'snoozed')
                        ORDER BY due_at ASC LIMIT 1
                    """, (identifier, f"%{identifier.lower()}%")).fetchone()

                    if not row:
                        # Try getting the most recently due/ringing item
                        row = conn.execute("""
                            SELECT * FROM scheduled_events
                            WHERE status = 'ringing'
                            ORDER BY due_at DESC LIMIT 1
                        """).fetchone()

                    if not row:
                        return {
                            "snoozed": False,
                            "message": f"No active alarm found to snooze for '{identifier}', Sir."
                        }

                    snooze_count = (row["snooze_count"] or 0) + 1
                    conn.execute("""
                        UPDATE scheduled_events
                        SET status = 'snoozed',
                            snooze_until = ?,
                            due_at = ?,
                            snooze_count = ?
                        WHERE id = ?
                    """, (new_due.isoformat(), new_due.isoformat(), snooze_count, row["id"]))

                    return {
                        "snoozed": True,
                        "id": row["id"],
                        "title": row["title"],
                        "minutes": minutes,
                        "snooze_count": snooze_count,
                        "new_due_at": new_due.isoformat(),
                        "message": f"Sir, I have snoozed '{row['title']}' for {minutes} minutes."
                    }
            finally:
                conn.close()

    @staticmethod
    def dismiss_alarm(identifier: Optional[str] = None) -> Dict[str, Any]:
        """Dismisses a ringing or currently pending alarm."""
        init_db()
        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    if identifier:
                        row = conn.execute("""
                            SELECT * FROM scheduled_events
                            WHERE (id = ? OR LOWER(title) LIKE ?)
                              AND status IN ('ringing', 'pending', 'snoozed')
                            LIMIT 1
                        """, (identifier, f"%{identifier.lower()}%")).fetchone()
                    else:
                        row = conn.execute("""
                            SELECT * FROM scheduled_events
                            WHERE status = 'ringing'
                            ORDER BY due_at DESC LIMIT 1
                        """).fetchone()

                    if not row:
                        return {
                            "dismissed": False,
                            "message": "No active alarm is currently sounding to dismiss, Sir."
                        }

                    # If recurring, advance to next recurrence
                    if row["recurrence"]:
                        due_dt = dateutil.parser.isoparse(row["due_at"])
                        next_due = compute_next_recurrence(due_dt, row["recurrence"])
                        conn.execute("""
                            UPDATE scheduled_events
                            SET status = 'pending',
                                due_at = ?,
                                snooze_count = 0,
                                last_notified_at = ?
                            WHERE id = ?
                        """, (next_due.isoformat(), get_utc_now().isoformat(), row["id"]))
                        return {
                            "dismissed": True,
                            "id": row["id"],
                            "title": row["title"],
                            "recurring": True,
                            "next_due": format_friendly_time(next_due.isoformat()),
                            "message": f"Alarm for '{row['title']}' dismissed. Next reminder: {format_friendly_time(next_due.isoformat())}, Sir."
                        }
                    else:
                        conn.execute("""
                            UPDATE scheduled_events
                            SET status = 'completed',
                                last_notified_at = ?
                            WHERE id = ?
                        """, (get_utc_now().isoformat(), row["id"]))
                        return {
                            "dismissed": True,
                            "id": row["id"],
                            "title": row["title"],
                            "recurring": False,
                            "message": f"Alarm for '{row['title']}' dismissed, Sir."
                        }
            finally:
                conn.close()

    @staticmethod
    def cancel_reminder(identifier: str) -> Dict[str, Any]:
        """Cancels a reminder by ID or title."""
        init_db()
        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    row = conn.execute("""
                        SELECT id, title FROM scheduled_events
                        WHERE (id = ? OR LOWER(title) LIKE ?)
                          AND status IN ('pending', 'snoozed', 'ringing')
                        LIMIT 1
                    """, (identifier, f"%{identifier.lower()}%")).fetchone()

                    if not row:
                        return {
                            "cancelled": False,
                            "message": f"Could not find an active reminder matching '{identifier}', Sir."
                        }

                    conn.execute("UPDATE scheduled_events SET status = 'cancelled' WHERE id = ?", (row["id"],))
                    return {
                        "cancelled": True,
                        "id": row["id"],
                        "title": row["title"],
                        "message": f"Sir, your reminder for '{row['title']}' has been cancelled."
                    }
            finally:
                conn.close()

    @staticmethod
    def reschedule_reminder(identifier: str, new_due_str: str) -> Dict[str, Any]:
        """Reschedules a reminder to a new time."""
        init_db()
        new_utc, rec = parse_natural_time(new_due_str)

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    row = conn.execute("""
                        SELECT id, title, recurrence FROM scheduled_events
                        WHERE (id = ? OR LOWER(title) LIKE ?)
                          AND status IN ('pending', 'snoozed', 'ringing')
                        LIMIT 1
                    """, (identifier, f"%{identifier.lower()}%")).fetchone()

                    if not row:
                        return {
                            "rescheduled": False,
                            "message": f"Could not find an active reminder matching '{identifier}' to reschedule, Sir."
                        }

                    effective_rec = rec if rec else row["recurrence"]
                    conn.execute("""
                        UPDATE scheduled_events
                        SET due_at = ?,
                            recurrence = ?,
                            status = 'pending',
                            snooze_count = 0
                        WHERE id = ?
                    """, (new_utc.isoformat(), effective_rec, row["id"]))

                    friendly = format_friendly_time(new_utc.isoformat())
                    return {
                        "rescheduled": True,
                        "id": row["id"],
                        "title": row["title"],
                        "new_due_at": new_utc.isoformat(),
                        "friendly_time": friendly,
                        "message": f"Sir, '{row['title']}' has been rescheduled to {friendly}."
                    }
            finally:
                conn.close()

    @staticmethod
    def process_due_events(max_missed_threshold_minutes: int = 120) -> List[Dict[str, Any]]:
        """
        Scans for due events, marks them ringing/processing, and prepares alerts.
        Differentiates between newly due events and overdue/missed events (from system sleep/reboot).
        """
        init_db()
        now_utc = get_utc_now()
        due_events = []

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    # Select pending or snoozed events whose deadline is <= now
                    cur = conn.execute("""
                        SELECT * FROM scheduled_events
                        WHERE status IN ('pending', 'snoozed')
                          AND due_at <= ?
                        ORDER BY due_at ASC
                    """, (now_utc.isoformat(),))
                    rows = cur.fetchall()

                    for r in rows:
                        event_id = r["id"]
                        due_dt = dateutil.parser.isoparse(r["due_at"])
                        delay_seconds = (now_utc - due_dt).total_seconds()
                        is_missed = delay_seconds > (max_missed_threshold_minutes * 60)

                        # Update status to 'ringing'
                        conn.execute("""
                            UPDATE scheduled_events
                            SET status = 'ringing',
                                last_notified_at = ?,
                                missed = ?
                            WHERE id = ?
                        """, (now_utc.isoformat(), 1 if is_missed else 0, event_id))

                        due_events.append({
                            "id": r["id"],
                            "type": r["event_type"],
                            "title": r["title"],
                            "duration_seconds": r["duration_seconds"],
                            "due_at": r["due_at"],
                            "recurrence": r["recurrence"],
                            "snooze_count": r["snooze_count"],
                            "missed": is_missed,
                            "delay_seconds": delay_seconds
                        })
            finally:
                conn.close()

        return due_events

    @staticmethod
    def mark_event_completed_or_recur(event_id: str):
        """Marks a ringing event completed, or schedules next recurrence."""
        init_db()
        now_utc = get_utc_now()

        with _DB_LOCK:
            conn = get_db_connection()
            try:
                with conn:
                    row = conn.execute("SELECT * FROM scheduled_events WHERE id = ?", (event_id,)).fetchone()
                    if not row:
                        return

                    if row["recurrence"]:
                        due_dt = dateutil.parser.isoparse(row["due_at"])
                        next_due = compute_next_recurrence(due_dt, row["recurrence"])
                        conn.execute("""
                            UPDATE scheduled_events
                            SET status = 'pending',
                                due_at = ?,
                                snooze_count = 0,
                                last_notified_at = ?
                            WHERE id = ?
                        """, (next_due.isoformat(), now_utc.isoformat(), event_id))
                    else:
                        conn.execute("""
                            UPDATE scheduled_events
                            SET status = 'completed',
                                last_notified_at = ?
                            WHERE id = ?
                        """, (now_utc.isoformat(), event_id))
            finally:
                conn.close()
