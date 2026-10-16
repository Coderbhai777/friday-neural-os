# -*- coding: utf-8 -*-
"""
ULTRON Memory System — 7-Tier Autonomous Knowledge & Episodic Gateway
Directly interfaces with Ultron7TierMemoryEngine (SQLite memory.db + working_memory.json + visual_memory)

Public Tool Functions:
- remember(text, memory_type=None, project=None)
- recall(query, memory_type=None)
- search_memory(query, limit=5)
- update_memory(key, value)
- forget(key)
- delete_memory(id_or_content)
- view_brain()
- get_working_memory()
- set_working_task(task, project, steps)
- advance_working_step()
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

try:
    from tools.ultron_memory_engine import (
        MEMORY_ENGINE,
        TYPE_PERSONAL,
        TYPE_EPISODIC,
        TYPE_SEMANTIC,
        TYPE_PROCEDURAL,
        TYPE_WORKING,
        TYPE_VISUAL,
        TYPE_PROJECT,
        ALL_MEMORY_TYPES
    )
except ImportError:
    from friday_tools.ultron_memory_engine import (
        MEMORY_ENGINE,
        TYPE_PERSONAL,
        TYPE_EPISODIC,
        TYPE_SEMANTIC,
        TYPE_PROCEDURAL,
        TYPE_WORKING,
        TYPE_VISUAL,
        TYPE_PROJECT,
        ALL_MEMORY_TYPES
    )

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
MEMORY_MD_FILE = DATA_DIR / "Ultron_Memory.md"
MEMORY_JSON_FILE = DATA_DIR / "ultron_memory.json"
EVENTS_JSON_FILE = DATA_DIR / "ultron_events.json"


def _auto_classify_memory_type(text: str) -> str:
    """Heuristic classifier to map text to one of the 7 memory types."""
    t_lower = text.lower()

    # 1. Personal
    if any(w in t_lower for w in ["my name is", "call me", "i like", "i love", "i enjoy", "i prefer", "my favorite", "my preference", "dont like", "don't like"]):
        return TYPE_PERSONAL

    # 2. Project & Mission
    if any(w in t_lower for w in ["milestone", "project goal", "blocker", "next step", "roadmap", "deadline", "mission"]):
        return TYPE_PROJECT

    # 3. Procedural
    if any(w in t_lower for w in ["how to", "procedure", "workflow", "when fixing", "steps to", "always run", "first inspect"]):
        return TYPE_PROCEDURAL

    # 4. Episodic
    if any(w in t_lower for w in ["yesterday", "earlier", "last night", "was debugging", "we discussed", "interview", "meeting", "exam", "test"]):
        return TYPE_EPISODIC

    # 5. Semantic (Default fact/knowledge)
    return TYPE_SEMANTIC


# =====================================================================
# PUBLIC TOOLS API
# =====================================================================

def remember(
    text: str,
    memory_type: Optional[str] = None,
    project: Optional[str] = None,
    importance: float = 0.7,
    confidence: float = 1.0
) -> str:
    """
    Stores a memory into the 7-tier persistent SQLite memory.db.
    Automatically classifies into personal, episodic, semantic, procedural, working, visual, or project.
    """
    clean_text = str(text or "").strip()
    if not clean_text:
        return "[WARN] Nothing provided to remember."

    # Remove conversational filler words
    t_clean = re.sub(
        r"^(?:please\s+)?(?:remember\s+(?:that\s+)?|keep\s+in\s+mind\s+(?:that\s+)?|note\s+(?:that\s+)?|store\s+(?:that\s+)?)",
        "", clean_text, flags=re.IGNORECASE
    ).strip()

    chosen_type = memory_type if (memory_type and memory_type.lower() in ALL_MEMORY_TYPES) else _auto_classify_memory_type(t_clean)

    # Key-Value fact pattern: "property: value" or "My property is value"
    kv_match = re.match(r"^([\w\s_-]{2,30})\s*[:=]\s*(.+)$", t_clean)
    if kv_match and chosen_type == TYPE_SEMANTIC:
        k = kv_match.group(1).strip()
        v = kv_match.group(2).strip()
        t_clean = f"{k}: {v}"

    rec = MEMORY_ENGINE.sqlite.add_memory(
        content=t_clean,
        memory_type=chosen_type,
        source="direct_tool",
        importance=importance,
        confidence=confidence,
        project=project
    )

    MEMORY_ENGINE._sync_markdown_file()
    return f"🧠 [Stored in {chosen_type.upper()} Memory | ID: {rec.get('id')}]: {t_clean}"


def recall(query: str = "", memory_type: Optional[str] = None) -> str:
    """
    Recalls memories, facts, project goals, and events matching a query across the 7 memory types.
    """
    q_clean = query.strip()
    m_types = [memory_type.lower()] if (memory_type and memory_type.lower() in ALL_MEMORY_TYPES) else None

    results = MEMORY_ENGINE.sqlite.search_memories(
        query=q_clean,
        memory_types=m_types,
        limit=8
    )

    sections = []

    # Check for active working memory / unfinished tasks
    w_state = MEMORY_ENGINE.working.load()
    if w_state.get("active_task"):
        sections.append(
            f"⚡ [ACTIVE MISSION / WORKING MEMORY]:\n"
            f"• Project: {w_state.get('project', 'ULTRON')}\n"
            f"• Active Task: {w_state.get('active_task')}\n"
            f"• Current Step: {w_state.get('current_step')}\n"
            f"• Unfinished Steps: {', '.join(w_state.get('unfinished_steps', []))}"
        )

    if results:
        grouped = {}
        for r in results:
            t = r.get("type", "semantic").upper()
            grouped.setdefault(t, []).append(r)

        for t_name, mems in grouped.items():
            lines = [f"• [{m.get('project') or 'General'}] {m['content']} (Confidence: {m.get('confidence', 1.0):.1f})" for m in mems]
            sections.append(f"🧠 [{t_name} MEMORY]:\n" + "\n".join(lines))

    if not sections:
        return f"No matching memories found for '{query}'."

    return "\n\n".join(sections)


def search_memory(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Programmatic API to search 7-tier memory records."""
    return MEMORY_ENGINE.sqlite.search_memories(query=query, limit=limit)


def update_memory(key_or_id: str, value: str) -> str:
    """Updates an existing memory record in SQLite."""
    success = MEMORY_ENGINE.sqlite.update_memory(key_or_id, content=value)
    if not success:
        # If not an existing ID, search by text or insert as new semantic memory
        matches = MEMORY_ENGINE.sqlite.search_memories(key_or_id, limit=1)
        if matches:
            MEMORY_ENGINE.sqlite.update_memory(matches[0]["id"], content=value)
            success = True
        else:
            rec = MEMORY_ENGINE.sqlite.add_memory(content=f"{key_or_id}: {value}", memory_type=TYPE_SEMANTIC)
            success = bool(rec)

    MEMORY_ENGINE._sync_markdown_file()
    return f"Updated Memory: {key_or_id} = {value}" if success else f"Failed to update memory for '{key_or_id}'."


def forget(key_or_id: str = "") -> str:
    """Removes specific or all memories from persistent SQLite storage."""
    if not key_or_id:
        return "Please specify what memory to forget."
    deleted = MEMORY_ENGINE.sqlite.delete_memory(key_or_id)
    MEMORY_ENGINE._sync_markdown_file()
    return f"Removed memory entry matching '{key_or_id}'." if deleted else f"No memory found matching '{key_or_id}'."


def delete_memory(key_or_id: str) -> str:
    return forget(key_or_id)


def delete_log(key: str) -> str:
    return forget(key)


def clear_old_logs(days: int = 30) -> str:
    return f"Logs older than {days} days retained in long-term SQLite archive."


def view_brain() -> str:
    """Returns a complete categorized overview of the 7-tier ULTRON memory core."""
    sections = ["[ULTRON 7-TIER AUTONOMOUS MEMORY CORE]"]

    # 1. Personal
    personal = MEMORY_ENGINE.sqlite.list_all(memory_type=TYPE_PERSONAL, limit=6)
    if personal:
        sections.append("## 1. Personal Memory (User Identity & Preferences):")
        for m in personal:
            sections.append(f"- **{m['id']}**: {m['content']}")

    # 2. Project
    project = MEMORY_ENGINE.sqlite.list_all(memory_type=TYPE_PROJECT, limit=6)
    if project:
        sections.append("\n## 2. Project & Mission Memory:")
        for m in project:
            sections.append(f"- **[{m.get('project') or 'ULTRON'}]**: {m['content']}")

    # 3. Working Memory
    w_state = MEMORY_ENGINE.working.load()
    sections.append("\n## 3. Working Memory (Current Task State):")
    if w_state.get("active_task"):
        sections.append(f"- Active Task: {w_state.get('active_task')} | Status: {w_state.get('status')}")
        sections.append(f"- Unfinished Steps: {w_state.get('unfinished_steps')}")
    else:
        sections.append("- *(idle / standby)*")

    # 4. Semantic
    semantic = MEMORY_ENGINE.sqlite.list_all(memory_type=TYPE_SEMANTIC, limit=8)
    if semantic:
        sections.append("\n## 4. Semantic Knowledge:")
        for m in semantic:
            sections.append(f"- {m['content']}")

    # 5. Procedural
    procedural = MEMORY_ENGINE.sqlite.list_all(memory_type=TYPE_PROCEDURAL, limit=5)
    if procedural:
        sections.append("\n## 5. Procedural Memory (Skills):")
        for m in procedural:
            sections.append(f"- {m['content']}")

    # 6. Episodic
    episodic = MEMORY_ENGINE.sqlite.list_all(memory_type=TYPE_EPISODIC, limit=6)
    if episodic:
        sections.append("\n## 6. Episodic Past Events:")
        for m in episodic:
            sections.append(f"- [{m['timestamp'][:16]}] {m['content']}")

    # 7. Visual
    v = MEMORY_ENGINE.visual.get_latest_observation()
    sections.append("\n## 7. Visual Memory:")
    if v:
        sections.append(f"- Latest Screen: {v.get('title')} ({v.get('app')}) -> {v.get('summary')}")
    else:
        sections.append("- *(no recent visual states)*")

    sections.append(f"\nStorage: {DATA_DIR / 'memory.db'} (SQLite Source of Truth)")
    return "\n".join(sections)


def get_working_memory() -> Dict[str, Any]:
    """Returns the current active working memory state."""
    return MEMORY_ENGINE.working.load()


def set_working_task(task: str, project: str = "ULTRON", steps: Optional[List[str]] = None) -> str:
    """Sets the active unfinished task in working memory."""
    MEMORY_ENGINE.working.set_active_task(task, project, steps)
    return f"Active task set in Working Memory: {task} ({len(steps or [task])} step(s))."


def advance_working_step(completed_step: Optional[str] = None) -> str:
    """Marks a step complete and advances working memory."""
    next_step = MEMORY_ENGINE.working.advance_step(completed_step)
    if next_step:
        return f"Step completed. Next unfinished step: {next_step}"
    return "All steps for active task completed!"


def auto_detect_and_store(prompt: str) -> Optional[str]:
    """Detects implicit facts, preferences, or tasks in user prompts."""
    MEMORY_ENGINE.record_interaction(prompt, "")
    return None


def save_memory(data: dict):
    """Saves memory payload."""
    MEMORY_ENGINE._sync_markdown_file()


def load_memory() -> dict:
    """Loads all memories categorized."""
    return {t: MEMORY_ENGINE.sqlite.list_all(memory_type=t, limit=20) for t in ALL_MEMORY_TYPES}


def save_fact(key: str, value: str) -> str:
    return remember(f"{key}: {value}", memory_type=TYPE_SEMANTIC)


def get_fact(key: str) -> str:
    res = recall(key, memory_type=TYPE_SEMANTIC)
    return res


def add_to_logs(text: str = "", content: str = "") -> str:
    msg = text or content or ""
    if not msg:
        return "[OK] No content to log."
    return remember(msg, memory_type=TYPE_EPISODIC)
