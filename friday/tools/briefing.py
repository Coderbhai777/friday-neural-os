"""
ULTRON Proactive Time-Aware Greeting & Daily Briefing Engine
Provides real-time local time detection, contextual greeting (morning/afternoon/evening),
user birthday detection & celebration (e.g. 7 March), upcoming competition tracking (e.g. IIT TechFest on 15th),
and proactive agenda recommendations.
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

ULTRON_DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
ULTRON_DATA_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_JSON_FILE = ULTRON_DATA_DIR / "ultron_events.json"
MEMORY_JSON_FILE = ULTRON_DATA_DIR / "ultron_memory.json"


def _load_events() -> List[Dict[str, Any]]:
    if EVENTS_JSON_FILE.exists():
        try:
            return json.loads(EVENTS_JSON_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    default_events = [
        {
            "id": "evt_iit_techfest",
            "title": "IIT TechFest Competition",
            "date": "15th",
            "category": "competition",
            "description": "IIT TechFest project exhibition, robotics and AI showcase",
            "priority": "high",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        },
        {
            "id": "evt_user_birthday",
            "title": "User Birthday (Shivansh)",
            "date": "7 March",
            "category": "birthday",
            "description": "Shivansh Sagar Pancholi Birthday",
            "priority": "critical",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    ]
    _save_events(default_events)
    return default_events


def _save_events(events: List[Dict[str, Any]]):
    try:
        EVENTS_JSON_FILE.write_text(
            json.dumps(events, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception:
        pass


def get_user_birthday() -> str:
    """Retrieves user's saved birthday from memory or events."""
    if MEMORY_JSON_FILE.exists():
        try:
            m = json.loads(MEMORY_JSON_FILE.read_text(encoding="utf-8"))
            facts = m.get("facts", {})
            for k in ["birthday", "User Birthday", "user_birthday", "bday"]:
                if k in facts and facts[k]:
                    return str(facts[k])
        except Exception:
            pass

    events = _load_events()
    for ev in events:
        if ev.get("category") == "birthday" or "birthday" in ev.get("title", "").lower():
            return ev.get("date", "7 March")
    return "7 March"


def is_birthday_today() -> Tuple[bool, str]:
    """Checks if today matches the user's birthday (e.g. 7 March)."""
    bday = get_user_birthday()
    now = datetime.now()
    
    # Extract day and month from birthday string
    # Matches '7 March', 'March 7', '7th March', '07-03', etc.
    day_match = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\b", bday)
    day = int(day_match.group(1)) if day_match else None
    
    month_names = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    month = None
    for name, m_num in month_names.items():
        if name in bday.lower():
            month = m_num
            break

    if day is not None and month is not None:
        if now.day == day and now.month == month:
            return True, bday
    elif day is not None and "march" in bday.lower():
        if now.day == day and now.month == 3:
            return True, bday
    
    # Text exact match fallback
    today_str1 = now.strftime("%d %B").lower()  # e.g. "7 march"
    today_str2 = now.strftime("%B %d").lower()  # e.g. "march 7"
    today_str3 = f"{now.day} {now.strftime('%B')}".lower()
    bday_clean = bday.lower().replace("th", "").replace("st", "").replace("nd", "").replace("rd", "").strip()
    
    if (today_str1 in bday_clean) or (today_str2 in bday_clean) or (today_str3 in bday_clean) or (bday_clean in today_str3):
        return True, bday

    return False, bday


def get_time_greeting() -> str:
    """Returns 'Good morning Sir', 'Good afternoon Sir', or 'Good evening Sir' based on local hour."""
    is_bday, _ = is_birthday_today()
    if is_bday:
        return "🎂 Happy Birthday Sir! 🎉"
        
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning Sir"
    elif 12 <= hour < 17:
        return "Good afternoon Sir"
    elif 17 <= hour < 22:
        return "Good evening Sir"
    else:
        return "Good evening Sir"


def get_current_time_str() -> str:
    """Returns formatted current time e.g. '5:35 PM'."""
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def get_upcoming_priorities() -> List[Dict[str, Any]]:
    """Returns high priority events, competitions, and milestones."""
    events = _load_events()
    mem_file = MEMORY_JSON_FILE
    if mem_file.exists():
        try:
            mem_data = json.loads(mem_file.read_text(encoding="utf-8"))
            for ev in mem_data.get("events", []):
                content = ev.get("content", "")
                if content and not any(content.lower() in e.get("title", "").lower() for e in events):
                    events.append({
                        "id": f"mem_{int(time.time())}",
                        "title": content,
                        "date": ev.get("timestamp", ""),
                        "category": "milestone",
                        "priority": "normal"
                    })
        except Exception:
            pass
    return events


async def add_upcoming_event(event: str, date: str = "", priority: str = "high") -> str:
    """
    Saves an upcoming event, competition, deadline, or exam for ULTRON to track and remind you about.
    """
    try:
        events = _load_events()
        new_entry = {
            "id": f"evt_{int(time.time())}",
            "title": event.strip(),
            "date": date.strip() if date else "Upcoming",
            "category": "competition" if ("comp" in event.lower() or "fest" in event.lower() or "hack" in event.lower()) else "event",
            "priority": priority,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        events.append(new_entry)
        _save_events(events)

        try:
            from friday_tools.ultron_memory import remember
            remember(f"Upcoming Event: {event} ({date})")
        except Exception:
            pass

        return f"[OK] Added upcoming event to ULTRON schedule: '{event}' [{date or 'Upcoming'}]."
    except Exception as e:
        return f"[ERROR] Failed to add event: {e}"


async def list_upcoming_events() -> str:
    """
    Lists all saved upcoming competitions, milestones, exams, and events.
    """
    try:
        events = _load_events()
        bday = get_user_birthday()
        lines = ["[CALENDAR] ULTRON Upcoming Milestones & Competitions:", ""]
        lines.append(f"- [ANNUAL] User Birthday: {bday}")
        for idx, ev in enumerate(events, 1):
            title = ev.get("title", "")
            dt = ev.get("date", "")
            prio = ev.get("priority", "normal").upper()
            lines.append(f"{idx}. [{prio}] {title} (Date: {dt})")
        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR] Failed to list events: {e}"


async def delete_upcoming_event(event_name: str) -> str:
    """
    Permanently deletes an event, competition, or deadline from ULTRON's schedule and all memory files.
    Matches event name, ID, or description (case-insensitive).
    """
    try:
        events = _load_events()
        q = event_name.strip().lower()
        if not q:
            return "[ERROR] Please specify the event name or ID to delete."
            
        remaining_events = []
        deleted_titles = []
        
        for ev in events:
            title = ev.get("title", "")
            ev_id = ev.get("id", "")
            desc = ev.get("description", "")
            if q in title.lower() or q in ev_id.lower() or (desc and q in desc.lower()):
                deleted_titles.append(title or ev_id)
            else:
                remaining_events.append(ev)
                
        _save_events(remaining_events)
        
        # Clean up matching items in ultron_memory.json as well
        if MEMORY_JSON_FILE.exists():
            try:
                m_data = json.loads(MEMORY_JSON_FILE.read_text(encoding="utf-8"))
                m_data["events"] = [e for e in m_data.get("events", []) if q not in e.get("content", "").lower()]
                MEMORY_JSON_FILE.write_text(json.dumps(m_data, indent=2, ensure_ascii=False), encoding="utf-8")
                
                from friday_tools.ultron_memory import _update_memory_md
                _update_memory_md(m_data)
            except Exception:
                pass
                
        if deleted_titles:
            return f"[OK] Successfully deleted event(s): {', '.join(deleted_titles)} from ULTRON schedule and memory."
        return f"[NOT FOUND] No event found matching '{event_name}' in calendar."
    except Exception as e:
        return f"[ERROR] Failed to delete event: {e}"


async def delete_event(event_name: str) -> str:
    """Alias for delete_upcoming_event."""
    return await delete_upcoming_event(event_name)


async def clear_all_events() -> str:
    """Clears all scheduled events and competitions."""
    try:
        _save_events([])
        if MEMORY_JSON_FILE.exists():
            try:
                m_data = json.loads(MEMORY_JSON_FILE.read_text(encoding="utf-8"))
                m_data["events"] = []
                MEMORY_JSON_FILE.write_text(json.dumps(m_data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
        return "[OK] All scheduled events and competitions have been cleared."
    except Exception as e:
        return f"[ERROR] Failed to clear events: {e}"



async def get_daily_briefing() -> str:
    """
    Generates a full time-aware briefing with current time, birthday checks, upcoming events (e.g. IIT TechFest), and suggested agenda.
    """
    try:
        is_bday, bday_str = is_birthday_today()
        curr_time = get_current_time_str()
        events = get_upcoming_priorities()

        if is_bday:
            return (
                f"🎂 HAPPY BIRTHDAY SIR! 🎉\n\n"
                f"Wishing you a victorious and magnificent year ahead! The time is {curr_time}.\n"
                f"All ULTRON neural systems, automated workflows, and intelligence engines are at your service for your special day.\n"
                f"Sir, what would you like to build, execute, or explore today?"
            )

        greeting = get_time_greeting()
        if events:
            top_event = events[0]
            event_title = top_event.get("title", "your upcoming milestones")
            event_date = top_event.get("date", "")
            date_part = f" on the {event_date}" if event_date else ""
            
            briefing = (
                f"{greeting}. The time is {curr_time}.\n\n"
                f"You have your {event_title}{date_part} coming up.\n"
                f"Sir, what should we do currently? Shall we plan about your {event_title} or work on something else?"
            )
        else:
            briefing = (
                f"{greeting}. The time is {curr_time}.\n\n"
                f"All systems are online and operational.\n"
                f"Sir, what should we do currently? Awaiting your command."
            )

        return briefing
    except Exception as e:
        return f"{get_time_greeting()}. The time is {get_current_time_str()}. Systems online."


def get_live_system_context() -> str:
    """
    Injects dynamic time, birthday status, and schedule context directly into ULTRON's conversation prompt.
    """
    is_bday, bday_str = is_birthday_today()
    greeting = get_time_greeting()
    curr_time = get_current_time_str()
    events = get_upcoming_priorities()
    
    event_lines = []
    top_title = "IIT TechFest competition on 15th"
    if events:
        top_title = events[0].get("title", top_title)
        for ev in events[:5]:
            event_lines.append(f"- {ev.get('title')} ({ev.get('date')})")
    
    events_str = "\n".join(event_lines) if event_lines else "- IIT TechFest competition on 15th"

    if is_bday:
        return f"""
## REAL-TIME ENVIRONMENT CONTEXT (Live Sync)
- Current Local Time: {curr_time}
- TODAY IS SIR'S BIRTHDAY: {bday_str} (March 7)

## MANDATORY BIRTHDAY CELEBRATION INSTRUCTION
Today is Sir's Birthday!
1. ALWAYS begin with "🎂 Happy Birthday Sir! 🎉 Wishing you a fantastic year ahead! The time is {curr_time}."
2. Celebrate his special day respectfully and authoritatively as ULTRON.
3. Proactively ask how ULTRON can assist in making today extraordinary.
"""

    return f"""
## REAL-TIME ENVIRONMENT CONTEXT (Live Sync)
- Current Local Time: {curr_time}
- Time Phase: {greeting}
- User Birthday: {bday_str} (March 7)
- Upcoming Priorities / Scheduled Items:
{events_str}

## GREETING & MEMORY RECALL GUIDELINES
1. GREET ONLY ONCE at the start of a session. NEVER greet again or announce the time during ongoing conversation.
2. For all follow-up turns, respond directly to the user's query or command without repeating "Hello Sir" or stating the time.
3. If today is Sir's birthday (7 March), warmly congratulate him.
"""
