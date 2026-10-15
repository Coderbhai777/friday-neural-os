"""
ULTRON Autonomous Code Execution Sandbox & Self-Healing Auto-Debugger
Safely runs code across multiple runtimes and automatically fixes errors until success.
"""

import os
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
CODE_DIR = Path.home() / "Documents" / "ULTRON_Code"
CODE_DIR.mkdir(parents=True, exist_ok=True)


def _get_gemini_model():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv(DATA_DIR / ".env")
        api_key = os.getenv("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def _run_process(cmd: list, timeout: int = 30, cwd: str = None) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            encoding='utf-8',
            errors='replace'
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Execution timed out after {timeout} seconds."
    except Exception as e:
        return -2, "", str(e)


async def run_code(code: str, language: str = "python", timeout: int = 30) -> str:
    """
    Executes a code snippet or script in Python, JavaScript/Node, PowerShell, or Bash.
    """
    lang = language.lower().strip()
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        if lang in ["python", "py"]:
            file_path = tmp_path / "script.py"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = [sys.executable, str(file_path)]
            
        elif lang in ["javascript", "js", "node"]:
            file_path = tmp_path / "script.js"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = ["node", str(file_path)]
            
        elif lang in ["powershell", "ps1", "ps"]:
            file_path = tmp_path / "script.ps1"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(file_path)]
            
        elif lang in ["batch", "cmd", "bat"]:
            file_path = tmp_path / "script.bat"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = ["cmd", "/c", str(file_path)]
            
        else:
            return f"Unsupported language: {language}. Supported: python, javascript, powershell, batch."
            
        code_ret, stdout, stderr = _run_process(cmd, timeout=timeout)
        
        output = []
        if stdout:
            output.append(f"[STDOUT]:\n{stdout}")
        if stderr:
            output.append(f"[STDERR]:\n{stderr}")
        if code_ret != 0:
            output.append(f"[EXIT CODE]: {code_ret}")
        else:
            output.append("[STATUS]: Success (Exit 0)")
            
        return "\n".join(output) if output else "[Process completed with empty output]"


async def execute_and_auto_debug(code: str, language: str = "python", max_retries: int = 3) -> str:
    """
    Autonomous Self-Healing Execution Loop:
    Executes code, inspects runtime tracebacks / errors, automatically generates the fix with AI,
    and re-runs until successful or until max_retries is reached.
    """
    current_code = code
    attempt_logs = []
    
    for attempt in range(1, max_retries + 1):
        attempt_logs.append(f"--- ATTEMPT {attempt}/{max_retries} ---")
        res_output = await run_code(current_code, language=language)
        
        # Check if succeeded
        if "[EXIT CODE]" not in res_output and "[STDERR]:" not in res_output:
            attempt_logs.append(f"[RESULT]: Success!\n{res_output}")
            
            # Save the successful script
            save_file = CODE_DIR / f"self_healed_{int(time.time())}.py"
            with open(save_file, "w", encoding="utf-8") as f:
                f.write(current_code)
                
            return f"✅ Code Executed Successfully (Fixed in {attempt} attempt(s)):\n\n{res_output}\n\n[Saved to]: {save_file}"
            
        attempt_logs.append(f"[ERROR ENCOUNTERED]:\n{res_output}")
        
        # If last attempt, finish
        if attempt == max_retries:
            break
            
        # Self-Healing: ask AI to diagnose and rewrite
        prompt = f"""You are an Autonomous Software Engineer and Bugfixer.
The following {language} code failed during execution:

FAILED CODE:
```
{current_code}
```

RUNTIME ERROR / TRACEBACK:
```
{res_output}
```

Diagnose the exact root cause and return ONLY the completely corrected, executable {language} code inside ```{language} ... ``` blocks. Do not explain, just return the working code."""

        try:
            model = _get_gemini_model()
            fix_resp = model.generate_content(prompt).text
            # Extract code block
            import re
            m = re.search(r'```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```', fix_resp, re.DOTALL)
            if m:
                current_code = m.group(1)
            else:
                current_code = fix_resp.strip()
            attempt_logs.append(f"[AI AUTO-FIX APPLIED]: Retrying execution...")
        except Exception as e:
            attempt_logs.append(f"[AI Fix Error]: {e}")
            break
            
    return "❌ Self-Healing Failed after retries:\n\n" + "\n\n".join(attempt_logs)


async def scaffold_project(project_type: str, project_name: str, target_dir: str = "") -> str:
    """
    Scaffolds complete multi-file starter templates (FastAPI, React, Flask, CLI, Automation).
    """
    dest_path = Path(target_dir) if target_dir else (CODE_DIR / project_name)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    ptype = project_type.lower().strip()
    
    if "fastapi" in ptype or "api" in ptype:
        (dest_path / "main.py").write_text("""from fastapi import FastAPI\n\napp = FastAPI(title="Generated API")\n\n@app.get("/")\ndef home():\n    return {"status": "online", "message": "ULTRON Scaffold Active"}\n""", encoding="utf-8")
        (dest_path / "requirements.txt").write_text("fastapi\nuvicorn\npydantic\n", encoding="utf-8")
        (dest_path / "README.md").write_text(f"# {project_name}\nFastAPI project generated by ULTRON.", encoding="utf-8")
        
    elif "react" in ptype or "web" in ptype:
        (dest_path / "index.html").write_text(f"""<!DOCTYPE html>\n<html>\n<head><title>{project_name}</title><script src="https://cdn.tailwindcss.com"></script></head>\n<body class="bg-slate-900 text-white flex items-center justify-center min-h-screen">\n<h1 class="text-3xl font-bold text-amber-400">{project_name}</h1>\n</body>\n</html>""", encoding="utf-8")
        (dest_path / "app.js").write_text("console.log('App initialized.');", encoding="utf-8")
        
    else:
        (dest_path / "app.py").write_text(f"# {project_name}\ndef main():\n    print('Running {project_name}')\n\nif __name__ == '__main__':\n    main()\n", encoding="utf-8")
        
    return f"Project '{project_name}' ({project_type}) scaffolded at: {dest_path}"
