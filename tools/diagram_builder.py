"""
ULTRON Architecture & Diagram Builder Engine
Generates, renders, and opens interactive Mermaid.js diagrams (Flowcharts, Sequence, Class, ER, State, Gantt) in dark-mode HTML/SVG.
"""

import os
import re
import json
import time
import asyncio
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

DIAGRAM_DIR = Path.home() / "Documents" / "ULTRON_Data" / "diagrams"
DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - ULTRON Neural Visualizer</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: #0b0f19;
            color: #00f0ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }}
        .header {{
            width: 100%;
            max-width: 1200px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 240, 255, 0.2);
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
        }}
        .badge {{
            background: rgba(0, 240, 255, 0.1);
            border: 1px solid #00f0ff;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 12px;
            letter-spacing: 1px;
        }}
        .diagram-container {{
            width: 100%;
            max-width: 1200px;
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            overflow: auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .controls {{
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }}
        button {{
            background: #1f2937;
            color: #00f0ff;
            border: 1px solid #00f0ff;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
        }}
        button:hover {{
            background: #00f0ff;
            color: #0b0f19;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
        }}
        pre.source {{
            width: 100%;
            max-width: 1200px;
            background: #05070d;
            border: 1px solid #1f2937;
            border-radius: 6px;
            padding: 15px;
            color: #94a3b8;
            font-size: 13px;
            margin-top: 20px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="badge">ULTRON DIAGRAM ENGINE v2.0</div>
    </div>
    <div class="diagram-container" id="container">
        <pre class="mermaid" id="diagram">
{mermaid_code}
        </pre>
    </div>
    <div class="controls">
        <button onclick="window.print()">🖨️ Print / Export PDF</button>
        <button onclick="navigator.clipboard.writeText(document.getElementById('raw-code').innerText); alert('Mermaid code copied to clipboard!')">📋 Copy Source</button>
    </div>
    <pre class="source" id="raw-code">
{mermaid_code}
    </pre>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#00f0ff',
                primaryTextColor: '#ffffff',
                primaryBorderColor: '#00f0ff',
                lineColor: '#38bdf8',
                secondaryColor: '#ec4899',
                tertiaryColor: '#8b5cf6'
            }}
        }});
    </script>
</body>
</html>
"""


async def build_mermaid_diagram(
    prompt: str,
    diagram_type: str = "auto",
    title: str = "",
    auto_open: bool = True
) -> str:
    """
    Generates an architectural, sequence, flowchart, state, or database ER diagram from text prompt and opens it in an interactive browser viewer.
    """
    def _execute():
        system_prompt = f"""You are ULTRON System Architect & Visualization Engine.
Generate high-fidelity, syntactically perfect Mermaid.js diagram code based on this request:
REQUEST: {prompt}
SPECIFIED DIAGRAM TYPE: {diagram_type}

RULES:
1. Return ONLY the raw Mermaid code block (e.g. `sequenceDiagram`, `flowchart TD`, `classDiagram`, `erDiagram`, `stateDiagram-v2`, `gantt`).
2. Wrap node labels with special characters or spaces in double quotes (e.g., id1["API Gateway (FastAPI)"]).
3. Ensure crisp layout, clear actor names, arrows, and logical data flow.
4. Do NOT output explanations or preamble. Return only the Mermaid diagram syntax.
"""
        raw = ""
        key = os.getenv("GEMINI_API_KEY")
        if key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=key)
                for mname in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]:
                    try:
                        model = genai.GenerativeModel(mname)
                        resp = model.generate_content(system_prompt)
                        if resp and resp.text:
                            raw = resp.text.strip()
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        if not raw:
            try:
                from friday_tools.ai_client import generate_ai_response
                raw = generate_ai_response(prompt=system_prompt)
            except Exception:
                pass

        # Clean code fences
        clean_mermaid = re.sub(r"^```(?:mermaid)?\s*", "", raw)
        clean_mermaid = re.sub(r"\s*```$", "", clean_mermaid).strip()

        diagram_title = title or (re.sub(r"[^a-zA-Z0-9_\s]", "", prompt)[:40].strip() or "System Architecture")
        safe_fname = re.sub(r"[^a-zA-Z0-9_\-]", "_", diagram_title)[:40].strip("_")
        out_file = DIAGRAM_DIR / f"{safe_fname}_{int(time.time())}.html"

        html_content = HTML_TEMPLATE.format(
            title=diagram_title,
            mermaid_code=clean_mermaid
        )

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        if auto_open:
            webbrowser.open(f"file:///{out_file}")

        return (
            f"# [DIAGRAM] ULTRON Diagram Generated: '{diagram_title}'\n\n"
            f"```mermaid\n{clean_mermaid}\n```\n\n"
            f"[HTML VIEWER] **Interactive HTML Viewer**: `{out_file}`\n"
            f"*(Opened in default browser)*"
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def render_and_open_diagram(mermaid_code: str, title: str = "Custom Diagram") -> str:
    """
    Renders existing raw Mermaid diagram code into an interactive HTML viewer and opens it.
    """
    def _execute():
        clean_code = re.sub(r"^```(?:mermaid)?\s*", "", mermaid_code)
        clean_code = re.sub(r"\s*```$", "", clean_code).strip()
        safe_fname = re.sub(r"[^a-zA-Z0-9_\-]", "_", title)[:40].strip("_") or "diagram"
        out_file = DIAGRAM_DIR / f"{safe_fname}_{int(time.time())}.html"

        html_content = HTML_TEMPLATE.format(
            title=title,
            mermaid_code=clean_code
        )

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        webbrowser.open(f"file:///{out_file}")
        return f"[OK] Opened diagram '{title}' in interactive viewer: {out_file}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)
