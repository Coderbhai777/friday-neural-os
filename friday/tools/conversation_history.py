"""
ULTRON Universal Conversation History & Memory Engine
Maintains persistent long-term knowledge (facts, preferences, learned memories) in ultron_memory.json,
while providing clean session isolation so new chats start with a fresh turn buffer
without inheriting stale previous task prompts across Groq and Gemini failovers.
"""

import os
import json
import time
import uuid
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional

PRIMARY_MEMORY_PATH = Path.home() / ".aria" / "ultron_session_memory.json"
BACKUP_MEMORY_PATH = Path.home() / "Documents" / "ULTRON_Data" / "chat_history.json"
MD_MEMORY_PATH = Path.home() / "Documents" / "ULTRON_Data" / "Ultron_Memory.md"
SESSION_STATE_PATH = Path.home() / "Documents" / "ULTRON_Data" / "active_session_state.json"

_lock = threading.Lock()
_CURRENT_SESSION_ID = str(uuid.uuid4())[:8]


def start_new_chat_session() -> str:
    """
    Explicitly starts a fresh chat session.
    Clears the active transient turn buffer while 100% preserving all persistent facts,
    profile data, and learned memories in ultron_memory.json.
    """
    global _CURRENT_SESSION_ID
    with _lock:
        _CURRENT_SESSION_ID = str(uuid.uuid4())[:8]
        try:
            SESSION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            state = {
                "session_id": _CURRENT_SESSION_ID,
                "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "start_timestamp": time.time()
            }
            SESSION_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception:
            pass

        # Clear transient session memory files
        for p in [PRIMARY_MEMORY_PATH, BACKUP_MEMORY_PATH]:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("[]", encoding="utf-8")
            except Exception:
                pass
        return _CURRENT_SESSION_ID


def clear_session_chat():
    """Clears transient session chat log. All long-term facts and memories remain untouched."""
    start_new_chat_session()


def get_current_session_id() -> str:
    global _CURRENT_SESSION_ID
    if SESSION_STATE_PATH.exists():
        try:
            data = json.loads(SESSION_STATE_PATH.read_text(encoding="utf-8"))
            if "session_id" in data:
                _CURRENT_SESSION_ID = data["session_id"]
        except Exception:
            pass
    return _CURRENT_SESSION_ID


def load_turns(current_session_only: bool = True) -> List[Dict[str, Any]]:
    """Loads past conversation turns from disk."""
    with _lock:
        all_turns = []
        seen = set()

        for p in [PRIMARY_MEMORY_PATH, BACKUP_MEMORY_PATH]:
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "text" in item and "role" in item:
                                t_text = str(item.get("text", "")).strip()
                                t_role = "user" if str(item.get("role", "")).lower() in ("user", "human") else "assistant"
                                t_time = str(item.get("timestamp", ""))
                                t_sess = str(item.get("session_id", ""))
                                
                                # Session isolation check
                                cur_sess = get_current_session_id()
                                if current_session_only and t_sess and t_sess != cur_sess:
                                    continue

                                key = (t_role, t_text, t_time)
                                if key not in seen and t_text:
                                    seen.add(key)
                                    all_turns.append({
                                        "role": t_role,
                                        "text": t_text,
                                        "model": item.get("model", "ULTRON-Core"),
                                        "timestamp": t_time or time.strftime("%Y-%m-%d %H:%M:%S"),
                                        "session_id": t_sess or cur_sess
                                    })
                except Exception:
                    pass

        def _sort_key(x):
            return x.get("timestamp", "")

        all_turns.sort(key=_sort_key)
        return all_turns[-40:]


def save_turns(turns: List[Dict[str, Any]]):
    """Saves conversation turns to disk and syncs with Markdown memory."""
    with _lock:
        trimmed = turns[-50:]

        for p in [PRIMARY_MEMORY_PATH, BACKUP_MEMORY_PATH]:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(trimmed, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass

        try:
            _sync_to_markdown(trimmed)
        except Exception:
            pass


def _sync_to_markdown(turns: List[Dict[str, Any]]):
    """Updates the Recent Conversations section in Ultron_Memory.md."""
    if not MD_MEMORY_PATH.exists():
        return
    try:
        content = MD_MEMORY_PATH.read_text(encoding="utf-8")
        if "## Recent Conversations" in content:
            parts = content.split("## Recent Conversations")
            prefix = parts[0]
            suffix = ""
            if "\n---" in parts[1]:
                suffix = "\n---" + parts[1].split("\n---", 1)[1]

            recent_lines = ["## Recent Conversations\n"]
            for t in turns[-12:]:
                ts = t.get("timestamp", time.strftime("%H:%M"))
                role = "User" if t.get("role") == "user" else "ULTRON"
                text = t.get("text", "")
                recent_lines.append(f"- [{ts}] **{role}**: {text[:140]}")

            new_content = prefix + "\n".join(recent_lines) + suffix
            MD_MEMORY_PATH.write_text(new_content, encoding="utf-8")
    except Exception:
        pass


def add_conversation_turn(role: str, text: str, model_name: str = ""):
    """Adds a new turn to the shared conversation memory."""
    if not text or not str(text).strip():
        return
    clean_role = "user" if role.lower() in ("user", "human") else "assistant"
    turns = load_turns(current_session_only=False)
    cur_sess = get_current_session_id()
    entry = {
        "role": clean_role,
        "text": str(text).strip(),
        "model": model_name or "ULTRON-Core",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": cur_sess
    }
    turns.append(entry)
    save_turns(turns)


def get_recent_history(max_turns: int = 10) -> List[Dict[str, str]]:
    """Returns the most recent conversation turns from the current active session."""
    turns = load_turns(current_session_only=True)
    recent = turns[-max_turns:]
    return [{"role": t.get("role", "user"), "text": t.get("text", "")} for t in recent]


def get_full_system_memory_context() -> str:
    """
    Returns complete persistent long-term memory including:
    - User Profile & Core Facts from ultron_memory.json
    - Preferences, Style Guidelines & Habits from ultron_memory.json
    - Learned Memories & Notes from ultron_memory.json
    - Scheduled Milestones & Events from ultron_events.json
    - Project Decisions from project_decisions.json
    - Contacts from ultron_memory.json
    - System integration directives (Minecraft, Subagents)
    (Note: Transient conversation turns are excluded to prevent cross-session instruction contamination)
    """
    context_blocks = []
    data_dir = Path.home() / "Documents" / "ULTRON_Data"

    # 1. Facts, Profile, Preferences & Learned Memory Logs from ultron_memory.json
    try:
        mem_json_path = data_dir / "ultron_memory.json"
        if mem_json_path.exists():
            data = json.loads(mem_json_path.read_text(encoding="utf-8"))

            # Facts & Profile
            facts = data.get("facts", {})
            if "kv" in data and isinstance(data["kv"], dict):
                for k, v in data["kv"].items():
                    if k not in facts:
                        facts[k] = v

            if facts:
                fact_lines = ["## PERSISTENT USER PROFILE & CORE FACTS:"]
                for k, v in facts.items():
                    fact_lines.append(f"- {k}: {v}")
                context_blocks.append("\n".join(fact_lines))

            # User Preferences
            prefs = data.get("preferences", {})
            if prefs:
                pref_lines = ["## USER PREFERENCES & HABITS:"]
                for k, v in prefs.items():
                    pref_lines.append(f"- {k}: {v}")
                context_blocks.append("\n".join(pref_lines))

            # Learned Memory Notes (from remember())
            logs = data.get("logs", [])
            valid_memories = []
            for item in logs[-20:]:
                content = item.get("content", "").strip() if isinstance(item, dict) else str(item).strip()
                if not content or len(content) > 300 or "CONTEXT FROM USER'S DOCUMENTS" in content:
                    continue
                ts = item.get("timestamp", "") if isinstance(item, dict) else ""
                valid_memories.append(f"- [{ts}] {content}" if ts else f"- {content}")

            if valid_memories:
                context_blocks.append("## RECENT LEARNED MEMORIES & NOTES (Remember Across Chats):\n" + "\n".join(valid_memories[-12:]))

            # Contacts
            contacts = data.get("contacts", {})
            if contacts:
                contact_lines = ["## PERSISTENT CONTACTS:"]
                for name, info in contacts.items():
                    phone = info.get("phone", info) if isinstance(info, dict) else info
                    contact_lines.append(f"- {name}: {phone}")
                context_blocks.append("\n".join(contact_lines))

            # Completed Subagents Alert
            alerts = data.get("pending_agent_alerts", [])
            if alerts:
                alert_lines = [
                    "## 🚨 URGENT: SUBAGENTS COMPLETED IN BACKGROUND:",
                    "The following autonomous subagents have finished their work. You MUST proactively inform Sir about these completed tasks and summarize the findings right at the beginning of your response:"
                ]
                for a in alerts[-3:]:
                    alert_lines.append(f"• Subagent [{a.get('agent_id')}] Completed Task: '{a.get('task')}'\n  Key Findings: {a.get('result_preview')}")
                context_blocks.append("\n".join(alert_lines))
    except Exception:
        pass

    # 2. Project Decisions
    try:
        proj_json_path = data_dir / "project_decisions.json"
        if proj_json_path.exists():
            p_data = json.loads(proj_json_path.read_text(encoding="utf-8"))
            if isinstance(p_data, dict) and p_data:
                proj_lines = ["## PROJECT DECISIONS & ARCHITECTURAL CONSTRAINTS:"]
                for proj_name, decs in list(p_data.items())[:6]:
                    if isinstance(decs, list) and decs:
                        latest = decs[-1]
                        d_text = latest.get("decision", "") if isinstance(latest, dict) else str(latest)
                        proj_lines.append(f"- [{proj_name.upper()}]: {d_text}")
                if len(proj_lines) > 1:
                    context_blocks.append("\n".join(proj_lines))
    except Exception:
        pass

    # 3. Events & Schedule
    try:
        events_json_path = data_dir / "ultron_events.json"
        if events_json_path.exists():
            evs = json.loads(events_json_path.read_text(encoding="utf-8"))
            if evs:
                ev_lines = ["## UPCOMING EVENTS & SCHEDULE:"]
                for ev in evs[:8]:
                    ev_lines.append(f"- {ev.get('title', '')} ({ev.get('date', '')}) [Priority: {ev.get('priority', 'normal')}]")
                context_blocks.append("\n".join(ev_lines))
    except Exception:
        pass

    # 4. Dedicated Integration Directives
    mc_directive = (
        "## MINECRAFT SMP DIRECTIVE:\n"
        "- When Shivansh says 'join my SMP', 'join the server', 'connect to Minecraft', or 'log into Minecraft', "
        "DO NOT open the desktop application. You MUST invoke the `start_minecraft_player_bot` tool to log your in-game player character into `hamaraserverkabap.aternos.me:40350`.\n"
        "- When asked to leave the SMP, invoke `stop_minecraft_player_bot`.\n"
        "- When asked about server status, players, or latency, invoke `minecraft_server_status`."
    )
    context_blocks.append(mc_directive)

    subagent_directive = (
        "## AUTONOMOUS SUBAGENT DIRECTIVE (MANDATORY TOOL INVOCATION):\n"
        "- When Shivansh asks to 'spawn a subagent', 'run a subagent', 'subagent chalao', or execute a background task, you MUST IMMEDIATELY trigger the `spawn_subagent(task=...)` tool call.\n"
        "- NEVER respond with conversational promises like 'I will do it' or 'Background mein process chal raha hai' without executing the `spawn_subagent` function tool call in the same turn.\n"
        "- When asked to check subagents, list running processes, or view status, immediately invoke `list_subagents`.\n"
        "- When asked for the output of a completed subagent, invoke `get_subagent_result(agent_id=...)`."
    )
    context_blocks.append(subagent_directive)

    return "\n\n".join(context_blocks)


def get_gemini_history_content(max_turns: int = 10) -> List[Dict[str, Any]]:
    """
    Builds multi-turn history structure for Gemini chat sessions within the current active session.
    Strictly enforces Gemini API constraints:
    1. Must start with 'user'.
    2. Must alternate strictly: user -> model -> user -> model.
    3. Must end with 'model' so chat.send_message(prompt) can be the next 'user' turn.
    """
    turns = load_turns(current_session_only=True)
    recent = turns[-max_turns:]
    if not recent:
        return []

    cleaned = []
    for t in recent:
        role = "user" if t.get("role") == "user" else "model"
        text = str(t.get("text", "")).strip()
        if not text:
            continue

        if not cleaned:
            if role == "user":
                cleaned.append({"role": role, "parts": [{"text": text}]})
        else:
            prev_role = cleaned[-1]["role"]
            if role != prev_role:
                cleaned.append({"role": role, "parts": [{"text": text}]})
            else:
                cleaned[-1]["parts"][0]["text"] += f"\n{text}"

    while cleaned and cleaned[-1]["role"] == "user":
        cleaned.pop()

    return cleaned


def get_groq_messages(system_instruction: str, current_prompt: str, max_turns: int = 10) -> List[Dict[str, str]]:
    """
    Builds a full multi-turn messages array for Groq/OpenAI with current session conversation context.
    Guarantees clean message ordering and prevents consecutive identical roles.
    """
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})

    turns = load_turns(current_session_only=True)
    recent = turns[-max_turns:] if max_turns > 0 else []

    cleaned_turns = []
    for t in recent:
        r = "user" if t.get("role", "user").lower() in ("user", "human") else "assistant"
        txt = str(t.get("text", "")).strip()
        if txt:
            cleaned_turns.append((r, txt))

    while cleaned_turns and cleaned_turns[0][0] != "user":
        cleaned_turns.pop(0)

    for r, txt in cleaned_turns:
        safe_txt = (txt[:347] + "...") if len(txt) > 350 else txt
        if messages and messages[-1]["role"] == r:
            messages[-1]["content"] += f"\n{safe_txt}"
        else:
            messages.append({"role": r, "content": safe_txt})

    clean_prompt = str(current_prompt).strip()
    if messages and messages[-1]["role"] == "user":
        messages.append({"role": "assistant", "content": "Acknowledged."})

    messages.append({"role": "user", "content": clean_prompt})
    return messages


ATTACHMENT_LOG_PATH = Path.home() / "Documents" / "ULTRON_Data" / "latest_chat_attachment.json"


def record_chat_attachment(file_path: str, instruction: str = ""):
    """Records the latest uploaded file or image attachment from the chat panel."""
    data = {
        "file_path": str(file_path),
        "file_name": Path(file_path).name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "instruction": instruction
    }
    try:
        ATTACHMENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ATTACHMENT_LOG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def get_latest_chat_attachment() -> Optional[Dict[str, Any]]:
    """Returns metadata about the latest file or image uploaded to the chat panel."""
    if ATTACHMENT_LOG_PATH.exists():
        try:
            return json.loads(ATTACHMENT_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def clear_conversation_history():
    """Clears the session history across all storage files."""
    start_new_chat_session()
    for p in [PRIMARY_MEMORY_PATH, BACKUP_MEMORY_PATH, ATTACHMENT_LOG_PATH]:
        try:
            if p.exists():
                p.unlink()
        except Exception:
            pass
