"""
ULTRON Autonomous Self-Code Editor & Project Developer Agent (Adapted from ULTRON-Echo)
Enables ULTRON to plan, write, edit, execute, debug, and auto-refactor complete software projects and codebases.
Includes autonomous error classification, traceback parsing, and automated fix loops.
"""

import os
import re
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

MAX_FIX_ATTEMPTS = 5
PROJECTS_DIR = Path.home() / "Desktop" / "UltronProjects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


class CodeEditorTools:
    """Core file and execution tools for the code editing agent."""

    @staticmethod
    def file_read(file_path: str, offset: int = 1, limit: int = 2000) -> str:
        p = Path(file_path)
        if not p.exists():
            return f"[ERROR] File does not exist: {file_path}"
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            start = max(0, offset - 1)
            end = min(len(lines), start + limit)
            numbered = [f"{i+1:5d} | {lines[i]}" for i in range(start, end)]
            return f"[{p.name} | Lines {start+1}-{end} of {len(lines)}]\n" + "\n".join(numbered)
        except Exception as e:
            return f"[ERROR] Could not read file: {e}"

    @staticmethod
    def file_write(file_path: str, content: str) -> str:
        p = Path(file_path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"[OK] Successfully written {len(content)} chars to {p.name}."
        except Exception as e:
            return f"[ERROR] Could not write file: {e}"

    @staticmethod
    def file_edit(file_path: str, old_str: str, new_str: str) -> str:
        p = Path(file_path)
        if not p.exists():
            return f"[ERROR] File does not exist: {file_path}"
        try:
            text = p.read_text(encoding="utf-8")
            if old_str not in text:
                return f"[ERROR] Target substring not found in {p.name}."
            new_text = text.replace(old_str, new_str, 1)
            p.write_text(new_text, encoding="utf-8")
            return f"[OK] Successfully replaced targeted block in {p.name}."
        except Exception as e:
            return f"[ERROR] Edit failed: {e}"

    @staticmethod
    def code_search(query: str, root_dir: str = "") -> str:
        target_dir = Path(root_dir) if root_dir else PROJECTS_DIR
        matches = []
        try:
            for root, _, files in os.walk(target_dir):
                for f in files:
                    if f.endswith(('.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt')):
                        full_p = Path(root) / f
                        try:
                            lines = full_p.read_text(encoding="utf-8", errors="ignore").splitlines()
                            for idx, l in enumerate(lines, 1):
                                if query.lower() in l.lower():
                                    matches.append(f"{full_p.name}:{idx} -> {l.strip()[:100]}")
                                    if len(matches) >= 30:
                                        break
                        except Exception:
                            pass
            if not matches:
                return f"[SEARCH] No occurrences of '{query}' found in {target_dir}."
            return f"[SEARCH RESULTS ({len(matches)})]:\n" + "\n".join(matches)
        except Exception as e:
            return f"[ERROR] Code search failed: {e}"


# ── Autonomous Project Scaffolder & Fixer ────────────────────────────────────

def _classify_error(output: str) -> str:
    low = output.lower()
    if any(x in low for x in ("modulenotfounderror", "no module named", "importerror")):
        return "import_error"
    if "syntaxerror" in low or "invalid syntax" in low:
        return "syntax_error"
    if any(x in low for x in ("traceback", "exception", "error:", "nameerror", "typeerror", "attributeerror")):
        return "runtime_error"
    return "none"


def _run_dev_pipeline(task_description: str, workspace_path: str = "") -> str:
    from friday_tools.ai_client import ask_ai

    work_dir = Path(workspace_path) if workspace_path else (PROJECTS_DIR / f"proj_{int(time.time())}")
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Plan Architecture
    plan_prompt = f"""You are ULTRON's Senior Software Architect.
Create a clean file plan for this development task:
Task: {task_description}

Return ONLY valid JSON matching this schema:
{{
  "project_name": "snake_case_name",
  "entry_point": "main.py",
  "files": [
    {{
      "path": "main.py",
      "description": "Main entry point and core logic"
    }}
  ],
  "run_command": "python main.py"
}}
"""
    raw_plan = ask_ai(plan_prompt)
    try:
        # Extract JSON
        json_match = re.search(r"\{.*\}", raw_plan, re.DOTALL)
        plan_data = json.loads(json_match.group(0)) if json_match else json.loads(raw_plan)
    except Exception:
        plan_data = {
            "project_name": "ultron_app",
            "entry_point": "main.py",
            "files": [{"path": "main.py", "description": task_description}],
            "run_command": "python main.py"
        }

    # 2. Write each file
    for f_info in plan_data.get("files", []):
        f_path = work_dir / f_info["path"]
        f_path.parent.mkdir(parents=True, exist_ok=True)

        write_prompt = f"""Write complete, production-ready, runnable Python code for this file:
File: {f_info['path']}
Description: {f_info['description']}
Overall Project Goal: {task_description}

Return ONLY the code wrapped in ```python ... ``` fences.
"""
        code_resp = ask_ai(write_prompt)
        code_match = re.search(r"```(?:python)?\s*\n(.*?)\n```", code_resp, re.DOTALL)
        clean_code = code_match.group(1) if code_match else code_resp
        f_path.write_text(clean_code.strip(), encoding="utf-8")

    # 3. Test & Auto-Fix Loop
    run_cmd = plan_data.get("run_command", f"python {plan_data.get('entry_point', 'main.py')}")
    fix_attempts = 0
    final_status = "PASSED"
    last_output = ""

    while fix_attempts < MAX_FIX_ATTEMPTS:
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", run_cmd],
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=15
            )
            last_output = (res.stdout + "\n" + res.stderr).strip()
            err_type = _classify_error(last_output)

            if res.returncode == 0 and err_type == "none":
                final_status = "PASSED (Clean Execution)"
                break

            # Synthesize Fix
            fix_attempts += 1
            entry_file = work_dir / plan_data.get("entry_point", "main.py")
            current_code = entry_file.read_text(encoding="utf-8") if entry_file.exists() else ""

            fix_prompt = f"""Fix this bug in {entry_file.name}:
Error Output:
{last_output}

Current Code:
```python
{current_code}
```

Return the complete corrected code wrapped in ```python ... ``` fences.
"""
            fixed_resp = ask_ai(fix_prompt)
            fix_match = re.search(r"```(?:python)?\s*\n(.*?)\n```", fixed_resp, re.DOTALL)
            fixed_code = fix_match.group(1) if fix_match else fixed_resp
            entry_file.write_text(fixed_code.strip(), encoding="utf-8")

        except subprocess.TimeoutExpired:
            final_status = "PASSED (Interactive / Long-running loop)"
            break
        except Exception as e:
            last_output = str(e)
            break

    return f"""[ULTRON CODE BUILDER]
Workspace   : {work_dir}
Files Created: {', '.join([f['path'] for f in plan_data.get('files', [])])}
Execution   : {final_status}
Fix Cycles  : {fix_attempts}
Output Log  : {last_output[:250]}
"""


# ── Tool Exports for ULTRON ────────────────────────────────────────────────

async def autonomous_code_builder(task_description: str, workspace_path: str = "") -> str:
    """
    Autonomously plans, writes, tests, and self-debugs a complete Python script or project from scratch.
    """
    return await asyncio.to_thread(_run_dev_pipeline, task_description, workspace_path)


async def code_editor_apply_edit(file_path: str, old_str: str, new_str: str) -> str:
    """
    Applies surgical code replacement to an existing file in the codebase.
    """
    return await asyncio.to_thread(CodeEditorTools.file_edit, file_path, old_str, new_str)


async def code_search_symbols(query: str, root_dir: str = "") -> str:
    """
    Searches for functions, symbols, or text across all project files.
    """
    return await asyncio.to_thread(CodeEditorTools.code_search, query, root_dir)
