"""
ULTRON JARVIS Structured Long-Term Memory & Knowledge Repository
Preferences, architectural project decisions, indexed documentation, and cognitive recall.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_MEM_FILE = DATA_DIR / "project_decisions.json"
DOCS_STORE_FILE = DATA_DIR / "knowledge_documents.json"


def _load_data(fp: Path) -> Dict[str, Any]:
    if fp.exists():
        try:
            return json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_data(fp: Path, data: Any):
    try:
        fp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# ==========================================
# 1. USER PREFERENCES & PROJECT MEMORY
# ==========================================

async def remember_user_preference(preference: str, category: str = "general") -> str:
    """Stores a specific user preference, style guideline, or habit."""
    from friday_tools.ultron_memory import _load_memory_json, _save_memory_json, _update_memory_md
    mem = _load_memory_json()
    mem.setdefault("preferences", {})[category] = preference
    _save_memory_json(mem)
    _update_memory_md(mem)
    return f"🧠 [Memory Learned]: Preference recorded under [{category}]: '{preference}'."


async def remember_project_decision(project: str, decision: str, rationale: str = "") -> str:
    """Records an architectural design decision, framework choice, or constraint for a project."""
    data = _load_data(PROJECT_MEM_FILE)
    proj_key = project.lower().strip()
    data.setdefault(proj_key, []).append({
        "decision": decision,
        "rationale": rationale,
        "timestamp": time.strftime("%Y-%m-%d %H:%M")
    })
    _save_data(PROJECT_MEM_FILE, data)
    return f"📐 [Project Memory]: Recorded decision for '{project}': '{decision}' (Rationale: {rationale or 'Standard Architecture'})."


async def retrieve_memory(query: str, category: str = "all") -> str:
    """Retrieves all matching facts, preferences, project decisions, and event logs."""
    from friday_tools.ultron_memory import recall
    results = [recall(query)]
    
    # Also search project decisions
    proj_data = _load_data(PROJECT_MEM_FILE)
    q = query.lower()
    proj_matches = []
    for proj, decs in proj_data.items():
        for d in decs:
            if q in proj or q in d.get("decision", "").lower() or q in d.get("rationale", "").lower():
                proj_matches.append(f"• [{proj.upper()}] {d.get('decision')} (Rationale: {d.get('rationale')})")
    
    if proj_matches:
        results.append("\n📐 [Project Architecture Decisions]:\n" + "\n".join(proj_matches))
        
    return "\n\n".join(results)


# ==========================================
# 2. KNOWLEDGE BASE & DOCUMENT STORAGE
# ==========================================

async def store_document(title: str, content: str, doc_type: str = "text") -> str:
    """Indexes a technical specification, API reference, or design document into ULTRON's local knowledge base."""
    docs = _load_data(DOCS_STORE_FILE)
    if not isinstance(docs, dict):
        docs = {}
    docs[title] = {
        "content": content,
        "type": doc_type,
        "created_at": time.strftime("%Y-%m-%d %H:%M")
    }
    _save_data(DOCS_STORE_FILE, docs)
    return f"📚 [Knowledge Base]: Document '{title}' ({len(content)} chars) indexed successfully."


async def search_knowledge(query: str) -> str:
    """Searches indexed documentation and knowledge base articles."""
    docs = _load_data(DOCS_STORE_FILE)
    if not isinstance(docs, dict) or not docs:
        return "[Knowledge Base] No indexed documents found. Use 'store_document()' to add specs."
        
    q = query.lower().strip()
    matches = []
    for title, doc in docs.items():
        if q in title.lower() or q in doc.get("content", "").lower():
            snippet = doc.get("content", "")[:350]
            matches.append(f"📖 **{title}** ({doc.get('created_at')}):\n{snippet}...")
            
    if matches:
        return f"📚 [Knowledge Matches for '{query}']:\n\n" + "\n\n".join(matches)
    return f"[Knowledge Base] No documentation found matching '{query}'."


async def save_conversation(summary: str, tags: list = None) -> str:
    """Saves a milestone conversation summary to persistent memory."""
    from friday_tools.ultron_memory import add_to_logs
    await add_to_logs(f"[SESSION SUMMARY] {summary} (Tags: {tags or []})")
    return f"[OK] Conversation summary preserved in memory: '{summary[:80]}...'"
