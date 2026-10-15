"""
ULTRON Memory System - Learns about the user and stores knowledge in Markdown & JSON.
Maintains persistent user profile, facts, preferences, exams, and conversation history.
"""

import os
import json
import re
from datetime import datetime, date, timedelta
from pathlib import Path

ULTRON_DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
MEMORY_MD_FILE = ULTRON_DATA_DIR / "Ultron_Memory.md"
MEMORY_JSON_FILE = ULTRON_DATA_DIR / "ultron_memory.json"
EVENTS_JSON_FILE = ULTRON_DATA_DIR / "ultron_events.json"


def _ensure_memory_md():
    """Create the memory markdown file if it doesn't exist."""
    if not MEMORY_MD_FILE.exists():
        MEMORY_MD_FILE.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_MD_FILE.write_text(
            "# ULTRON Memory\n\n"
            "This file contains everything ULTRON has learned about Shivansh.\n"
            "ULTRON updates this file automatically as it learns.\n\n"
            "---\n\n"
            "## User Profile\n\n"
            "- **Name**: Shivansh Sagar Pancholi\n"
            "- **Role**: Coder, Chess ACM, and Developer\n\n"
            "---\n\n"
            "## Facts & Knowledge\n\n"
            "---\n\n"
            "## Events & Schedule\n\n"
            "---\n\n"
            "## Recent Conversations\n\n",
            encoding="utf-8",
        )


def _load_memory_json():
    """Load structured memory from JSON with automated schema migration."""
    data = {"facts": {}, "events": [], "logs": [], "preferences": {}, "contacts": {}, "pending_agent_alerts": []}
    if MEMORY_JSON_FILE.exists():
        try:
            loaded = json.loads(MEMORY_JSON_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update(loaded)
                if "kv" in data and isinstance(data["kv"], dict):
                    for k, v in data["kv"].items():
                        if k not in data["facts"]:
                            data["facts"][k] = v
        except Exception:
            pass
    for k in ["facts", "preferences", "contacts"]:
        if not isinstance(data.get(k), dict):
            data[k] = {}
    for k in ["events", "logs", "pending_agent_alerts"]:
        if not isinstance(data.get(k), list):
            data[k] = []
    return data


def _save_memory_json(data):
    """Save structured memory to JSON."""
    MEMORY_DATA_DIR = MEMORY_JSON_FILE.parent
    MEMORY_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_JSON_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _update_memory_md(data):
    """Regenerate the markdown file from structured data."""
    _ensure_memory_md()
    lines = ["# ULTRON Memory\n"]
    lines.append("This file contains everything ULTRON has learned about Shivansh.\n")
    lines.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    lines.append("\n---\n")

    # User Profile
    lines.append("\n## User Profile\n")
    for k, v in data.get("facts", {}).items():
        lines.append(f"- **{k}**: {v}")
    if not data.get("facts"):
        lines.append("- *(learning...)*")
    lines.append("\n---\n")

    # Preferences
    lines.append("\n## Preferences\n")
    for k, v in data.get("preferences", {}).items():
        lines.append(f"- **{k}**: {v}")
    if not data.get("preferences"):
        lines.append("- *(learning...)*")
    lines.append("\n---\n")

    # Events & Exams
    lines.append("\n## Events & Schedule\n")
    for ev in data.get("events", [])[-20:]:
        ts = ev.get("timestamp", "")
        content = ev.get("content", "")
        lines.append(f"- [{ts}] {content}")
    if not data.get("events"):
        lines.append("- *(no events yet)*")
    lines.append("\n---\n")

    # Conversation Logs
    lines.append("\n## Recent Conversations\n")
    for log in data.get("logs", [])[-30:]:
        ts = log.get("timestamp", "")
        content = log.get("content", "")
        lines.append(f"- [{ts}] {content}")
    if not data.get("logs"):
        lines.append("- *(no logs yet)*")
    lines.append("\n---\n")

    # Contacts
    lines.append("\n## Contacts\n")
    for name, info in data.get("contacts", {}).items():
        if isinstance(info, dict):
            phone = info.get("phone", "")
            notes = info.get("notes", "")
            lines.append(f"- **{name}**: {phone} {('(' + notes + ')') if notes else ''}")
        else:
            lines.append(f"- **{name}**: {info}")
    if not data.get("contacts"):
        lines.append("- *(no contacts yet)*")

    MEMORY_MD_FILE.write_text("\n".join(lines), encoding="utf-8")


# ========================
# PUBLIC API
# ========================

def remember(text: str) -> str:
    """Store a memory/fact/event with automated fact extraction and multi-turn persistence."""
    clean_text = str(text or "").strip()
    if not clean_text:
        return "[WARN] Nothing provided to remember."

    data = _load_memory_json()
    entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "content": clean_text}
    data["logs"].append(entry)

    # 1. Clean trigger words
    t_clean = re.sub(r"^(?:please\s+)?(?:remember\s+(?:that\s+)?|keep\s+in\s+mind\s+(?:that\s+)?|note\s+(?:that\s+)?|store\s+(?:that\s+)?)", "", clean_text, flags=re.IGNORECASE).strip()

    # 2. Key-Value pattern
    kv_match = re.match(r"^([\w\s_-]{2,30})\s*[:=]\s*(.+)$", t_clean)
    if kv_match:
        k = kv_match.group(1).strip()
        v = kv_match.group(2).strip()
        data["facts"][k] = v

    # 3. "My <property> is <value>" pattern
    my_match = re.match(r"^(?:my|mera|our)\s+([\w\s_-]{2,30})\s+(?:is|hai|are)\s+(.+)$", t_clean, flags=re.IGNORECASE)
    if my_match:
        k = my_match.group(1).strip()
        v = my_match.group(2).strip()
        data["facts"][k] = v

    # 4. Auto-detect events & specialized entities
    event_kw = ["meeting", "interview", "appointment", "tomorrow", "today",
                "exam", "test", "flight", "trip", "birthday", "deadline", "party", "hackathon"]
    if any(kw in clean_text.lower() for kw in event_kw):
        data["events"].append(entry)

    _save_memory_json(data)
    _update_memory_md(data)
    return f"🧠 [Stored in ULTRON Memory]: {clean_text}"


def auto_detect_and_store(prompt: str):
    """Detects implicit facts, exams, or events in user prompts."""
    p_lower = prompt.lower()
    if "exam" in p_lower or "test" in p_lower or "paper" in p_lower:
        if "english" in p_lower:
            update_memory("Upcoming Exam", "English Exam (2026-10-09 - Tomorrow)")


def recall(query: str = "") -> str:
    """Recall memories, facts, exams, and events matching a query."""
    data = _load_memory_json()
    results = []
    q_lower = query.lower().strip()

    # 1. Check Events from ultron_events.json & ultron_memory.json
    events_list = []
    if EVENTS_JSON_FILE.exists():
        try:
            evs = json.loads(EVENTS_JSON_FILE.read_text(encoding="utf-8"))
            if isinstance(evs, list):
                for e in evs:
                    title = e.get("title", "")
                    edate = e.get("date", "")
                    events_list.append(f"• {title} (Date: {edate})")
        except Exception:
            pass

    for ev in data.get("events", []):
        c = ev.get("content", "")
        if c and c not in [e.replace("• ", "") for e in events_list]:
            events_list.append(f"• {c}")

    # If asking for exams / tomorrow / schedule
    if not q_lower or any(w in q_lower for w in ["exam", "tomorrow", "test", "schedule", "events", "kal", "all", "everything", "facts"]):
        if events_list:
            results.append("📅 [UPCOMING EXAMS & EVENTS]:\n" + "\n".join(events_list))

    # 2. Search facts
    matched_facts = []
    for k, v in data.get("facts", {}).items():
        if not q_lower or q_lower in k.lower() or q_lower in str(v).lower() or any(w in q_lower for w in ["fact", "profile", "all", "memory", "exam"]):
            matched_facts.append(f"• {k}: {v}")

    if matched_facts:
        results.append("🧠 [STORED FACTS & PROFILE]:\n" + "\n".join(matched_facts))

    # 3. Search logs
    matched_logs = []
    for log in data.get("logs", []):
        content = log.get("content", "")
        if len(content) > 250 or "CONTEXT FROM USER" in content:
            continue
        if not q_lower or q_lower in content.lower():
            matched_logs.append(f"• [{log.get('timestamp', '')}] {content}")

    if matched_logs:
        results.append("📝 [KNOWLEDGE LOGS]:\n" + "\n".join(matched_logs[-6:]))

    if not results:
        return f"No matching memories found for '{query}'."
    return "\n\n".join(results)


def view_brain() -> str:
    """View complete contents of ULTRON memory core."""
    data = _load_memory_json()
    sections = ["[ULTRON COMPREHENSIVE MEMORY MATRIX]"]

    # Facts
    facts = data.get("facts", {})
    if facts:
        sections.append("## Core User Facts & Profile:")
        for k, v in facts.items():
            sections.append(f"- **{k}**: {v}")

    # Events & Schedule
    events = data.get("events", [])
    if events:
        sections.append("\n## Upcoming Exams & Schedule:")
        for ev in events[-6:]:
            sections.append(f"- [{ev.get('timestamp', '')}] {ev.get('content', '')}")

    # Preferences
    prefs = data.get("preferences", {})
    if prefs:
        sections.append("\n## User Preferences:")
        for k, v in prefs.items():
            sections.append(f"- **{k}**: {v}")

    # Logs
    logs = [l for l in data.get("logs", []) if len(l.get("content", "")) < 250 and "CONTEXT" not in l.get("content", "")]
    if logs:
        sections.append("\n## Recent Knowledge Logs:")
        for l in logs[-8:]:
            sections.append(f"- [{l.get('timestamp', '')}] {l.get('content', '')}")

    sections.append(f"\nStorage File: {MEMORY_MD_FILE}")
    return "\n".join(sections)



def get_recent_conversations(count: int = 10) -> str:
    """Retrieves recent conversations from disk."""
    import friday_tools.conversation_history as mem
    turns = mem.load_turns(current_session_only=False)
    if not turns:
        return "No past conversation turns logged on disk."
    lines = ["💬 [RECENT CONVERSATION ARCHIVE]:"]
    for t in turns[-count:]:
        role = "User (Shivansh)" if t.get("role") == "user" else "ULTRON"
        lines.append(f"• [{t.get('timestamp', '')}] **{role}**: {t.get('text', '')[:120]}")
    return "\n".join(lines)


def forget(key: str = "") -> str:
    """Clear specific or all memories across storage files."""
    data = _load_memory_json()
    if key:
        k_lower = key.lower().strip()
        data["facts"] = {k: v for k, v in data.get("facts", {}).items() if k_lower not in k.lower() and k_lower not in str(v).lower()}
        data["logs"] = [l for l in data.get("logs", []) if k_lower not in l.get("content", "").lower()]
        data["events"] = [e for e in data.get("events", []) if k_lower not in e.get("content", "").lower()]
    else:
        data = {"facts": {}, "events": [], "logs": [], "preferences": {}, "contacts": {}, "pending_agent_alerts": []}

    _save_memory_json(data)
    _update_memory_md(data)
    return "Memory cleared." if not key else f"Removed entries matching '{key}'."


def delete_event(key: str) -> str:
    return forget(key)


def update_memory(key: str, value: str) -> str:
    """Update a specific fact."""
    data = _load_memory_json()
    data["facts"][key] = value
    _save_memory_json(data)
    _update_memory_md(data)
    return f"Updated: {key} = {value}"


def save_fact(key: str, value: str) -> str:
    return update_memory(key, value)


def get_fact(key: str) -> str:
    data = _load_memory_json()
    return data.get("facts", {}).get(key, f"No fact found for '{key}'.")


def search_memory(query: str, limit: int = 5) -> list:
    return [recall(query)]


def load_memory() -> dict:
    return _load_memory_json()


def save_memory(data: dict):
    _save_memory_json(data)
    _update_memory_md(data)


async def add_to_logs(text: str = "", content: str = "") -> str:
    msg = text or content or ""
    if not msg:
        return "[OK] No content to log."
    data = _load_memory_json()
    data.setdefault("logs", []).append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "content": msg,
    })
    _save_memory_json(data)
    _update_memory_md(data)
    return f"[OK] Added to logs: {msg}"
