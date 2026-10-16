# -*- coding: utf-8 -*-
"""
ULTRON Ω — 7-Tier Autonomous Persistent Memory Engine
Architecture: SQLite (memory.db) + JSON (working_memory.json, world_model.json) + visual_memory/

Provides 7 distinct memory types:
1. Personal memory: Name, preferred communication style, interests, preferences.
2. Episodic memory: Past events, interactions, debug sessions, past conversations.
3. Semantic memory: Facts, explanations, knowledge learned from conversations and documents.
4. Procedural memory: Step-by-step procedures and workflows for performing tasks.
5. Working memory: Current task, recent messages, open application, unfinished steps.
6. Visual memory: Screen observations, application states, changes between screenshots.
7. Project and mission memory: Project decisions, goals, blockers, next unfinished steps across restarts.

Features:
- SQLite source of truth with FTS5 full-text search (zero paid API keys required).
- Standardized metadata schema (id, type, content, source, timestamp, importance, confidence, project, expires_at).
- Automatic memory retrieval & context builder hooked into the AI decision loop.
- Memory writer with deduplication, confidence scoring, and fact extraction.
- Persistent mission & unfinished task recovery across PC restarts.
"""

import os
import sys
import json
import time
import uuid
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

# Storage directories
DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_DB_FILE = DATA_DIR / "memory.db"
WORKING_MEMORY_FILE = DATA_DIR / "working_memory.json"
WORLD_MODEL_FILE = DATA_DIR / "world_model.json"
VISUAL_MEMORY_DIR = DATA_DIR / "visual_memory"
VISUAL_MEMORY_DIR.mkdir(parents=True, exist_ok=True)

LEGACY_MEMORY_FILE = DATA_DIR / "ultron_memory.json"
LEGACY_MD_FILE = DATA_DIR / "Ultron_Memory.md"

# 7 Formal Memory Types
TYPE_PERSONAL = "personal"
TYPE_EPISODIC = "episodic"
TYPE_SEMANTIC = "semantic"
TYPE_PROCEDURAL = "procedural"
TYPE_WORKING = "working"
TYPE_VISUAL = "visual"
TYPE_PROJECT = "project"

ALL_MEMORY_TYPES = [
    TYPE_PERSONAL,
    TYPE_EPISODIC,
    TYPE_SEMANTIC,
    TYPE_PROCEDURAL,
    TYPE_WORKING,
    TYPE_VISUAL,
    TYPE_PROJECT,
]


# =====================================================================
# 1. SQLITE PERSISTENT STORAGE (memory.db)
# =====================================================================

class UltronSQLiteMemory:
    """Thread-safe SQLite storage for long-term memories with FTS5 search."""

    def __init__(self, db_path: Path = MEMORY_DB_FILE):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._lock:
            conn = self._get_connection()
            try:
                # Main memories table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        source TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        importance REAL DEFAULT 0.5,
                        confidence REAL DEFAULT 1.0,
                        project TEXT,
                        expires_at TEXT,
                        metadata TEXT
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);")

                # FTS5 virtual table for lightning-fast lexical search
                try:
                    conn.execute("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                            id UNINDEXED,
                            content,
                            project,
                            type,
                            tokenize='porter unicode61'
                        );
                    """)
                except Exception:
                    # Fallback if FTS5 is not compiled in
                    pass

                conn.commit()
            finally:
                conn.close()

    def add_memory(
        self,
        content: str,
        memory_type: str = TYPE_SEMANTIC,
        source: str = "conversation",
        importance: float = 0.5,
        confidence: float = 1.0,
        project: Optional[str] = None,
        expires_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Inserts or updates a memory record with deduplication and metadata."""
        clean_content = content.strip()
        if not clean_content:
            return {}

        mem_type = memory_type.lower() if memory_type.lower() in ALL_MEMORY_TYPES else TYPE_SEMANTIC
        clean_project = project.strip() if project else None
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                # Check for near-exact deduplication within same type/project
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, content, importance, confidence FROM memories WHERE type = ? AND content = ? LIMIT 1;",
                    (mem_type, clean_content)
                )
                existing = cursor.fetchone()
                if existing:
                    existing_id = existing["id"]
                    # Update importance / confidence if new is higher
                    new_importance = max(existing["importance"], importance)
                    new_confidence = max(existing["confidence"], confidence)
                    meta_str = json.dumps(metadata or {}, ensure_ascii=False)
                    cursor.execute("""
                        UPDATE memories 
                        SET importance = ?, confidence = ?, timestamp = ?, project = COALESCE(?, project), metadata = ?
                        WHERE id = ?;
                    """, (new_importance, new_confidence, now_iso, clean_project, meta_str, existing_id))
                    conn.commit()
                    return {
                        "id": existing_id,
                        "type": mem_type,
                        "content": clean_content,
                        "source": source,
                        "timestamp": now_iso,
                        "importance": new_importance,
                        "confidence": new_confidence,
                        "project": clean_project,
                        "expires_at": expires_at,
                        "metadata": metadata or {}
                    }

                # Create fresh memory record
                new_id = memory_id or f"mem_{uuid.uuid4().hex[:8]}"
                meta_str = json.dumps(metadata or {}, ensure_ascii=False)

                cursor.execute("""
                    INSERT INTO memories (id, type, content, source, timestamp, importance, confidence, project, expires_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    new_id, mem_type, clean_content, source, now_iso,
                    importance, confidence, clean_project, expires_at, meta_str
                ))

                # Update FTS
                try:
                    cursor.execute("""
                        INSERT INTO memories_fts (id, content, project, type)
                        VALUES (?, ?, ?, ?);
                    """, (new_id, clean_content, clean_project or "", mem_type))
                except Exception:
                    pass

                conn.commit()

                return {
                    "id": new_id,
                    "type": mem_type,
                    "content": clean_content,
                    "source": source,
                    "timestamp": now_iso,
                    "importance": importance,
                    "confidence": confidence,
                    "project": clean_project,
                    "expires_at": expires_at,
                    "metadata": metadata or {}
                }
            finally:
                conn.close()

    def search_memories(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        project: Optional[str] = None,
        limit: int = 5,
        min_confidence: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Searches memories with ranking based on relevance, importance, confidence, and recency."""
        q_clean = query.strip()
        results = []

        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # If query is empty, return highest importance recent memories
                if not q_clean:
                    sql = "SELECT * FROM memories WHERE confidence >= ?"
                    params: List[Any] = [min_confidence]
                    if memory_types:
                        sql += f" AND type IN ({','.join(['?'] * len(memory_types))})"
                        params.extend(memory_types)
                    if project:
                        sql += " AND project = ?"
                        params.append(project)
                    sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?;"
                    params.append(limit)
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    return [self._row_to_dict(r) for r in rows]

                # FTS5 search first
                fts_ids = []
                # Clean tokens for FTS
                tokens = re.findall(r"\w+", q_clean)
                if tokens:
                    fts_query = " OR ".join(tokens)
                    try:
                        cursor.execute(
                            "SELECT id FROM memories_fts WHERE memories_fts MATCH ? LIMIT 20;",
                            (fts_query,)
                        )
                        fts_ids = [row["id"] for row in cursor.fetchall()]
                    except Exception:
                        fts_ids = []

                # Fallback / Union with LIKE matching
                like_conditions = []
                like_params = []
                for t in tokens[:4]:
                    like_conditions.append("content LIKE ?")
                    like_params.append(f"%{t}%")

                where_clauses = ["confidence >= ?"]
                params = [min_confidence]

                if memory_types:
                    where_clauses.append(f"type IN ({','.join(['?'] * len(memory_types))})")
                    params.extend(memory_types)

                if project:
                    where_clauses.append("project = ?")
                    params.append(project)

                if fts_ids:
                    id_placeholders = ",".join(["?"] * len(fts_ids))
                    match_clause = f"(id IN ({id_placeholders})"
                    params.extend(fts_ids)
                    if like_conditions:
                        match_clause += f" OR ({' OR '.join(like_conditions)})"
                        params.extend(like_params)
                    match_clause += ")"
                    where_clauses.append(match_clause)
                elif like_conditions:
                    where_clauses.append(f"({' OR '.join(like_conditions)})")
                    params.extend(like_params)

                sql = f"SELECT * FROM memories WHERE {' AND '.join(where_clauses)} LIMIT 30;"
                cursor.execute(sql, params)
                rows = cursor.fetchall()

                # Score & rank memories:
                # Score = (0.5 * token_overlap) + (0.3 * importance) + (0.2 * confidence)
                query_words = set(t.lower() for t in tokens)
                scored = []
                for r in rows:
                    content_lower = r["content"].lower()
                    content_words = set(re.findall(r"\w+", content_lower))
                    overlap = len(query_words.intersection(content_words)) / max(1, len(query_words))
                    
                    score = (0.5 * overlap) + (0.3 * (r["importance"] or 0.5)) + (0.2 * (r["confidence"] or 1.0))
                    scored.append((score, self._row_to_dict(r)))

                scored.sort(key=lambda x: x[0], reverse=True)
                return [item[1] for item in scored[:limit]]
            finally:
                conn.close()

    def get_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM memories WHERE id = ?;", (memory_id,))
                row = cursor.fetchone()
                return self._row_to_dict(row) if row else None
            finally:
                conn.close()

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        importance: Optional[float] = None,
        confidence: Optional[float] = None,
        project: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM memories WHERE id = ?;", (memory_id,))
                row = cursor.fetchone()
                if not row:
                    return False

                new_content = content if content is not None else row["content"]
                new_importance = importance if importance is not None else row["importance"]
                new_confidence = confidence if confidence is not None else row["confidence"]
                new_project = project if project is not None else row["project"]
                new_meta = json.dumps(metadata, ensure_ascii=False) if metadata is not None else row["metadata"]
                now_iso = datetime.now(timezone.utc).isoformat()

                cursor.execute("""
                    UPDATE memories
                    SET content = ?, importance = ?, confidence = ?, project = ?, metadata = ?, timestamp = ?
                    WHERE id = ?;
                """, (new_content, new_importance, new_confidence, new_project, new_meta, now_iso, memory_id))

                # Update FTS
                try:
                    cursor.execute("DELETE FROM memories_fts WHERE id = ?;", (memory_id,))
                    cursor.execute("""
                        INSERT INTO memories_fts (id, content, project, type)
                        VALUES (?, ?, ?, ?);
                    """, (memory_id, new_content, new_project or "", row["type"]))
                except Exception:
                    pass

                conn.commit()
                return True
            finally:
                conn.close()

    def delete_memory(self, memory_id_or_content: str) -> bool:
        clean = memory_id_or_content.strip()
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                # Find matching IDs first
                cursor.execute(
                    "SELECT id FROM memories WHERE id = ? OR content = ? OR content LIKE ?;",
                    (clean, clean, f"%{clean}%")
                )
                ids = [r["id"] for r in cursor.fetchall()]
                if not ids:
                    return False

                id_placeholders = ",".join(["?"] * len(ids))
                cursor.execute(f"DELETE FROM memories WHERE id IN ({id_placeholders});", ids)
                deleted = cursor.rowcount > 0
                try:
                    cursor.execute(f"DELETE FROM memories_fts WHERE id IN ({id_placeholders});", ids)
                except Exception:
                    pass
                conn.commit()
                return deleted
            finally:
                conn.close()

    def list_all(self, memory_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if memory_type:
                    cursor.execute(
                        "SELECT * FROM memories WHERE type = ? ORDER BY timestamp DESC LIMIT ?;",
                        (memory_type, limit)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM memories ORDER BY timestamp DESC LIMIT ?;",
                        (limit,)
                    )
                return [self._row_to_dict(r) for r in cursor.fetchall()]
            finally:
                conn.close()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        meta = {}
        if row["metadata"]:
            try:
                meta = json.loads(row["metadata"])
            except Exception:
                meta = {}
        return {
            "id": row["id"],
            "type": row["type"],
            "content": row["content"],
            "source": row["source"],
            "timestamp": row["timestamp"],
            "importance": row["importance"],
            "confidence": row["confidence"],
            "project": row["project"],
            "expires_at": row["expires_at"],
            "metadata": meta
        }


# =====================================================================
# 2. WORKING MEMORY & WORLD MODEL STORAGE (JSON)
# =====================================================================

class UltronWorkingMemory:
    """Manages working_memory.json: active conversation, current task, unfinished steps across restarts."""

    def __init__(self, file_path: Path = WORKING_MEMORY_FILE):
        self.file_path = file_path
        self._lock = threading.Lock()
        self.state = self.load()

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if self.file_path.exists():
                try:
                    return json.loads(self.file_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            default_state = {
                "active_task": None,
                "project": "ULTRON",
                "status": "idle",
                "unfinished_steps": [],
                "current_step": None,
                "open_application": "VS Code",
                "recent_messages": [],
                "last_active_window": None,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            self._save(default_state)
            return default_state

    def _save(self, data: Dict[str, Any]):
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def set_active_task(self, task: str, project: str = "ULTRON", steps: Optional[List[str]] = None):
        with self._lock:
            self.state["active_task"] = task
            self.state["project"] = project
            self.state["status"] = "in_progress"
            self.state["unfinished_steps"] = steps or [task]
            self.state["current_step"] = steps[0] if steps else task
            self._save(self.state)

    def advance_step(self, completed_step: Optional[str] = None) -> Optional[str]:
        """Marks current step done, advances to next unfinished step."""
        with self._lock:
            steps = self.state.get("unfinished_steps", [])
            if steps:
                if completed_step and completed_step in steps:
                    steps.remove(completed_step)
                else:
                    steps.pop(0)
            self.state["unfinished_steps"] = steps
            if steps:
                self.state["current_step"] = steps[0]
            else:
                self.state["current_step"] = None
                self.state["status"] = "completed"
            self._save(self.state)
            return self.state.get("current_step")

    def record_message(self, role: str, text: str):
        with self._lock:
            msgs = self.state.setdefault("recent_messages", [])
            msgs.append({
                "role": role,
                "text": text[:300],
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self.state["recent_messages"] = msgs[-12:]
            self._save(self.state)

    def update_open_application(self, app_title: str):
        with self._lock:
            self.state["open_application"] = app_title
            self.state["last_active_window"] = app_title
            self._save(self.state)

    def get_unfinished_summary(self) -> Optional[str]:
        with self._lock:
            task = self.state.get("active_task")
            steps = self.state.get("unfinished_steps", [])
            proj = self.state.get("project", "ULTRON")
            if task and steps:
                return f"Project '{proj}': {task} (Current step: {self.state.get('current_step')}, Remaining: {len(steps)})"
            return None


class UltronVisualMemory:
    """Manages visual memory: screen states, application transitions, and summaries."""

    def __init__(self, dir_path: Path = VISUAL_MEMORY_DIR):
        self.dir_path = dir_path
        self.log_file = dir_path / "screen_states.jsonl"
        self._lock = threading.Lock()

    def record_screen_observation(
        self,
        app_name: str,
        window_title: str,
        summary: str,
        changes_detected: bool = False,
        screenshot_path: Optional[str] = None
    ):
        with self._lock:
            self.dir_path.mkdir(parents=True, exist_ok=True)
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "app": app_name,
                "title": window_title,
                "summary": summary,
                "changes_detected": changes_detected,
                "screenshot": screenshot_path
            }
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_latest_observation(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            if not self.log_file.exists():
                return None
            try:
                lines = self.log_file.read_text(encoding="utf-8").strip().splitlines()
                if lines:
                    return json.loads(lines[-1])
            except Exception:
                pass
            return None


# =====================================================================
# 3. CONSOLIDATED 7-TIER MEMORY ENGINE
# =====================================================================

class Ultron7TierMemoryEngine:
    """
    Central orchestration engine for all 7 ULTRON memory types.
    Handles storage, automatic retrieval, context building, and post-action updates.
    """

    def __init__(self):
        self.sqlite = UltronSQLiteMemory()
        self.working = UltronWorkingMemory()
        self.visual = UltronVisualMemory()
        self._ensure_seed_memories()

    def _ensure_seed_memories(self):
        """Seeds initial core personal & project knowledge if database is fresh."""
        existing = self.sqlite.list_all(limit=5)
        if not existing:
            # 1. Personal Memory
            self.sqlite.add_memory(
                content="The user's name is Shivansh Sagar Pancholi. He is a Coder, Chess ACM, and Autonomous AI Architect.",
                memory_type=TYPE_PERSONAL,
                source="system",
                importance=1.0,
                confidence=1.0,
                project="ULTRON"
            )
            self.sqlite.add_memory(
                content="User enjoys anime, robotics, chess, and prefers ULTRON to speak naturally without waiting for a wake word.",
                memory_type=TYPE_PERSONAL,
                source="system",
                importance=0.9,
                confidence=1.0,
                project="ULTRON"
            )
            # 2. Semantic Memory
            self.sqlite.add_memory(
                content="The ULTRON repository contains an advanced world model, proactive vision companion, and verification engine.",
                memory_type=TYPE_SEMANTIC,
                source="system",
                importance=0.85,
                confidence=1.0,
                project="ULTRON"
            )
            # 3. Procedural Memory
            self.sqlite.add_memory(
                content="When fixing a bug, inspect the logs, reproduce the issue, make a change, and run a test to verify procedural integrity.",
                memory_type=TYPE_PROCEDURAL,
                source="system",
                importance=0.9,
                confidence=1.0,
                project="ULTRON"
            )
            # 4. Project & Mission Memory
            self.sqlite.add_memory(
                content="ULTRON milestone: Implement reliable 7-type autonomous persistent memory retrieval across PC restarts.",
                memory_type=TYPE_PROJECT,
                source="system",
                importance=0.95,
                confidence=1.0,
                project="ULTRON"
            )

        # Migrate legacy files if present
        self._migrate_legacy_data()

    def _migrate_legacy_data(self):
        """Migrates legacy ultron_memory.json items into SQLite memory.db."""
        if LEGACY_MEMORY_FILE.exists():
            try:
                legacy = json.loads(LEGACY_MEMORY_FILE.read_text(encoding="utf-8"))
                # Facts -> Semantic / Personal
                facts = legacy.get("facts", {})
                for k, v in facts.items():
                    if k in ["user_name", "interests"]:
                        self.sqlite.add_memory(
                            content=f"User {k}: {v}",
                            memory_type=TYPE_PERSONAL,
                            importance=0.9,
                            project="ULTRON"
                        )
                    elif k == "active_projects":
                        self.sqlite.add_memory(
                            content=f"Active projects: {', '.join(v) if isinstance(v, list) else v}",
                            memory_type=TYPE_PROJECT,
                            importance=0.9,
                            project="ULTRON"
                        )
                    else:
                        self.sqlite.add_memory(
                            content=f"{k}: {v}",
                            memory_type=TYPE_SEMANTIC,
                            importance=0.7,
                            project="ULTRON"
                        )

                # Recent tasks -> Episodic
                for task in legacy.get("recent_tasks", []):
                    proj = task.get("project", "ULTRON")
                    t_desc = task.get("task", "")
                    if t_desc:
                        self.sqlite.add_memory(
                            content=f"Task worked on in {proj}: {t_desc}",
                            memory_type=TYPE_EPISODIC,
                            importance=0.6,
                            project=proj
                        )
            except Exception:
                pass

    # -------------------------------------------------------------
    # 4. AUTOMATIC MEMORY RETRIEVAL & CONTEXT BUILDER
    # -------------------------------------------------------------

    def retrieve_relevant_memories(
        self,
        query: str,
        limit_per_type: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves the most useful memories across the 7 types:
        Personal, Episodic, Semantic, Procedural, Working, Visual, Project.
        """
        memories = {}

        # 1. Personal: Always retrieve high-importance personal facts
        personal = self.sqlite.search_memories(query, memory_types=[TYPE_PERSONAL], limit=limit_per_type)
        if not personal:
            personal = self.sqlite.search_memories("", memory_types=[TYPE_PERSONAL], limit=2)
        memories[TYPE_PERSONAL] = personal

        # 2. Project & Mission: Critical for cross-restart continuity
        project_mems = self.sqlite.search_memories(query, memory_types=[TYPE_PROJECT], limit=limit_per_type)
        if not project_mems:
            project_mems = self.sqlite.search_memories("", memory_types=[TYPE_PROJECT], limit=2)
        memories[TYPE_PROJECT] = project_mems

        # 3. Working Memory (Current unfinished tasks)
        working_state = self.working.load()
        memories[TYPE_WORKING] = [working_state]

        # 4. Semantic Knowledge
        memories[TYPE_SEMANTIC] = self.sqlite.search_memories(query, memory_types=[TYPE_SEMANTIC], limit=limit_per_type)

        # 5. Procedural Memory
        memories[TYPE_PROCEDURAL] = self.sqlite.search_memories(query, memory_types=[TYPE_PROCEDURAL], limit=limit_per_type)

        # 6. Episodic Past Events
        memories[TYPE_EPISODIC] = self.sqlite.search_memories(query, memory_types=[TYPE_EPISODIC], limit=limit_per_type)

        # 7. Visual Memory (Latest screen observation)
        latest_vis = self.visual.get_latest_observation()
        memories[TYPE_VISUAL] = [latest_vis] if latest_vis else []

        return memories

    def build_injected_context(self, user_query: str) -> str:
        """
        Formats retrieved memories across all 7 types into a compact, high-density system context block.
        """
        retrieved = self.retrieve_relevant_memories(user_query)

        lines = ["\n[ULTRON 7-TIER PERSISTENT MEMORY CONTEXT]"]

        # 1. Personal
        if retrieved.get(TYPE_PERSONAL):
            p_facts = [f"• {m['content']}" for m in retrieved[TYPE_PERSONAL]]
            lines.append("👤 PERSONAL MEMORY:\n" + "\n".join(p_facts))

        # 2. Project / Mission
        if retrieved.get(TYPE_PROJECT):
            proj_facts = [f"• [{m.get('project') or 'ULTRON'}] {m['content']}" for m in retrieved[TYPE_PROJECT]]
            lines.append("🎯 PROJECT & MISSION MEMORY:\n" + "\n".join(proj_facts))

        # 3. Working Memory
        w_state = retrieved.get(TYPE_WORKING, [{}])[0]
        if w_state.get("active_task"):
            lines.append(
                f"⚡ WORKING MEMORY (UNFINISHED):\n"
                f"• Task: {w_state.get('active_task')} | Status: {w_state.get('status')} | Current Step: {w_state.get('current_step')}\n"
                f"• Open App: {w_state.get('open_application')}"
            )
        elif w_state.get("open_application"):
            lines.append(f"⚡ WORKING MEMORY:\n• Open App: {w_state.get('open_application')}")

        # 4. Visual Memory
        v_state = retrieved.get(TYPE_VISUAL, [])
        if v_state and v_state[0]:
            v = v_state[0]
            lines.append(f"👁️ VISUAL MEMORY:\n• Screen State: {v.get('title')} ({v.get('app')}) -> {v.get('summary', 'Active')}")

        # 5. Semantic Knowledge
        if retrieved.get(TYPE_SEMANTIC):
            s_facts = [f"• {m['content']}" for m in retrieved[TYPE_SEMANTIC]]
            lines.append("🧠 SEMANTIC KNOWLEDGE:\n" + "\n".join(s_facts))

        # 6. Procedural Memory
        if retrieved.get(TYPE_PROCEDURAL):
            proc_facts = [f"• {m['content']}" for m in retrieved[TYPE_PROCEDURAL]]
            lines.append("🛠️ PROCEDURAL MEMORY:\n" + "\n".join(proc_facts))

        # 7. Episodic Past Events
        if retrieved.get(TYPE_EPISODIC):
            ep_facts = [f"• [{m['timestamp'][:10]}] {m['content']}" for m in retrieved[TYPE_EPISODIC]]
            lines.append("📜 EPISODIC MEMORY:\n" + "\n".join(ep_facts))

        lines.append("Use these memories seamlessly to maintain absolute continuity across restarts.\n")
        return "\n\n".join(lines)

    # -------------------------------------------------------------
    # 5. MEMORY WRITER (POST-INTERACTION & VERIFICATION)
    # -------------------------------------------------------------

    def record_interaction(
        self,
        user_message: str,
        assistant_reply: str,
        active_app: Optional[str] = None
    ):
        """
        Extracts new facts, events, and task updates, and records working memory turns.
        """
        # 1. Update working memory turns
        self.working.record_message("user", user_message)
        self.working.record_message("assistant", assistant_reply)
        if active_app:
            self.working.update_open_application(active_app)

        u_clean = user_message.strip()
        u_lower = u_clean.lower()

        # 2. Auto-detect project commands (e.g. "continue the project", "let's work on X")
        proj_match = re.search(r"(?:work on|working on|continue(?: with)?|start)\s+(?:the\s+)?([a-zA-Z0-9_-]+(?:\s+[a-zA-Z0-9_-]+)?)", u_clean, re.I)
        if proj_match and "continue" in u_lower:
            proj_name = proj_match.group(1).strip()
            self.working.set_active_task(f"Developing {proj_name}", project=proj_name)

        # 3. Auto-detect facts & preferences ("my X is Y", "remember that X")
        fact_match = re.match(r"^(?:my|mera|our)\s+([\w\s_-]{2,30})\s+(?:is|are|hai)\s+(.+)$", u_clean, re.IGNORECASE)
        if fact_match:
            prop = fact_match.group(1).strip()
            val = fact_match.group(2).strip()
            self.sqlite.add_memory(
                content=f"User's {prop} is {val}",
                memory_type=TYPE_PERSONAL if any(w in prop.lower() for w in ["name", "style", "interest", "like", "favorite"]) else TYPE_SEMANTIC,
                source="conversation",
                importance=0.8,
                confidence=1.0
            )

        # 4. Auto-detect procedural instructions ("when doing X, always Y")
        if u_lower.startswith("when ") and ("always" in u_lower or "should" in u_lower or "must" in u_lower):
            self.sqlite.add_memory(
                content=u_clean,
                memory_type=TYPE_PROCEDURAL,
                source="conversation",
                importance=0.85,
                confidence=1.0
            )

        # 5. Auto-detect events & exams
        if any(w in u_lower for w in ["exam", "test", "interview", "meeting", "deadline", "flight"]):
            self.sqlite.add_memory(
                content=u_clean,
                memory_type=TYPE_EPISODIC,
                source="conversation",
                importance=0.8,
                confidence=1.0
            )

        # 6. Sync human-readable markdown
        self._sync_markdown_file()

    def _sync_markdown_file(self):
        """Regenerates Ultron_Memory.md for readable auditing."""
        try:
            lines = [
                "# ULTRON 7-Tier Autonomous Memory Core\n",
                f"*Last synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
                "---\n"
            ]

            # Personal
            lines.append("## 1. Personal Memory (Identity & Preferences)\n")
            for m in self.sqlite.list_all(memory_type=TYPE_PERSONAL, limit=10):
                lines.append(f"- **[{m['id']}]** {m['content']}")

            # Project
            lines.append("\n## 2. Project & Mission Memory\n")
            for m in self.sqlite.list_all(memory_type=TYPE_PROJECT, limit=10):
                lines.append(f"- **[{m['project'] or 'General'}]** {m['content']}")

            # Working
            lines.append("\n## 3. Working Memory (Current Task State)\n")
            unfin = self.working.get_unfinished_summary()
            lines.append(f"- {unfin or 'No pending unfinished tasks.'}")

            # Semantic
            lines.append("\n## 4. Semantic Memory (Facts & Knowledge)\n")
            for m in self.sqlite.list_all(memory_type=TYPE_SEMANTIC, limit=15):
                lines.append(f"- **[{m['id']}]** {m['content']}")

            # Procedural
            lines.append("\n## 5. Procedural Memory (Skills & Workflows)\n")
            for m in self.sqlite.list_all(memory_type=TYPE_PROCEDURAL, limit=10):
                lines.append(f"- **[{m['id']}]** {m['content']}")

            # Episodic
            lines.append("\n## 6. Episodic Memory (Events & History)\n")
            for m in self.sqlite.list_all(memory_type=TYPE_EPISODIC, limit=10):
                lines.append(f"- [{m['timestamp'][:16]}] {m['content']}")

            # Visual
            lines.append("\n## 7. Visual Memory (Screen & Workspace)\n")
            v = self.visual.get_latest_observation()
            if v:
                lines.append(f"- Latest Screen: {v.get('title')} ({v.get('app')}) -> {v.get('summary', 'Active')}")
            else:
                lines.append("- *(no recent screen states recorded)*")

            LEGACY_MD_FILE.write_text("\n".join(lines), encoding="utf-8")
        except Exception:
            pass


# Global Singleton Instance
MEMORY_ENGINE = Ultron7TierMemoryEngine()


# =====================================================================
# 6. BACKWARD-COMPATIBLE API (For existing tests & tools)
# =====================================================================

def generate_memory_fallback_prompt(recent_activity: str = None) -> Dict[str, Any]:
    """
    Called when screen observation is unavailable, obscured, or inconclusive.
    Retrieves past project memory and frames it as a hypothesis, NOT an asserted fact.
    Preserves exact contract expected by tests and companion.
    """
    # Look for last project task
    tasks = MEMORY_ENGINE.sqlite.list_all(memory_type=TYPE_EPISODIC, limit=5)
    last_task = None
    proj_name = "your project"

    for t in tasks:
        if t.get("project") and t["project"] != "ULTRON":
            proj_name = t["project"]
            last_task = t
            break

    if not last_task:
        working_state = MEMORY_ENGINE.working.load()
        proj_name = working_state.get("project") or "your project"

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
    """Records an activity into episodic and project memory."""
    MEMORY_ENGINE.sqlite.add_memory(
        content=f"Task worked on in {project_name}: {task_description}",
        memory_type=TYPE_EPISODIC,
        source="system",
        importance=0.7,
        project=project_name
    )
    MEMORY_ENGINE.working.set_active_task(task_description, project=project_name)

    # Also keep legacy JSON file updated for older components
    try:
        mem = {}
        if LEGACY_MEMORY_FILE.exists():
            mem = json.loads(LEGACY_MEMORY_FILE.read_text(encoding="utf-8"))
        tasks = mem.setdefault("recent_tasks", [])
        tasks.append({
            "project": project_name,
            "task": task_description,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        mem["recent_tasks"] = tasks[-15:]
        LEGACY_MEMORY_FILE.write_text(json.dumps(mem, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def handle_conversational_context(user_utterance: str) -> Optional[str]:
    """Detects emotional markers and conversational milestones."""
    u_lower = user_utterance.lower().strip()

    if any(k in u_lower for k in ["bad day", "rough day", "terrible day", "exhausted", "tired of this"]):
        return "I'm sorry it was a rough day. Want to talk about what happened, or would you rather take your mind off it?"

    if any(k in u_lower for k in ["fixed that bug", "fixed the bug", "finally working", "it works now", "resolved the issue"]):
        return "Nice! Was it the same issue you were stuck on earlier?"

    if any(k in u_lower for k in ["new idea", "what if we build", "crazy idea", "thinking about building"]):
        return "That sounds interesting. Want to explore how we'd actually build it?"

    if any(k in u_lower for k in ["stop talking about", "don't want to talk about", "drop it", "never mind"]):
        return "Understood, Sir. Dropping the topic."

    return None


def inspect_memory(query: str = "") -> Dict[str, Any]:
    """Inspects stored memories across types."""
    if not query:
        all_mems = MEMORY_ENGINE.sqlite.list_all(limit=50)
    else:
        all_mems = MEMORY_ENGINE.sqlite.search_memories(query, limit=50)

    categorized = {t: [] for t in ALL_MEMORY_TYPES}
    for m in all_mems:
        t = m.get("type", TYPE_SEMANTIC)
        if t in categorized:
            categorized[t].append(m)
        else:
            categorized[TYPE_SEMANTIC].append(m)
    return categorized


def correct_memory(key_or_id: str, new_value: Any, category: str = TYPE_SEMANTIC) -> bool:
    """Updates an existing memory record in SQLite."""
    # Try by ID first
    mem = MEMORY_ENGINE.sqlite.get_by_id(key_or_id)
    if mem:
        return MEMORY_ENGINE.sqlite.update_memory(key_or_id, content=str(new_value))

    # Try searching for content matching key
    matches = MEMORY_ENGINE.sqlite.search_memories(key_or_id, limit=1)
    if matches:
        return MEMORY_ENGINE.sqlite.update_memory(matches[0]["id"], content=str(new_value))

    # Add as new
    MEMORY_ENGINE.sqlite.add_memory(
        content=f"{key_or_id}: {new_value}",
        memory_type=category,
        importance=0.8
    )
    return True


def delete_memory(key_or_id: str, category: str = TYPE_SEMANTIC) -> bool:
    """Deletes an existing memory record."""
    return MEMORY_ENGINE.sqlite.delete_memory(key_or_id)
