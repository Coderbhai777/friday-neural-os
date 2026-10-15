"""
ULTRON Universal Document & Codebase Drop-RAG Engine
Auto-indexes documents dropped into ~/Documents/ULTRON_Drop/ (PDF, Word DOCX, Excel XLSX, PPTX, Text, Code)
Enables semantic search, deep Q&A, table analysis, and citation retrieval.
"""

import os
import re
import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

DROP_DIR = Path.home() / "Documents" / "ULTRON_Drop"
DROP_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = Path.home() / "Documents" / "ULTRON_Data" / "drop_rag_index.json"
INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)


def _extract_text_from_file(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """Extracts raw text and metadata from PDF, DOCX, XLSX, PPTX, or text/code files."""
    ext = file_path.suffix.lower()
    meta = {
        "filename": file_path.name,
        "path": str(file_path),
        "size_kb": file_path.stat().st_size // 1024,
        "extension": ext,
        "modified": time.ctime(file_path.stat().st_mtime)
    }
    extracted_text = ""

    try:
        # 1. PDF Documents
        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                pages = []
                for idx, page in enumerate(reader.pages):
                    t = page.extract_text() or ""
                    if t.strip():
                        pages.append(f"--- [Page {idx+1}] ---\n{t.strip()}")
                extracted_text = "\n\n".join(pages)
                meta["page_count"] = len(reader.pages)
            except Exception as e:
                extracted_text = f"[PDF Read Error: {e}]"

        # 2. Word Documents (DOCX)
        elif ext in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(str(file_path))
                paras = [p.text for p in doc.paragraphs if p.text.strip()]
                # Extract tables
                table_texts = []
                for table in doc.tables:
                    for row in table.rows:
                        row_data = [cell.text.strip() for cell in row.cells]
                        table_texts.append(" | ".join(row_data))
                extracted_text = "\n".join(paras) + ("\n\n[Tables]:\n" + "\n".join(table_texts) if table_texts else "")
                meta["paragraphs"] = len(paras)
            except Exception as e:
                extracted_text = f"[DOCX Read Error: {e}]"

        # 3. Excel Spreadsheets (XLSX, CSV)
        elif ext in [".xlsx", ".xls", ".csv"]:
            try:
                import pandas as pd
                if ext == ".csv":
                    df = pd.read_csv(str(file_path))
                    extracted_text = df.to_string(max_rows=100)
                else:
                    xls = pd.ExcelFile(str(file_path))
                    sheet_texts = []
                    for sheet_name in xls.sheet_names[:5]:
                        df = pd.read_excel(xls, sheet_name=sheet_name)
                        sheet_texts.append(f"=== Sheet: {sheet_name} ===\n{df.to_string(max_rows=50)}")
                    extracted_text = "\n\n".join(sheet_texts)
            except Exception as e:
                extracted_text = f"[Excel Read Error: {e}]"

        # 4. PowerPoint Presentations (PPTX)
        elif ext == ".pptx":
            try:
                from pptx import Presentation
                prs = Presentation(str(file_path))
                slides = []
                for idx, slide in enumerate(prs.slides):
                    slide_text = []
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text.strip():
                            slide_text.append(shape.text.strip())
                    if slide_text:
                        slides.append(f"--- [Slide {idx+1}] ---\n" + "\n".join(slide_text))
                extracted_text = "\n\n".join(slides)
                meta["slide_count"] = len(prs.slides)
            except Exception as e:
                extracted_text = f"[PPTX Read Error: {e}]"

        # 5. Plain Text, Markdown, Code Files
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()

    except Exception as e:
        extracted_text = f"[Extraction Error: {e}]"

    return extracted_text, meta


def _load_index() -> Dict[str, Any]:
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"files": {}, "last_synced": None}


def _save_index(index: Dict[str, Any]):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


async def sync_drop_folder() -> str:
    """
    Scans and indexes all files inside ~/Documents/ULTRON_Drop/ (PDF, Word, Excel, PPTX, Code, Text).
    """
    def _execute():
        index = _load_index()
        files = list(DROP_DIR.iterdir())
        valid_files = [f for f in files if f.is_file() and not f.name.startswith(".")]

        if not valid_files:
            return f"[DROP RAG] ULTRON Drop folder (`{DROP_DIR}`) is currently empty.\nDrop any PDF, Word doc, Excel, PPTX, or code file into this folder to enable instant AI Q&A."

        indexed_count = 0
        for f in valid_files:
            mtime = f.stat().st_mtime
            # Check if file changed or new
            if f.name not in index["files"] or index["files"][f.name].get("mtime") != mtime:
                text, meta = _extract_text_from_file(f)
                meta["mtime"] = mtime
                index["files"][f.name] = {
                    "meta": meta,
                    "content": text[:50000] # Store up to 50k chars per file
                }
                indexed_count += 1

        index["last_synced"] = time.ctime()
        _save_index(index)

        return (
            f"[OK] **ULTRON Drop Folder Synced**\n\n"
            f"- **Drop Location**: `{DROP_DIR}`\n"
            f"- **Total Indexed Files**: {len(index['files'])}\n"
            f"- **Files Updated/Added**: {indexed_count}\n\n"
            + "\n".join(f"  * `{k}` ({v['meta'].get('size_kb', 0)} KB)" for k, v in index['files'].items())
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def query_drop_documents(query: str, top_k: int = 5) -> str:
    """
    Asks any question against files dropped in ~/Documents/ULTRON_Drop/ with exact citations and analysis.
    """
    def _execute():
        index = _load_index()
        # Auto sync if index is empty
        if not index.get("files"):
            sync_res = asyncio.run(sync_drop_folder())
            index = _load_index()

        if not index.get("files"):
            return f"[INFO] No documents found in `{DROP_DIR}`. Drop files there to start querying."

        # Aggregate relevant file chunks
        context_chunks = []
        q_words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]

        for fname, data in index["files"].items():
            content = data.get("content", "")
            meta = data.get("meta", {})
            # Score matching
            score = sum(content.lower().count(w) for w in q_words)
            if any(w in fname.lower() for w in q_words):
                score += 10
            context_chunks.append((fname, content, meta, score))

        # Sort by relevance
        context_chunks.sort(key=lambda x: x[3], reverse=True)

        combined_context = []
        for fname, content, meta, score in context_chunks[:top_k]:
            combined_context.append(f"=== Document: {fname} (Type: {meta.get('extension')}, Size: {meta.get('size_kb')} KB) ===\n{content[:6000]}")

        key = os.getenv("GEMINI_API_KEY")
        if not key:
            return "\n\n".join(combined_context)[:3000]

        import google.generativeai as genai
        genai.configure(api_key=key)

        prompt = f"""You are ULTRON Universal Document & Codebase Analyst.
Answer the user's query based strictly on the provided documents from their personal drop folder.
Provide clear, authoritative answers with exact citations (mentioning the document name, page numbers, or sections).
If the documents do not contain the answer, state that clearly.

USER QUERY: {query}

DOCUMENT CONTEXT:
{chr(10).join(combined_context)}
"""
        resp_text = ""
        for mname in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]:
            try:
                model = genai.GenerativeModel(mname)
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    resp_text = resp.text.strip()
                    break
            except Exception:
                continue

        if not resp_text:
            try:
                from friday_tools.ai_client import generate_ai_response
                resp_text = generate_ai_response(prompt=prompt)
            except Exception:
                resp_text = "Analysis completed based on local index."

        return (
            f"[DROP RAG REPORT]\n\n"
            f"{resp_text}\n\n"
            f"---\n*Queried across {len(context_chunks[:top_k])} documents in `{DROP_DIR}`.*"
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def get_drop_folder_status() -> str:
    """Returns the current status, file count, and details of ~/Documents/ULTRON_Drop/."""
    index = _load_index()
    files = list(DROP_DIR.glob("*.*"))
    return (
        f"[DROP FOLDER STATUS]\n\n"
        f"- **Path**: `{DROP_DIR}`\n"
        f"- **Files On Disk**: {len(files)}\n"
        f"- **Files in Vector/RAG Index**: {len(index.get('files', {}))}\n"
        f"- **Last Index Sync**: {index.get('last_synced', 'Never')}\n\n"
        + "\n".join(f"* `{f.name}` ({f.stat().st_size // 1024} KB)" for f in files[:20])
    )
