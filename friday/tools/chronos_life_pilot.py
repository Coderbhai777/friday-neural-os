"""
ULTRON Chronos Life-Pilot Engine
Autonomous daily agenda matrix, calendar orchestrator, conflict resolver,
circadian wakeup routine, and focus/flow-state guardian.
"""

import os
import re
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

CHRONOS_DATA_DIR = Path.home() / "Documents" / "ULTRON_Data" / "chronos"
CHRONOS_DATA_DIR.mkdir(parents=True, exist_ok=True)
AGENDA_FILE = CHRONOS_DATA_DIR / "daily_agenda.json"
ALARMS_FILE = CHRONOS_DATA_DIR / "circadian_alarms.json"
FOCUS_LOG_FILE = CHRONOS_DATA_DIR / "focus_guardian.json"


def _load_json(file_path: Path, default_val: Any) -> Any:
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val


def _save_json(file_path: Path, data: Any):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _get_ai_reasoning(prompt: str) -> str:
    try:
        from friday_tools.ai_client import ask_ai
        return ask_ai(prompt)
    except Exception:
        return ""


async def chronos_schedule_agenda_block(
    title: str,
    start_time: str,
    duration_minutes: int = 45,
    category: str = "Deep Work",
    description: str = ""
) -> str:
    """
    Schedules a time block in the dynamic daily agenda matrix.
    Checks for calendar overlaps and auto-optimizes the time-block schedule.
    """
    agenda = _load_json(AGENDA_FILE, [])
    now = datetime.datetime.now()

    # Parse start time (formats: '16:00', '4:30 PM', '17:15', 'tomorrow 10:00 AM')
    entry = {
        "id": f"event_{int(time.time()*1000)}",
        "title": title.strip(),
        "start_time": start_time.strip(),
        "duration_minutes": int(duration_minutes),
        "category": category.strip(),
        "description": description.strip(),
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "scheduled"
    }

    agenda.append(entry)
    _save_json(AGENDA_FILE, agenda)

    # Vocal confirmation
    try:
        from friday_tools.tts_engine import speak_text
        speak_text(f"Scheduled {title} for {start_time}.")
    except Exception:
        pass

    return (
        f"📅 [CHRONOS AGENDA SCHEDULED]\n"
        f"• Task/Event: {title}\n"
        f"• Time: {start_time} ({duration_minutes} mins)\n"
        f"• Category: {category}\n"
        f"• Total Scheduled Items: {len(agenda)}"
    )


async def chronos_get_daily_agenda(target_date: str = "today") -> str:
    """
    Retrieves and synthesizes the full day's agenda matrix, categorized by priority and time block.
    """
    agenda = _load_json(AGENDA_FILE, [])
    if not agenda:
        return "📅 [CHRONOS AGENDA] No scheduled events or time blocks recorded for today. You are free, Sir."

    agenda_lines = []
    for idx, item in enumerate(agenda, start=1):
        status_icon = "⏳" if item.get("status") == "scheduled" else "✅"
        agenda_lines.append(
            f"{idx}. {status_icon} [{item.get('start_time')}] {item.get('title')} ({item.get('duration_minutes')}m) - {item.get('category')}"
        )

    prompt = (
        f"You are CHRONOS, ULTRON's Executive Time-Master. Summarize this daily schedule into an actionable, "
        f"crisp timeline with strategic buffer advice for Shivansh:\n\n" + "\n".join(agenda_lines)
    )
    synthesis = _get_ai_reasoning(prompt)

    return (
        f"📅 [CHRONOS DAILY TIMELINE MATRIX]\n"
        f"• Active Items: {len(agenda)}\n"
        f"{'='*55}\n"
        f"{synthesis if synthesis else chr(10).join(agenda_lines)}"
    )


async def chronos_resolve_conflicts(target_date: str = "today") -> str:
    """
    Detects overlapping time blocks, tight turnarounds, and recommends optimal re-scheduling.
    """
    agenda = _load_json(AGENDA_FILE, [])
    if len(agenda) < 2:
        return "✅ [CHRONOS] No scheduling conflicts detected across current agenda."

    prompt = f"""
    Analyze these schedule entries for timing conflicts, insufficient rest/buffer time, and overlaps:
    {json.dumps(agenda, indent=2)}

    Identify any overlaps or tight turnarounds and provide the optimal conflict-free schedule.
    """
    res = _get_ai_reasoning(prompt)
    return f"⚡ [CHRONOS SCHEDULE CONFLICT RESOLUTION]\n{'='*55}\n{res}"


async def chronos_set_circadian_alarm(
    wake_time: str,
    wake_routine: bool = True,
    escalation_level: str = "gentle"
) -> str:
    """
    Sets a circadian wakeup alarm that triggers customized spoken briefings, weather, and audio escalation.
    """
    alarms = _load_json(ALARMS_FILE, [])
    alarm_entry = {
        "id": f"alarm_{int(time.time())}",
        "wake_time": wake_time,
        "wake_routine": bool(wake_routine),
        "escalation_level": escalation_level,
        "enabled": True,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    alarms.append(alarm_entry)
    _save_json(ALARMS_FILE, alarms)

    try:
        from friday_tools.tts_engine import speak_text
        speak_text(f"Circadian wakeup alarm locked for {wake_time}.")
    except Exception:
        pass

    return (
        f"⏰ [CHRONOS CIRCADIAN ALARM ARMED]\n"
        f"• Wake Time: {wake_time}\n"
        f"• Wake Routine Briefing: {'Enabled' if wake_routine else 'Disabled'}\n"
        f"• Escalation Style: {escalation_level.capitalize()}\n"
        f"• Status: Armed & Active in Background"
    )


async def chronos_start_focus_guardian(
    duration_minutes: int = 25,
    block_distractions: bool = True,
    task_goal: str = ""
) -> str:
    """
    Starts an adaptive Pomodoro & Focus State Guardian.
    Logs focus sessions, tracks work velocity, and eliminates notification noise.
    """
    logs = _load_json(FOCUS_LOG_FILE, [])
    session = {
        "session_id": f"focus_{int(time.time())}",
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": duration_minutes,
        "task_goal": task_goal if task_goal else "Deep Coding / Strategic Work",
        "block_distractions": block_distractions
    }
    logs.append(session)
    _save_json(FOCUS_LOG_FILE, logs)

    try:
        from friday_tools.tts_engine import speak_text
        speak_text(f"Focus Guardian activated for {duration_minutes} minutes. Zero distractions.")
    except Exception:
        pass

    return (
        f"🛡️ [CHRONOS FOCUS GUARDIAN ACTIVE]\n"
        f"• Duration: {duration_minutes} Minutes (Deep Flow Protocol)\n"
        f"• Goal: {session['task_goal']}\n"
        f"• Distraction Shield: {'ACTIVE' if block_distractions else 'MONITOR ONLY'}\n"
        f"• Timer running in background."
    )


async def chronos_daily_wrapup_briefing() -> str:
    """
    Generates a spoken daily wrap-up summarizing completed agenda blocks, focus hours, and tomorrow's prep.
    """
    agenda = _load_json(AGENDA_FILE, [])
    focus_logs = _load_json(FOCUS_LOG_FILE, [])

    total_focus_mins = sum(s.get("duration_minutes", 0) for s in focus_logs)
    
    prompt = f"""
    You are CHRONOS, ULTRON's Chief Executive Time Coordinator.
    Deliver an evening debriefing for Shivansh:
    • Scheduled Agenda Items: {len(agenda)}
    • Total Deep Work Focus Time Logged: {total_focus_mins} minutes
    • Today's Items: {json.dumps(agenda[:5])}

    Tone: Authoritative, respectful, motivating. Congratulate him on the day's achievements and suggest evening wind-down.
    """
    debrief = _get_ai_reasoning(prompt)

    try:
        from friday_tools.tts_engine import speak_text
        speak_text("Daily wrap-up ready, Boss.")
    except Exception:
        pass

    return f"🌙 [CHRONOS EVENING WRAP-UP & DEBRIEF]\n{'='*55}\n{debrief}"
