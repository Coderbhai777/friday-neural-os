# -*- coding: utf-8 -*-
"""
ULTRON Ω — Epistemic Memory Engine & Screen-to-Memory Fallback Subsystem
Features:
- Strict 4-tier knowledge classification:
    1. OBSERVED_FACT: Currently visible on screen right now
    2. STORED_MEMORY: Recorded preference/task from a past session
    3. INFERENCE: Hypothesis framed with calibrated uncertainty
    4. UNKNOWN: Explicitly admitted uncertainty
- Screen-to-Memory Fallback: Hypothesizes past project context without falsely claiming it is currently visible
- Emotional & Conversational Continuity (celebrates bug fixes, supports rough days, respects boundaries)
- Memory CRUD: inspect, correct, and delete stored items
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
MEMORY_FILE = DATA_DIR / "ultron_memory.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_memory() -> Dict[str, Any]:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "facts": {
            "user_name": "Shivansh Sagar Pancholi",
            "active_projects": ["ULTRON", "Photon-Chess-Engine", "Blue-Whale"],
            "interests": ["Robotics", "AI Engineering", "Chess", "Anime"]
        },
        "recent_tasks": [],
        "preferences": {},
        "conversational_history": []
    }


def _save_memory(mem: Dict[str, Any]):
    MEMORY_FILE.write_text(json.dumps(mem, indent=2, ensure_ascii=False), encoding="utf-8")


# -------------------------------------------------------------
# 1. SCREEN-TO-MEMORY FALLBACK (HYPOTHESIS ENGINE)
# -------------------------------------------------------------

def generate_memory_fallback_prompt(recent_activity: str = None) -> Dict[str, Any]:
    """
    Called when screen observation is unavailable, obscured, or inconclusive.
    Retrieves past project memory and frames it as a hypothesis, NOT an asserted fact.
    """
    mem = _load_memory()
    recent = mem.get("recent_tasks", [])
    projects = mem.get("facts", {}).get("active_projects", ["your project"])

    last_task = recent[-1] if recent else {"project": projects[0] if projects else "your project", "task": "development"}
    proj_name = last_task.get("project", "your project")

    hypothesis = f"Earlier, you were working on your {proj_name} project. Are you continuing that, or doing something different now?"

    return {
        "status": "MEMORY_FALLBACK",
        "epistemic_level": "INFERENCE",
        "basis": "STORED_MEMORY",
        "project": proj_name,
        "spoken_text": hypothesis,
        "is_currently_visible": False
    }


def record_task_activity(project_name: str, task_description: str):
    """Records an activity into recent task history."""
    mem = _load_memory()
    tasks = mem.setdefault("recent_tasks", [])
    tasks.append({
        "project": project_name,
        "task": task_description,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    # Keep last 15
    mem["recent_tasks"] = tasks[-15:]
    _save_memory(mem)


# -------------------------------------------------------------
# 2. EMOTIONAL CONTEXT & CONVERSATIONAL CONTINUITY
# -------------------------------------------------------------

def handle_conversational_context(user_utterance: str) -> Optional[str]:
    """
    Detects emotional markers and task milestones to provide natural follow-ups.
    Never claims human consciousness or feelings.
    """
    u_lower = user_utterance.lower().strip()

    # Bad day / burnout check-in
    if any(k in u_lower for k in ["bad day", "rough day", "terrible day", "exhausted", "tired of this"]):
        return "I'm sorry it was a rough day. Want to talk about what happened, or would you rather take your mind off it?"

    # Bug fix celebration
    if any(k in u_lower for k in ["fixed that bug", "fixed the bug", "finally working", "it works now", "resolved the issue"]):
        return "Nice! Was it the same issue you were stuck on earlier?"

    # New ambitious project/idea
    if any(k in u_lower for k in ["new idea", "what if we build", "crazy idea", "thinking about building"]):
        return "That sounds interesting. Want to explore how we'd actually build it?"

    # User says stop discussing
    if any(k in u_lower for k in ["stop talking about", "don't want to talk about", "drop it", "never mind"]):
        return "Understood, Sir. Dropping the topic."

    return None


# -------------------------------------------------------------
# 3. MEMORY CRUD CONTROLS
# -------------------------------------------------------------

def inspect_memory(query: str = "") -> Dict[str, Any]:
    """Inspects stored facts, preferences, and recent project memories."""
    mem = _load_memory()
    if not query:
        return mem
    q = query.lower()
    filtered = {
        "facts": {k: v for k, v in mem.get("facts", {}).items() if q in str(k).lower() or q in str(v).lower()},
        "preferences": {k: v for k, v in mem.get("preferences", {}).items() if q in str(k).lower() or q in str(v).lower()},
        "recent_tasks": [t for t in mem.get("recent_tasks", []) if q in str(t).lower()]
    }
    return filtered


def correct_memory(key: str, new_value: Any, category: str = "facts") -> bool:
    """Updates or corrects an existing memory entry."""
    mem = _load_memory()
    if category not in mem:
        mem[category] = {}
    if isinstance(mem[category], dict):
        mem[category][key] = new_value
        _save_memory(mem)
        return True
    return False


def delete_memory(key: str, category: str = "facts") -> bool:
    """Permanently deletes a specific memory item."""
    mem = _load_memory()
    if category in mem and isinstance(mem[category], dict) and key in mem[category]:
        del mem[category][key]
        _save_memory(mem)
        return True
    return False
