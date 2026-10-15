"""
ULTRON Omni-Memory RAG & Semantic Clipboard Vault
Continuous knowledge ingestion, clipboard semantic vectorization,
instant spoken recall, and sensitive data protection.
"""

import os
import re
import json
import time
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import pyperclip
except ImportError:
    pyperclip = None

VAULT_DIR = Path.home() / "Documents" / "ULTRON_Data" / "memory_vault"
VAULT_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DB_FILE = VAULT_DIR / "semantic_records.json"


def _load_vault() -> List[Dict[str, Any]]:
    if VAULT_DB_FILE.exists():
        try:
            with open(VAULT_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_vault(records: List[Dict[str, Any]]):
    try:
        with open(VAULT_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _scrub_sensitive_patterns(text: str) -> str:
    """Masks API keys, passwords, and tokens before permanent indexing."""
    # Mask JWT tokens
    text = re.sub(r'eyJ[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{20,}', '[REDACTED_JWT_TOKEN]', text)
    # Mask Bearer tokens
    text = re.sub(r'(Bearer\s+)[a-zA-Z0-9_\-\.]{20,}', r'\1[REDACTED_TOKEN]', text, flags=re.IGNORECASE)
    # Mask Generic API Keys (sk-..., gsk_..., AIza...)
    text = re.sub(r'(sk-[a-zA-Z0-9]{20,}|gsk_[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_\-]{25,})', '[REDACTED_API_KEY]', text)
    return text


def _classify_content(text: str) -> str:
    """Classifies content into Code, URL, Document, or General Note."""
    if re.search(r'https?://[^\s]+', text):
        return "URL/Link"
    if re.search(r'(def |class |import |function |const |let |var |\{|\}|SELECT |FROM |public static)', text):
        return "Code Snippet"
    if len(text.splitlines()) > 5:
        return "Document/Article"
    return "Note/Clipboard"


async def omni_memory_ingest(
    content: str,
    category: str = "general",
    metadata: str = "",
    tags: str = ""
) -> str:
    """
    Ingests text, code snippets, research papers, or clipboard items into the Second Brain vault.
    Automatically scrubs secrets, generates content hashes, and timestamps entries.
    """
    clean_text = _scrub_sensitive_patterns(content.strip())
    if not clean_text:
        return "[MEMORY ERROR] Content cannot be empty."

    vault = _load_vault()
    content_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()[:16]

    # Check duplicates
    for rec in vault:
        if rec.get("hash") == content_hash:
            return f"ℹ️ [OMNI-MEMORY] Content already indexed in vault (Hash: {content_hash})."

    entry = {
        "id": f"mem_{int(time.time()*1000)}",
        "hash": content_hash,
        "content": clean_text,
        "category": _classify_content(clean_text) if category == "general" else category,
        "metadata": metadata.strip(),
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    vault.append(entry)
    _save_vault(vault)

    return (
        f"🧠 [OMNI-MEMORY INGESTED]\n"
        f"• Entry Hash: {content_hash}\n"
        f"• Classification: {entry['category']}\n"
        f"• Length: {len(clean_text)} characters\n"
        f"• Total Vault Entries: {len(vault)}"
    )


async def omni_memory_sync_clipboard() -> str:
    """
    Pulls active Windows clipboard contents, filters out duplicates, and indexes it directly into memory.
    """
    if pyperclip is None:
        return "[MEMORY ERROR] Pyperclip module not available for clipboard reading."

    try:
        clip_text = pyperclip.paste()
        if not clip_text or not clip_text.strip():
            return "ℹ️ [OMNI-MEMORY] System clipboard is currently empty."

        res = await omni_memory_ingest(clip_text.strip(), category="clipboard", metadata="Auto-captured from Windows Clipboard")
        return f"📋 [CLIPBOARD SYNC]\n{res}"
    except Exception as e:
        return f"[MEMORY ERROR] Failed to access clipboard: {e}"


async def omni_memory_semantic_recall(query: str, top_k: int = 5, category: str = "") -> str:
    """
    Performs semantic and contextual retrieval across the Second Brain vault.
    Synthesizes the answer with AI reasoning and triggers spoken audio recall.
    """
    vault = _load_vault()
    if not vault:
        return "🧠 [OMNI-MEMORY] Memory vault is empty. No records stored yet."

    # Filter by category if requested
    records = vault
    if category.strip():
        records = [r for r in vault if category.lower() in r.get("category", "").lower()]

    # Format entries for semantic matching
    entries_text = []
    for r in records[-50:]:  # Take last 50 entries
        entries_text.append(f"[{r.get('timestamp')}] ({r.get('category')} | Tags: {r.get('tags')}): {r.get('content')[:500]}")

    from friday_tools.ai_client import ask_ai
    prompt = f"""
    You are OMNI-MEMORY, ULTRON's Semantic Second Brain & Recall Vault.
    User Query: "{query}"

    Vault Records:
    {chr(10).join(entries_text)}

    Task:
    1. Locate the exact record(s) matching the user's intent.
    2. Provide the precise recalled content (links, code, or notes).
    3. Give a 1-sentence executive summary.
    """
    recalled_info = ask_ai(prompt)

    try:
        from friday_tools.tts_engine import speak_text
        first_line = recalled_info.split("\n")[0] if recalled_info else "Memory retrieved."
        clean_first = re.sub(r'[*_#`]', '', first_line).strip()
        speak_text(f"Memory retrieved: {clean_first[:80]}")
    except Exception:
        pass

    return (
        f"🔍 [OMNI-MEMORY SEMANTIC RECALL // QUERY: '{query}']\n"
        f"{'='*55}\n"
        f"{recalled_info}"
    )


async def omni_memory_vault_summary() -> str:
    """
    Returns high-level statistics, storage volume, categories, and recent memory index points.
    """
    vault = _load_vault()
    categories = {}
    for r in vault:
        cat = r.get("category", "Uncategorized")
        categories[cat] = categories.get(cat, 0) + 1

    summary_lines = [
        f"🧠 [OMNI-MEMORY VAULT STATUS]",
        f"• Total Stored Records: {len(vault)}",
        f"• Vault Location: {VAULT_DB_FILE}",
        f"• Categories Breakdown:"
    ]
    for c, count in categories.items():
        summary_lines.append(f"  - {c}: {count}")

    if vault:
        summary_lines.append("\nRecent Entries:")
        for r in vault[-3:]:
            summary_lines.append(f"  • [{r.get('timestamp')}] {r.get('category')}: {r.get('content')[:70]}...")

    return "\n".join(summary_lines)


async def omni_memory_purge_sensitive(auto_scrub: bool = True) -> str:
    """
    Audits memory records for accidentally leaked credentials or secrets and sanitizes them.
    """
    vault = _load_vault()
    modified_count = 0
    for r in vault:
        original = r.get("content", "")
        scrubbed = _scrub_sensitive_patterns(original)
        if scrubbed != original:
            r["content"] = scrubbed
            modified_count += 1

    if modified_count > 0:
        _save_vault(vault)
        return f"🛡️ [OMNI-MEMORY SANITIZED] Successfully scrubbed sensitive patterns from {modified_count} memory records."
    return "🛡️ [OMNI-MEMORY SANITIZED] No unmasked sensitive secrets found in memory records."
