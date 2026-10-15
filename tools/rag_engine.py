"""
ULTRON Smart RAG Engine (Personal Document Search & QA)
Indexes PDFs, DOCX, TXT, MD, Python, and code files locally into SQLite.
Provides semantic retrieval and question-answering with citation.
"""

import os
import re
import math
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# RAG Storage Location
RAG_DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)
RAG_DOCS_DIR = Path.home() / "Documents" / "ULTRON_Docs"
RAG_DOCS_DIR.mkdir(parents=True, exist_ok=True)
RAG_DB_PATH = RAG_DATA_DIR / "ultron_rag.db"


def _get_db():
    conn = sqlite3.connect(str(RAG_DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE,
            file_name TEXT,
            file_type TEXT,
            file_size INTEGER,
            indexed_at TEXT,
            chunk_count INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER,
            file_name TEXT,
            file_path TEXT,
            chunk_index INTEGER,
            content TEXT,
            FOREIGN KEY (doc_id) REFERENCES documents (id) ON DELETE CASCADE
        )
    """)
    return conn


def _clean_watermarks(text: str) -> str:
    """Strips mobile scanner watermark noise (AnyScanner, CamScanner, etc.)."""
    lines = []
    watermark_patterns = [
        r"^anyscanner\b", r"^camscanner\b", r"^scanned\s+with\b", r"^adobe\s+scan\b",
        r"^page\s+\d+\s+of\s+\d+$", r"^wps\s+office\b"
    ]
    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        if any(re.search(pat, line_clean, re.IGNORECASE) for pat in watermark_patterns):
            continue
        lines.append(line)
    return "\n".join(lines)


def _ocr_scanned_pdf(file_path: str) -> str:
    """Performs parallel neural OCR on scanned PDF pages using PyMuPDF and Gemini Flash Vision."""
    try:
        import io
        import pymupdf
        from PIL import Image
        import google.generativeai as genai
        import concurrent.futures

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return ""

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        doc = pymupdf.open(file_path)
        prompt = (
            "Extract all handwritten, printed, Devanagari, Marathi, Hindi, and English text from this textbook or worksheet page accurately.\n"
            "IGNORE all scanner watermarks like 'Any Scanner', 'CamScanner', mobile shadows, or border artifacts.\n"
            "Preserve all chapter headings, story passages, poems, questions, grammar exercises, and numbered items cleanly."
        )

        def _process_page(page_idx):
            try:
                page = doc[page_idx]
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                if img.width > 1400:
                    ratio = 1400 / img.width
                    img = img.resize((1400, int(img.height * ratio)), Image.Resampling.LANCZOS)
                
                resp = model.generate_content([prompt, img])
                if resp and resp.text:
                    cleaned_page = _clean_watermarks(resp.text.strip())
                    if cleaned_page:
                        return page_idx, f"--- [Page {page_idx+1}] ---\n{cleaned_page}"
            except Exception:
                pass
            return page_idx, ""

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(_process_page, range(len(doc))))

        results.sort(key=lambda x: x[0])
        extracted_pages = [text for _, text in results if text]
        return "\n\n".join(extracted_pages)
    except Exception as e:
        return f"Scanned OCR error: {e}"


def _ocr_image_file(file_path: str) -> str:
    """Performs neural OCR directly on an image file (PNG/JPG/JPEG)."""
    try:
        from PIL import Image
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return ""

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        img = Image.open(file_path)
        if img.width > 1600:
            ratio = 1600 / img.width
            img = img.resize((1600, int(img.height * ratio)), Image.Resampling.LANCZOS)

        prompt = (
            "Extract all Devanagari, Marathi, Hindi, and English text from this document image accurately.\n"
            "Ignore scanner watermarks, phone borders, or camera glare. Format headings and questions cleanly."
        )
        resp = model.generate_content([prompt, img])
        return _clean_watermarks(resp.text.strip()) if resp and resp.text else ""
    except Exception:
        return ""


def _extract_text(file_path: str) -> str:
    """Extracts raw text from text files, DOCX, digital PDFs, scanned AnyScanner PDFs, and images."""
    p = Path(file_path)
    if not p.exists():
        return ""

    ext = p.suffix.lower()

    # Plain text / Code / Markdown
    if ext in ('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.csv', '.cpp', '.c', '.h', '.bat', '.ps1', '.sql'):
        try:
            return p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    # Direct Images (JPG, PNG, WEBP, JPEG)
    if ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp'):
        return _ocr_image_file(str(p))

    # PDF documents (Digital + Scanned AnyScanner support)
    if ext == '.pdf':
        digital_text = ""
        total_pages = 1
        try:
            import pymupdf
            doc = pymupdf.open(str(p))
            total_pages = max(1, len(doc))
            text_parts = [page.get_text() for page in doc]
            digital_text = _clean_watermarks("\n".join(text_parts)).strip()
        except Exception:
            try:
                import pypdf
                reader = pypdf.PdfReader(str(p))
                total_pages = max(1, len(reader.pages))
                text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
                digital_text = _clean_watermarks("\n".join(text_parts)).strip()
            except Exception:
                pass

        # If digital text exists and has substantial content (> 35 chars per page)
        if len(digital_text) > (total_pages * 35):
            return digital_text

        # Otherwise, this is a scanned document (AnyScanner, CamScanner, photo) -> run Neural OCR
        return _ocr_scanned_pdf(str(p))

    # Word documents (.docx)
    if ext == '.docx':
        try:
            import docx
            doc = docx.Document(str(p))
            return "\n".join([para.text for para in doc.paragraphs if para.text])
        except Exception as e:
            return f"DOCX extract error: {e}"

    return ""


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    """Splits text into overlapping chunks."""
    words = text.split()
    if not words:
        return []
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def _tokenize(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r'\w+', text) if len(w) > 1]


def _bm25_score(query_tokens: List[str], chunk_tokens: List[str], avg_doc_len: float, k1: float = 1.5, b: float = 0.75) -> float:
    """Calculates BM25 relevance score."""
    if not chunk_tokens:
        return 0.0
    doc_len = len(chunk_tokens)
    score = 0.0
    freq_map = {}
    for t in chunk_tokens:
        freq_map[t] = freq_map.get(t, 0) + 1

    for q in query_tokens:
        f = freq_map.get(q, 0)
        if f > 0:
            numerator = f * (k1 + 1)
            denominator = f + k1 * (1 - b + b * (doc_len / (avg_doc_len or 1.0)))
            score += numerator / denominator
    return score


# =========================================================
# PUBLIC RAG TOOLS
# =========================================================

async def rag_index_file(file_path: str) -> str:
    """Indexes a single document (PDF, DOCX, TXT, MD, Code) into Ultron's RAG knowledge base."""
    p = Path(file_path)
    if not p.exists():
        return f"❌ File not found: {file_path}"

    text = _extract_text(str(p))
    if not text.strip():
        return f"⚠️ No extractable text found in {p.name}"

    chunks = _chunk_text(text)
    conn = _get_db()
    cursor = conn.cursor()

    # Clean old entry if exists
    cursor.execute("SELECT id FROM documents WHERE file_path = ?", (str(p),))
    existing = cursor.fetchone()
    if existing:
        doc_id = existing[0]
        cursor.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

    # Insert new document
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
        INSERT INTO documents (file_path, file_name, file_type, file_size, indexed_at, chunk_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (str(p), p.name, p.suffix.lower(), p.stat().st_size, now, len(chunks)))
    doc_id = cursor.lastrowid

    # Insert chunks
    for idx, c in enumerate(chunks):
        cursor.execute("""
            INSERT INTO chunks (doc_id, file_name, file_path, chunk_index, content)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_id, p.name, str(p), idx, c))

    conn.commit()
    conn.close()
    return f"✅ Indexed document '{p.name}' ({len(chunks)} chunks, {len(text.split())} words)."


async def rag_index_folder(folder_path: str = "") -> str:
    """Indexes all documents in a folder into Ultron's RAG knowledge base."""
    target_dir = Path(folder_path) if folder_path else RAG_DOCS_DIR
    if not target_dir.exists():
        return f"❌ Folder does not exist: {target_dir}"

    valid_exts = {'.pdf', '.docx', '.txt', '.md', '.py', '.js', '.html', '.json', '.csv', '.cpp', '.sql'}
    indexed_count = 0
    total_chunks = 0

    for root, _, files in os.walk(str(target_dir)):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in valid_exts and not p.name.startswith('.'):
                res = await rag_index_file(str(p))
                if "Indexed" in res:
                    indexed_count += 1

    return f"📚 Indexed {indexed_count} documents from '{target_dir.name}' into RAG knowledge base."


async def rag_search_documents(query: str, top_k: int = 3) -> str:
    """Searches indexed personal documents and returns the top relevant excerpts."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name, file_path, chunk_index, content FROM chunks")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "ℹ️ No documents indexed yet. Use rag_index_folder or put files in '~/Documents/ULTRON_Docs'."

    query_tokens = _tokenize(query)
    if not query_tokens:
        return "Please provide a search query."

    avg_len = sum(len(_tokenize(r[4])) for r in rows) / len(rows)

    scored = []
    for r in rows:
        chunk_tokens = _tokenize(r[4])
        score = _bm25_score(query_tokens, chunk_tokens, avg_len)
        if score > 0.1:
            scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_results = scored[:top_k]

    if not top_results:
        return f"🔍 No relevant matches found in documents for query: '{query}'"

    output = [f"📄 Found {len(top_results)} relevant document sections for '{query}':\n"]
    for rank, (score, r) in enumerate(top_results, 1):
        file_name = r[1]
        chunk_idx = r[3]
        content = r[4]
        output.append(f"--- [Match {rank}: {file_name} (Section {chunk_idx})] ---")
        output.append(content[:400] + ("..." if len(content) > 400 else ""))
        output.append("")

    return "\n".join(output)


async def rag_ask_documents(question: str, folder_path: str = "") -> str:
    """
    Asks a question across all your indexed documents.
    Retrieves relevant document context and answers using Ultron's dual AI inference engine.
    """
    # If folder passed, index it first
    if folder_path and os.path.exists(folder_path):
        await rag_index_folder(folder_path)

    context_search = await rag_search_documents(question, top_k=4)

    if "No relevant matches" in context_search or "No documents indexed" in context_search:
        # Fallback to direct AI answer
        from friday_tools.ai_client import generate_ai_response
        return generate_ai_response(question)

    prompt = f"""
You are Ultron, answering a question using the user's indexed personal documents.

CONTEXT FROM USER'S DOCUMENTS:
{context_search}

QUESTION:
{question}

INSTRUCTIONS:
- Answer accurately based on the provided document context.
- Cite the document name(s) you found the answer in.
- If the document context doesn't contain the full answer, state what was found in the documents and add any helpful general knowledge.
"""
    from friday_tools.ai_client import generate_ai_response
    answer = generate_ai_response(prompt)
    return f"📖 **Document Knowledge Result**:\n\n{answer}\n\n*(Sources retrieved from personal document index)*"


async def rag_list_indexed_docs() -> str:
    """Lists all files currently indexed in Ultron's RAG knowledge base."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_name, file_type, file_size, chunk_count, indexed_at, file_path FROM documents")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"📂 Document index is empty.\nDrop documents into: {RAG_DOCS_DIR}\nThen run: rag_index_folder"

    lines = [f"📚 **Indexed Documents in Ultron RAG ({len(rows)} files)**:\n"]
    for r in rows:
        size_kb = r[2] / 1024
        lines.append(f"• **{r[0]}** ({r[1]}, {size_kb:.1f} KB) — {r[3]} chunks [Indexed: {r[4]}]")

    lines.append(f"\n📁 Dedicated Folder: `{RAG_DOCS_DIR}`")
    return "\n".join(lines)
