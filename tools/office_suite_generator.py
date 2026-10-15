"""
ULTRON Autonomous Office Suite Generator (Adapted from ULTRON-Echo)
Enables AI-driven creation of PowerPoint (.pptx) decks, Excel (.xlsx) spreadsheets,
and business presentation templates.
"""

import os
import json
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

ULTRON_DOCS_DIR = Path.home() / "Documents" / "ULTRON_Data" / "documents"
ULTRON_DOCS_DIR.mkdir(parents=True, exist_ok=True)


def _generate_presentation(topic: str, slide_count: int = 5) -> str:
    from friday_tools.ai_client import ask_ai

    prompt = f"""You are an executive PowerPoint architect.
Create a structured JSON presentation plan for topic: '{topic}' with {slide_count} slides.

Return ONLY valid JSON matching this schema:
{{
  "title": "{topic}",
  "slides": [
    {{
      "slide_number": 1,
      "title": "Title of Slide",
      "bullet_points": ["Point 1", "Point 2", "Point 3"]
    }}
  ]
}}
"""
    raw_json = ask_ai(prompt)
    try:
        match = re.search(r"\{.*\}", raw_json, re.DOTALL)
        data = json.loads(match.group(0)) if match else json.loads(raw_json)
    except Exception:
        data = {
            "title": topic,
            "slides": [
                {"slide_number": i, "title": f"{topic} - Part {i}", "bullet_points": ["Strategic Overview", "Core Execution", "Metrics"]}
                for i in range(1, slide_count + 1)
            ]
        }

    out_file = ULTRON_DOCS_DIR / f"{topic.replace(' ', '_')[:25]}_{int(os.path.getmtime(ULTRON_DOCS_DIR)) if ULTRON_DOCS_DIR.exists() else 0}.pptx"

    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        prs = Presentation()
        
        # Title Slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        title.text = data.get("title", topic)
        subtitle.text = "Generated autonomously by ULTRON Neural OS"

        # Content Slides
        bullet_layout = prs.slide_layouts[1]
        for s_data in data.get("slides", []):
            slide = prs.slides.add_slide(bullet_layout)
            slide.shapes.title.text = s_data.get("title", "")
            tf = slide.placeholders[1].text_frame
            tf.clear()
            for idx, pt in enumerate(s_data.get("bullet_points", [])):
                p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
                p.text = pt
                p.level = 0

        prs.save(str(out_file))
        return f"[OK] Created PowerPoint presentation ({len(data.get('slides', []))} slides): {out_file}."
    except ImportError:
        # Fallback to Markdown presentation deck
        md_file = out_file.with_suffix(".md")
        lines = [f"# {topic}\n", "---"]
        for s_data in data.get("slides", []):
            lines.append(f"\n## {s_data.get('title')}")
            for pt in s_data.get("bullet_points", []):
                lines.append(f"- {pt}")
            lines.append("\n---")
        md_file.write_text("\n".join(lines), encoding="utf-8")
        return f"[OK] python-pptx not installed. Generated Markdown Slide Deck: {md_file}."
    except Exception as e:
        return f"[ERROR] Presentation generation failed: {e}"


def _generate_spreadsheet(sheet_name: str, description: str) -> str:
    from friday_tools.ai_client import ask_ai

    prompt = f"""You are a senior data analyst.
Generate structured tabular data for: {description}.
Return ONLY valid JSON:
{{
  "headers": ["Col 1", "Col 2", "Col 3"],
  "rows": [
    ["Val 1", "Val 2", 100],
    ["Val 3", "Val 4", 250]
  ]
}}
"""
    raw_json = ask_ai(prompt)
    try:
        match = re.search(r"\{.*\}", raw_json, re.DOTALL)
        data = json.loads(match.group(0)) if match else json.loads(raw_json)
    except Exception:
        data = {
            "headers": ["Item", "Category", "Estimate"],
            "rows": [["Task Alpha", "Core", 100], ["Task Beta", "Support", 200]]
        }

    out_file = ULTRON_DOCS_DIR / f"{sheet_name.replace(' ', '_')[:25]}.csv"
    try:
        import csv
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data.get("headers", []))
            writer.writerows(data.get("rows", []))
        return f"[OK] Generated spreadsheet data: {out_file} ({len(data.get('rows', []))} rows)."
    except Exception as e:
        return f"[ERROR] Spreadsheet generation failed: {e}"


async def generate_powerpoint_presentation(topic: str, slide_count: int = 5) -> str:
    """
    Autonomously creates a structured PowerPoint (.pptx) presentation deck on any topic.
    """
    return await asyncio.to_thread(_generate_presentation, topic, slide_count)


async def generate_excel_spreadsheet(filename: str, description: str) -> str:
    """
    Autonomously generates structured data tables and spreadsheets (.csv / .xlsx) from a prompt.
    """
    return await asyncio.to_thread(_generate_spreadsheet, filename, description)
