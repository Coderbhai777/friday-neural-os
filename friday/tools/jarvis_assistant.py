"""
ULTRON JARVIS Personal Assistant, Notes, Todos, Timers & Calendar Suite
Seamless schedule management, persistent notes, todo checklist, timer alerts, and daily organization.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

ASSISTANT_DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
ASSISTANT_DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_FILE = ASSISTANT_DATA_DIR / "ultron_notes.json"
TODOS_FILE = ASSISTANT_DATA_DIR / "ultron_todos.json"
TIMERS_FILE = ASSISTANT_DATA_DIR / "ultron_timers.json"


def _load_json(file_path: Path, default_val: Any) -> Any:
    if file_path.exists():
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default_val


def _save_json(file_path: Path, data: Any):
    try:
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# ==========================================
# 1. REMINDERS & TIMERS
# ==========================================

async def create_reminder(reminder_text: str, time_str: str) -> str:
    """Sets a voice/visual reminder for a specific time or event."""
    try:
        from friday_tools.briefing import add_upcoming_event
        res = await add_upcoming_event(event=f"Reminder: {reminder_text}", date=time_str, priority="high")
        return f"⏰ [Reminder Set]: '{reminder_text}' scheduled for {time_str}."
    except Exception as e:
        return f"[ERROR] Failed to set reminder: {e}"


async def set_timer(minutes: float, label: str = "Timer") -> str:
    """Sets a countdown timer for N minutes."""
    timers = _load_json(TIMERS_FILE, [])
    target_ts = time.time() + (float(minutes) * 60)
    target_time_str = time.strftime("%I:%M:%S %p", time.localtime(target_ts))
    
    timers.append({
        "label": label,
        "minutes": minutes,
        "expires_at": target_ts,
        "expires_time": target_time_str
    })
    _save_json(TIMERS_FILE, timers)
    return f"⏱️ [Timer Started]: '{label}' set for {minutes} minute(s). Will sound alarm at {target_time_str}."


# ==========================================
# 2. CALENDAR & SCHEDULE
# ==========================================

async def create_calendar_event(title: str, date_time: str, description: str = "") -> str:
    """Adds an event, competition, or meeting to ULTRON's master calendar."""
    from friday_tools.briefing import add_upcoming_event
    return await add_upcoming_event(event=f"{title} - {description}" if description else title, date=date_time)


async def read_calendar(date_or_range: str = "today") -> str:
    """Reads all scheduled events, competitions, and milestones from calendar."""
    from friday_tools.briefing import list_upcoming_events
    return await list_upcoming_events()


# ==========================================
# 3. NOTES & RESEARCH SCRATCHPAD
# ==========================================

async def create_note(title: str, content: str, tags: str = "") -> str:
    """Saves a rich text note or code snippet to ULTRON's persistent notebook."""
    notes = _load_json(NOTES_FILE, [])
    note_entry = {
        "id": f"note_{int(time.time())}",
        "title": title,
        "content": content,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "created_at": time.strftime("%Y-%m-%d %H:%M")
    }
    notes.append(note_entry)
    _save_json(NOTES_FILE, notes)
    return f"📝 [Note Created]: '{title}' saved successfully."


async def search_notes(query: str) -> str:
    """Searches saved notes by title, content, or tags."""
    notes = _load_json(NOTES_FILE, [])
    q = query.lower().strip()
    matches = []
    for n in notes:
        if q in n["title"].lower() or q in n["content"].lower() or any(q in t.lower() for t in n.get("tags", [])):
            matches.append(f"• **{n['title']}** ({n['created_at']}):\n  {n['content'][:250]}...")
            
    if matches:
        return f"📓 [Notes Matching '{query}']:\n\n" + "\n\n".join(matches)
    return f"[Notes] No notes found matching '{query}'."


# ==========================================
# 4. TODOS & ACTION ITEMS
# ==========================================

async def make_todo(task: str, priority: str = "normal", due_date: str = "") -> str:
    """Adds a task to ULTRON's actionable Todo checklist."""
    todos = _load_json(TODOS_FILE, [])
    t_id = f"todo_{len(todos) + 1}"
    entry = {
        "id": t_id,
        "task": task,
        "priority": priority.lower(),
        "due_date": due_date or "Today",
        "status": "pending",
        "created_at": time.strftime("%Y-%m-%d %H:%M")
    }
    todos.append(entry)
    _save_json(TODOS_FILE, todos)
    return f"✅ [Todo Added - #{t_id}]: '{task}' [Priority: {priority.upper()}, Due: {due_date or 'Today'}]."


async def complete_todo(task_id_or_keyword: str) -> str:
    """Marks a todo task as completed."""
    todos = _load_json(TODOS_FILE, [])
    q = task_id_or_keyword.lower().strip()
    completed_task = None
    for t in todos:
        if q == t["id"].lower() or q in t["task"].lower():
            t["status"] = "completed"
            completed_task = t["task"]
            break
            
    if completed_task:
        _save_json(TODOS_FILE, todos)
        return f"🎉 [Todo Completed]: '{completed_task}' marked as DONE."
    return f"[Todo] Could not find pending task matching '{task_id_or_keyword}'."


async def list_todos(status: str = "pending") -> str:
    """Lists todos filtered by status ('pending', 'completed', 'all')."""
    todos = _load_json(TODOS_FILE, [])
    filtered = [t for t in todos if status == "all" or t.get("status") == status]
    if not filtered:
        return f"📋 [Todo List]: No {status} tasks found."
        
    lines = [f"📋 [ULTRON TASK CHECKLIST - {status.upper()}]:"]
    for t in filtered:
        box = "✅" if t.get("status") == "completed" else "⬜"
        prio = f"[{t.get('priority', 'normal').upper()}]"
        lines.append(f"{box} {t['id']}: {prio} {t['task']} (Due: {t.get('due_date', 'N/A')})")
    return "\n".join(lines)
