"""
ULTRON Document Intelligence & PDF/Word Generator (Adapted from ULTRON-Echo)
Enables reading and extracting text from PDFs, merging PDFs, and creating formatted Word (.docx) documents.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Optional

def _extract_pdf(pdf_path: str) -> str:
    p = Path(pdf_path).expanduser().resolve()
    if not p.exists():
        return f"[ERROR] PDF file not found: {pdf_path}"

    # Try pypdf / pypdf2 / pdfplumber or fallback to basic string parser
    try:
        import pypdf
        reader = pypdf.PdfReader(str(p))
        text = []
        for idx, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                text.append(f"--- Page {idx+1} ---\n{t}")
        return "\n\n".join(text) if text else "[PDF] No readable text found in document."
    except Exception:
        pass

    try:
        import fitz # PyMuPDF
        doc = fitz.open(str(p))
        text = [f"--- Page {i+1} ---\n{page.get_text()}" for i, page in enumerate(doc)]
        return "\n\n".join(text)
    except Exception as e:
        return f"[ERROR] PDF extraction failed: {e}. Ensure pypdf or pymupdf is installed."


def _create_docx(filename: str, title: str, content: str) -> str:
    out_dir = Path.home() / "Documents" / "ULTRON_Data" / "documents"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (filename if filename.endswith(".docx") else f"{filename}.docx")

    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        
        doc = Document()
        doc.add_heading(title, 0)
        
        for para in content.split("\n\n"):
            if para.strip().startswith("# "):
                doc.add_heading(para.strip()[2:], level=1)
            elif para.strip().startswith("## "):
                doc.add_heading(para.strip()[3:], level=2)
            elif para.strip().startswith("### "):
                doc.add_heading(para.strip()[4:], level=3)
            elif para.strip().startswith("- "):
                for line in para.splitlines():
                    doc.add_paragraph(line.strip()[2:], style='List Bullet')
            else:
                doc.add_paragraph(para.strip())
                
        doc.save(str(out_path))
        return f"[OK] Created Word document: {out_path}."
    except ImportError:
        # Fallback to rich markdown / html text file
        alt_path = out_path.with_suffix(".md")
        alt_path.write_text(f"# {title}\n\n{content}", encoding="utf-8")
        return f"[OK] python-docx not installed. Saved as Markdown: {alt_path}."
    except Exception as e:
        return f"[ERROR] Could not create document: {e}"


async def extract_pdf_text(pdf_path: str) -> str:
    """Extracts all text from a PDF document."""
    return await asyncio.to_thread(_extract_pdf, pdf_path)


async def create_word_document(filename: str, title: str, content: str) -> str:
    """Creates a formatted Word (.docx) document with headers, paragraphs, and bullets."""
    return await asyncio.to_thread(_create_docx, filename, title, content)
