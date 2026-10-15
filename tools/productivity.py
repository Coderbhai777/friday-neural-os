import os
import shutil
import subprocess
import winsound
import json
import time as time_lib
from datetime import datetime, timedelta

# Import the persistent scheduler engine and background daemon
try:
    from tools.scheduler_service import JarvisScheduler, format_friendly_time
    from tools.jarvis_reminder_daemon import start_daemon_detached, get_running_daemon_pid
except ImportError:
    try:
        from friday_tools.scheduler_service import JarvisScheduler, format_friendly_time
        from friday_tools.jarvis_reminder_daemon import start_daemon_detached, get_running_daemon_pid
    except ImportError:
        JarvisScheduler = None
        start_daemon_detached = lambda: True
        get_running_daemon_pid = lambda: None


# ==============================
# PRODUCTIVITY (FOCUS MODE)
# ==============================

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
BACKUP_PATH = r"C:\Windows\System32\drivers\etc\hosts.bak"

async def enable_focus_mode(websites: list[str]) -> str:
    """
    Blocks the specified websites by modifying the hosts file.
    Requires Administrator privileges.
    """
    try:
        # Backup hosts file if not exists
        if not os.path.exists(BACKUP_PATH):
            shutil.copy(HOSTS_PATH, BACKUP_PATH)

        with open(HOSTS_PATH, "r") as f:
            content = f.read()

        new_entries = "\n# FOCUS MODE START\n"
        for site in websites:
            # Clean domain
            domain = site.replace("https://", "").replace("http://", "").replace("www.", "").strip()
            if domain not in content:
                new_entries += f"127.0.0.1 {domain}\n"
                new_entries += f"127.0.0.1 www.{domain}\n"
        new_entries += "# FOCUS MODE END\n"

        with open(HOSTS_PATH, "a") as f:
            f.write(new_entries)

        # Flush DNS
        subprocess.run("ipconfig /flushdns", shell=True)
        return f"✅ Focus Mode ENABLED. Blocked: {', '.join(websites)}"

    except PermissionError:
        return "❌ Permission Denied: Run ULTRON as Administrator."
    except Exception as e:
        return f"❌ Failed to enable Focus Mode: {e}"

async def disable_focus_mode() -> str:
    """
    Restores the original hosts file to unblock websites.
    """
    try:
        if os.path.exists(BACKUP_PATH):
            shutil.copy(BACKUP_PATH, HOSTS_PATH)
            subprocess.run("ipconfig /flushdns", shell=True)
            return "✅ Focus Mode DISABLED. Websites unblocked."
        else:
            return "❌ No backup found. Cannot restore hosts file."
    except PermissionError:
        return "❌ Permission Denied: Run ULTRON as Administrator."
    except Exception as e:
        return f"❌ Failed to disable Focus Mode: {e}"


# ==============================
# JARVIS PERSISTENT TIMERS & REMINDERS
# ==============================

def _auto_start_daemon():
    """Silently ensures the background reminder daemon is running."""
    try:
        start_daemon_detached()
    except Exception:
        pass


async def set_timer(duration_seconds: int = None, task: str = "Timer", **kwargs) -> str:
    """
    Sets a persistent countdown timer for a number of seconds with an optional label.
    Persists to SQLite database and operates even when the main Jarvis window is closed.
    """
    _auto_start_daemon()
    secs = duration_seconds if duration_seconds is not None else (kwargs.get("seconds") or kwargs.get("duration") or 60)
    lbl = task if task != "Timer" else (kwargs.get("label") or kwargs.get("task") or "Timer")

    if JarvisScheduler:
        try:
            res = JarvisScheduler.create_timer(int(secs), str(lbl))
            return res.get("message", f"Timer set for {secs} seconds for: {lbl}")
        except Exception as e:
            print(f"[Timer Service Error]: {e}")

    return f"Timer set for {secs} seconds for: {lbl}"


async def get_timer(task_or_id: str = "Timer", **kwargs) -> str:
    """
    Retrieves the remaining time and status of an active countdown timer.
    """
    target = task_or_id if task_or_id != "Timer" else (kwargs.get("label") or kwargs.get("id") or "Timer")
    if JarvisScheduler:
        res = JarvisScheduler.get_timer_status(str(target))
        return res.get("message", f"Timer status checked for {target}.")
    return "Timer service unavailable."


async def list_active_timers(**kwargs) -> str:
    """
    Lists all active countdown timers with their remaining time.
    """
    if JarvisScheduler:
        timers = JarvisScheduler.list_active_timers()
        if not timers:
            return "Sir, there are currently no active timers running."
        lines = ["Active Timers:"]
        for t in timers:
            lines.append(f"• {t['title']} (ID: {t['id']}): {t['remaining_seconds']}s remaining [Due: {t['friendly_time']}]")
        return "\n".join(lines)
    return "No active timers found."


async def cancel_timer(task_or_id: str = "Timer", **kwargs) -> str:
    """
    Cancels an active timer by label or ID.
    """
    target = task_or_id if task_or_id != "Timer" else (kwargs.get("label") or kwargs.get("id") or "Timer")
    if JarvisScheduler:
        res = JarvisScheduler.cancel_timer(str(target))
        return res.get("message", f"Timer '{target}' cancelled.")
    return f"Timer '{target}' cancellation requested."


async def add_smart_reminder(task: str = "Reminder", time_at: str = "in 15 minutes", **kwargs) -> str:
    """
    Sets a reminder for a specific time (HH:MM or natural language).
    Operates persistently even when main window is closed.
    """
    _auto_start_daemon()
    t = task or kwargs.get("title") or "Reminder"
    tm = time_at or kwargs.get("time") or "in 15 minutes"
    if JarvisScheduler:
        try:
            res = JarvisScheduler.create_reminder(str(t), str(tm))
            return res.get("message", f"Reminder set for '{t}' at {tm}, Sir.")
        except Exception as e:
            print(f"[Reminder Service Error]: {e}")
    return f"Reminder set for {t} at {tm}"


async def set_alarm(time_at: str = "08:00", task: str = "Alarm", **kwargs) -> str:
    """
    Sets an alarm for a specific time (HH:MM or natural language).
    """
    _auto_start_daemon()
    tm = time_at or kwargs.get("time") or "08:00"
    t = task if task != "Alarm" else (kwargs.get("label") or "Alarm")
    if JarvisScheduler:
        try:
            res = JarvisScheduler.create_reminder(str(t), str(tm))
            return res.get("message", f"Alarm set for {tm} for: {t}")
        except Exception as e:
            print(f"[Alarm Service Error]: {e}")
    return f"Alarm set for {tm} for: {t}"


async def create_reminder(title: str = None, due_at: str = None, recurrence: str = None, **kwargs) -> str:
    """
    Creates a one-time or recurring reminder (e.g. daily, weekdays, weekly).
    """
    _auto_start_daemon()
    t = title or kwargs.get("reminder_text") or kwargs.get("task") or "Reminder"
    d = due_at or kwargs.get("time_str") or kwargs.get("time_at") or kwargs.get("time") or "in 15 minutes"
    rec = recurrence or kwargs.get("repeat")
    if JarvisScheduler:
        res = JarvisScheduler.create_reminder(str(t), str(d), recurrence=rec)
        return res.get("message", f"Reminder created for '{t}'.")
    return f"Reminder created for '{t}' at {d}."


async def list_reminders(status: str = "pending") -> str:
    """
    Lists scheduled reminders (pending, snoozed, completed, or all).
    """
    if JarvisScheduler:
        reminders = JarvisScheduler.list_reminders(status_filter=status)
        if not reminders:
            return f"Sir, there are no {status} reminders on your schedule."
        lines = [f"Scheduled Reminders ({status}):"]
        for r in reminders:
            rec_tag = f" [Repeats: {r['recurrence']}]" if r.get("recurrence") else ""
            lines.append(f"• '{r['title']}' (ID: {r['id']}) - {r['friendly_time']}{rec_tag}")
        return "\n".join(lines)
    return "No reminders found."


async def snooze_reminder(reminder_id_or_title: str = "", minutes: int = 5) -> str:
    """
    Snoozes an active or ringing reminder/alarm for a number of minutes (default 5).
    """
    if JarvisScheduler:
        res = JarvisScheduler.snooze_reminder(reminder_id_or_title, minutes=minutes)
        return res.get("message", f"Snoozed for {minutes} minutes.")
    return f"Snoozed for {minutes} minutes."


async def dismiss_alarm(event_id: str = "") -> str:
    """
    Dismisses the currently sounding alarm or timer.
    """
    # Silence ongoing audio immediately
    try:
        from tools.jarvis_alarm_announcer import stop_active_alarm
        stop_active_alarm()
    except Exception:
        try:
            from friday_tools.jarvis_alarm_announcer import stop_active_alarm
            stop_active_alarm()
        except Exception:
            pass

    if JarvisScheduler:
        res = JarvisScheduler.dismiss_alarm(event_id if event_id else None)
        return res.get("message", "Alarm dismissed, Sir.")
    return "Alarm dismissed, Sir."


async def cancel_reminder(reminder_id_or_title: str) -> str:
    """
    Cancels a scheduled reminder by ID or title.
    """
    if JarvisScheduler:
        res = JarvisScheduler.cancel_reminder(reminder_id_or_title)
        return res.get("message", f"Reminder '{reminder_id_or_title}' cancelled.")
    return f"Reminder '{reminder_id_or_title}' cancelled."


async def reschedule_reminder(reminder_id_or_title: str, new_due_at: str) -> str:
    """
    Reschedules an existing reminder to a new time or date.
    """
    _auto_start_daemon()
    if JarvisScheduler:
        res = JarvisScheduler.reschedule_reminder(reminder_id_or_title, new_due_at)
        return res.get("message", f"Reminder rescheduled to {new_due_at}.")
    return f"Reminder rescheduled to {new_due_at}."


async def check_and_notify_reminders(session=None):
    """
    Periodic check hook called by active chat session.
    Checks and triggers pending/due events.
    """
    _auto_start_daemon()
    if JarvisScheduler:
        try:
            due_events = JarvisScheduler.process_due_events()
            for ev in due_events:
                r_type = ev.get("type", "reminder")
                task = ev.get("title", "Task")
                print(f"🔔 TRIGGER: {task} ({r_type})")
                
                # Trigger audible alert & voice announcement
                try:
                    from tools.jarvis_alarm_announcer import trigger_event_alert
                    trigger_event_alert(ev)
                except Exception:
                    try:
                        from friday_tools.jarvis_alarm_announcer import trigger_event_alert
                        trigger_event_alert(ev)
                    except Exception:
                        winsound.Beep(1000, 1000)

                if session:
                    try:
                        await session.generate_reply(
                            instructions=f"PROACTIVE NOTIFICATION: The {r_type} for '{task}' is due right now. Inform Sir in a natural, polite manner."
                        )
                    except Exception as err:
                        print(f"Failed to send verbal session notification: {err}")
        except Exception as e:
            print(f"[Check Reminders Error]: {e}")
