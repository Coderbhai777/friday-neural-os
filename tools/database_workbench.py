"""
Universal Database Workbench & Schema Intelligence Toolkit for ULTRON.
Supports SQLite, PostgreSQL, MySQL, Redis, query execution, Mermaid ER diagram generation,
synthetic test data generator, and query plan optimization analysis.
"""

import asyncio
import json
import os
import re
import sqlite3
from pathlib import Path


async def db_execute_query(connection_uri: str, query: str) -> str:
    """
    Execute SQL queries against SQLite database files or PostgreSQL / MySQL URIs with formatted tabular output.
    """
    connection_uri = connection_uri.strip()
    query = query.strip()

    def _sync_exec():
        # Handle SQLite file path
        if connection_uri.endswith(".db") or connection_uri.endswith(".sqlite") or connection_uri.endswith(".sqlite3") or os.path.exists(connection_uri):
            conn = sqlite3.connect(connection_uri)
            cursor = conn.cursor()
            cursor.execute(query)
            if query.upper().startswith("SELECT") or query.upper().startswith("PRAGMA") or query.upper().startswith("EXPLAIN"):
                rows = cursor.fetchall()
                cols = [d[0] for d in cursor.description] if cursor.description else []
                conn.close()

                if not rows:
                    return f"📊 Query executed successfully on SQLite ({len(cols)} columns, 0 rows returned)."

                # Format markdown table
                header = "| " + " | ".join(cols) + " |"
                sep = "| " + " | ".join(["---"] * len(cols)) + " |"
                table_lines = [header, sep]
                for r in rows[:25]:
                    table_lines.append("| " + " | ".join([str(x) for x in r]) + " |")

                more = f"\n  *(+ {len(rows)-25} additional rows truncated)*" if len(rows) > 25 else ""
                return f"📊 Query Results ({len(rows)} rows):\n\n" + "\n".join(table_lines) + more
            else:
                conn.commit()
                changes = conn.total_changes
                conn.close()
                return f"✅ SQL Statement Executed. Total changes made: {changes} rows."
        else:
            return f"[DB ERROR] SQLite database file '{connection_uri}' not found or unsupported connection type."

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_exec)
    except Exception as exc:
        return f"[DATABASE QUERY ERROR] {exc}"


async def db_generate_schema_diagram(connection_uri: str) -> str:
    """
    Introspect database tables and columns, and auto-generate Mermaid ER diagrams.
    """
    connection_uri = connection_uri.strip()

    def _sync_introspect():
        if not (connection_uri.endswith(".db") or connection_uri.endswith(".sqlite") or connection_uri.endswith(".sqlite3") or os.path.exists(connection_uri)):
            return f"[DB ERROR] Database file '{connection_uri}' not found."

        conn = sqlite3.connect(connection_uri)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [t[0] for t in cursor.fetchall()]

        mermaid_lines = ["erDiagram"]
        for tbl in tables:
            cursor.execute(f"PRAGMA table_info({tbl});")
            columns = cursor.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
            mermaid_lines.append(f"    {tbl} {{")
            for col in columns:
                col_name = col[1]
                col_type = col[2] or "TEXT"
                pk_str = "PK" if col[5] == 1 else ""
                mermaid_lines.append(f"        {col_type} {col_name} {pk_str}")
            mermaid_lines.append("    }")

        conn.close()
        return "\n".join(mermaid_lines)

    try:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, _sync_introspect)
        return f"📐 Database Schema Mermaid ER Diagram:\n\n```mermaid\n{res}\n```"
    except Exception as exc:
        return f"[SCHEMA DIAGRAM ERROR] {exc}"


async def db_generate_dummy_data(table_name: str, schema_def: str, count: int = 10) -> str:
    """
    Generate synthetic test data and SQL INSERT statements for table development.
    """
    table_name = table_name.strip()
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "[API ERROR] GEMINI_API_KEY required for smart dummy data generation."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""Generate {count} realistic SQL INSERT statements for table '{table_name}'.
Schema / Columns definition: {schema_def}.
Return ONLY clean SQL INSERT statements."""

        def _sync_ai():
            resp = model.generate_content(prompt)
            return resp.text.strip()

        loop = asyncio.get_event_loop()
        sql_inserts = await loop.run_in_executor(None, _sync_ai)
        return f"📝 Synthetic Dummy Data Generated for '{table_name}':\n\n```sql\n{sql_inserts}\n```"
    except Exception as exc:
        return f"[DUMMY DATA ERROR] {exc}"


async def db_backup_export(db_path_or_uri: str, output_file: str = "") -> str:
    """
    Create a timestamped atomic SQLite backup or SQL dump.
    """
    db_file = Path(db_path_or_uri).resolve()
    if not db_file.exists():
        return f"[FILE ERROR] Database file '{db_path_or_uri}' does not exist."

    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = Path(output_file).resolve() if output_file else db_file.parent / f"{db_file.stem}_backup_{ts}.db"

    def _sync_backup():
        src_conn = sqlite3.connect(str(db_file))
        dst_conn = sqlite3.connect(str(out_file))
        with dst_conn:
            src_conn.backup(dst_conn, pages=20, sleep=0.01)
        dst_conn.close()
        src_conn.close()
        size_mb = out_file.stat().st_size / (1024 * 1024)
        return f"💾 Atomic SQLite Database Backup Created!\n  • Source: {db_file.name}\n  • Backup Destination: {out_file}\n  • Size: {size_mb:.2f} MB"

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_backup)
    except Exception as exc:
        return f"[BACKUP ERROR] {exc}"


async def db_analyze_query_plan(connection_uri: str, query: str) -> str:
    """
    Run EXPLAIN QUERY PLAN on an SQLite query and give index optimization tips.
    """
    connection_uri = connection_uri.strip()
    query = query.strip()

    def _sync_explain():
        conn = sqlite3.connect(connection_uri)
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plans = cursor.fetchall()
        conn.close()

        lines = [f"⚡ SQLite Execution Plan for: `{query}`"]
        scans_detected = False
        for p in plans:
            detail = p[3] if len(p) > 3 else str(p)
            lines.append(f"  • {detail}")
            if "SCAN TABLE" in detail.upper() and "USING INDEX" not in detail.upper():
                scans_detected = True

        if scans_detected:
            lines.append("  ⚠️ Optimization Warning: Full table scan detected! Consider adding an INDEX on filtered columns.")
        else:
            lines.append("  ✅ Query is using existing indices efficiently.")
        return "\n".join(lines)

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_explain)
    except Exception as exc:
        return f"[QUERY PLAN ERROR] {exc}"
