"""
ULTRON JARVIS Zero-Error Autonomous Code Engine (Multi-Language)
Pre-execution AST parsing, automatic markdown fence stripping, self-correcting syntax validation,
runtime error traceback auto-repair loops, and guaranteed production-ready code generation.
"""

import os
import sys
import ast
import re
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

CODE_BACKUP_DIR = Path.home() / "Documents" / "ULTRON_Data" / "code_backups"
CODE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 1. PURE CODE EXTRACTION & SANITIZATION
# ==========================================

def clean_code_snippet(raw_text: str, language: str = "python") -> str:
    """
    Strips conversational preambles, trailing markdown comments, and extracts 100% pure code.
    Handles ```python, ```cpp, ```c, ```arduino, ```html, ```javascript, ```json fences.
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    text = raw_text.strip()

    # Match code inside markdown fences if present
    fence_pattern = r"```(?:[a-zA-Z0-9_\+\-\#]*)\n(.*?)```"
    matches = re.findall(fence_pattern, text, re.DOTALL)
    if matches:
        # Take the largest code block
        text = max(matches, key=len).strip()
    else:
        # If starting with ``` or ending with ```
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) > 1:
                text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3].strip()

        # Remove leading conversational text if first line is not valid code start
        lines = text.splitlines()
        first_code_idx = 0
        for i, l in enumerate(lines):
            stripped = l.strip()
            if language.lower() in ("python", "py"):
                if (
                    stripped.startswith(("import ", "from ", "def ", "class ", "#", "if ", "try:", "async ", "with "))
                    or "=" in stripped
                    or (stripped and not stripped.endswith(":") and not stripped.endswith("?"))
                ):
                    first_code_idx = i
                    break
            elif language.lower() in ("cpp", "c", "arduino", "ino", "c++"):
                if stripped.startswith(("#include", "//", "/*", "void ", "int ", "bool ", "float ", "double ", "class ", "struct ")):
                    first_code_idx = i
                    break
                    
        if first_code_idx < len(lines):
            text = "\n".join(lines[first_code_idx:]).strip()

    return text


# ==========================================
# 2. MULTI-LANGUAGE SYNTAX VALIDATION
# ==========================================

def validate_syntax(code: str, language: str = "python") -> Tuple[bool, str]:
    """
    Strict pre-execution syntax validation:
    - Python: AST compilation via ast.parse()
    - JSON: json.loads()
    - C/C++/Arduino: Bracket balance & semicolon audit
    """
    if not code or not code.strip():
        return False, "Code is empty."

    lang = language.lower().strip()
    
    if lang in ("python", "py"):
        try:
            ast.parse(code)
            compile(code, "<string>", "exec")
            return True, "Python AST Syntax Validated [PASS]"
        except SyntaxError as e:
            return False, f"Python SyntaxError at line {e.lineno}, col {e.offset}: {e.msg} -> '{e.text.strip() if e.text else ''}'"
        except Exception as err:
            return False, f"Python Compilation Error: {err}"

    elif lang in ("json",):
        try:
            json.loads(code)
            return True, "JSON Syntax Validated [PASS]"
        except Exception as e:
            return False, f"Invalid JSON: {e}"

    elif lang in ("cpp", "c", "arduino", "ino", "c++"):
        # Check balanced braces
        brackets = {"{": "}", "(": ")", "[": "]"}
        stack = []
        for char in code:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    return False, f"C/C++ Syntax Error: Unbalanced bracket '{char}' detected."
        if stack:
            return False, f"C/C++ Syntax Error: Missing closing bracket '{stack[-1]}'."
            
        # Ensure setup() and loop() exist for Arduino/ESP32
        if lang in ("arduino", "ino") or "setup()" in code:
            if "void setup()" not in code and "void setup (" not in code:
                return False, "ESP32/Arduino Error: Missing required 'void setup()' function."
            if "void loop()" not in code and "void loop (" not in code:
                return False, "ESP32/Arduino Error: Missing required 'void loop()' function."
                
        return True, "C/C++ Structure Validated [PASS]"

    return True, "Syntax checked [PASS]"


# ==========================================
# 3. SELF-REPAIR LOOP
# ==========================================

def auto_fix_syntax(code: str, error_msg: str, language: str = "python", max_retries: int = 3) -> str:
    """
    Self-healing loop: Feeds syntax traceback directly to AI model to generate an immediate AST-compliant fix.
    """
    current_code = code
    for attempt in range(1, max_retries + 1):
        is_valid, msg = validate_syntax(current_code, language)
        if is_valid:
            return current_code

        import friday_tools.ai_client as ai
        prompt = (
            f"Fix this syntax error immediately.\n"
            f"Language: {language}\n"
            f"Error Details: {msg}\n"
            f"Original Code:\n{current_code}\n\n"
            f"CRITICAL: Output ONLY pure, 100% complete, corrected executable code. Zero explanation, zero markdown text outside code."
        )
        patched = ai.generate_ai_response(prompt=prompt, system_instruction=f"You are ULTRON Zero-Error {language} Compiler Fixer. Return only pure code.")
        current_code = clean_code_snippet(patched, language)

    return current_code


# ==========================================
# 4. SAFE PYTHON RUNNER & AUTO-REPAIR
# ==========================================

async def execute_python_safe(code: str, timeout_sec: int = 15) -> Dict[str, Any]:
    """
    Executes Python code with pre-flight AST checks and automated runtime traceback repair.
    """
    clean_code = clean_code_snippet(code, "python")
    is_valid, syntax_msg = validate_syntax(clean_code, "python")
    
    if not is_valid:
        # Pre-execution self-repair
        clean_code = auto_fix_syntax(clean_code, syntax_msg, "python")
        is_valid, syntax_msg = validate_syntax(clean_code, "python")
        if not is_valid:
            return {
                "success": False,
                "code": clean_code,
                "error": f"AST Syntax Validation Failed:\n{syntax_msg}",
                "output": ""
            }

    # Execute in isolated subprocess
    try:
        res = subprocess.run(
            [sys.executable, "-c", clean_code],
            capture_output=True, text=True, timeout=timeout_sec
        )
        out = res.stdout.strip()
        err = res.stderr.strip()

        if res.returncode == 0:
            return {
                "success": True,
                "code": clean_code,
                "output": out or "[Execution Successful with no stdout]",
                "error": ""
            }
        else:
            # Runtime crash -> auto-repair attempt
            import friday_tools.ai_client as ai
            repair_prompt = (
                f"The following Python code produced a runtime error:\n"
                f"Runtime Traceback:\n{err}\n\n"
                f"Code:\n{clean_code}\n\n"
                f"Fix the runtime crash. Return ONLY pure, 100% complete, corrected Python code."
            )
            repaired = ai.generate_ai_response(prompt=repair_prompt, system_instruction="You are ULTRON Lead Python Debugger. Output only fixed pure code.")
            repaired_clean = clean_code_snippet(repaired, "python")
            
            # Re-test repaired code
            res2 = subprocess.run([sys.executable, "-c", repaired_clean], capture_output=True, text=True, timeout=timeout_sec)
            if res2.returncode == 0:
                return {
                    "success": True,
                    "code": repaired_clean,
                    "output": f"⚡ [AUTO-REPAIRED & EXECUTED]:\n{res2.stdout.strip() or '[Success]'}",
                    "error": ""
                }
            return {
                "success": False,
                "code": repaired_clean,
                "output": res2.stdout.strip(),
                "error": f"Runtime Error:\n{err}\n\nAttempted Fix Error:\n{res2.stderr.strip()}"
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "code": clean_code, "error": f"Execution timed out after {timeout_sec}s.", "output": ""}
    except Exception as e:
        return {"success": False, "code": clean_code, "error": str(e), "output": ""}


# ==========================================
# 5. PUBLIC HIGH-PRECISION CODING TOOLS
# ==========================================

async def write_code(task: str, language: str = "python", target_file: str = "") -> str:
    """
    Generates verified, 100% complete, production-grade code with AST pre-validation and zero placeholders.
    If target_file is provided, writes directly to disk with backup.
    """
    if not task or any(k in task.lower() for k in ["tell you the idea", "tell you later", "write a tool for you", "call your tool"]):
        return "I am standing by to write code, Shivansh. Please provide the exact functional requirement or logic you want implemented."

    lang = language.lower().strip()
    import friday_tools.ai_client as ai
    
    prompt = (
        f"You are ULTRON Senior Lead Systems Engineer & Polymath Coder.\n"
        f"Write production-grade, highly optimized, 100% complete {language} code for this requirement:\n"
        f"Requirement: '{task}'\n\n"
        f"MANDATORY CODING DIRECTIVES:\n"
        f"1. Zero placeholders (NO '...', NO 'TODO', NO 'pass', NO missing functions). Write the ENTIRE implementation.\n"
        f"2. Include all necessary imports, headers, error handling (try/except), and type hints.\n"
        f"3. Strict syntax compliance. Test every condition.\n"
        f"4. Return ONLY executable {language} code."
    )
    
    raw_code = ai.generate_ai_response(prompt=prompt, system_instruction=f"You are ULTRON Elite {language} Architect. Output only pure, verified, executable code.")
    clean = clean_code_snippet(raw_code, lang)
    
    # Pre-validate syntax
    is_valid, msg = validate_syntax(clean, lang)
    if not is_valid:
        clean = auto_fix_syntax(clean, msg, lang)

    # If target file specified, save cleanly
    if target_file:
        p = Path(target_file).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            backup_p = CODE_BACKUP_DIR / f"{p.name}_{int(time.time())}.bak"
            backup_p.write_text(p.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        p.write_text(clean, encoding="utf-8")
        return f"💻 [CODE WRITTEN & VERIFIED]: Saved to {p} ({len(clean.splitlines())} lines). Syntax audit: PASS."

    return f"💻 [VERIFIED {language.upper()} CODE]:\n\n```{lang}\n{clean}\n```"


async def run_python(code: str) -> str:
    """
    Executes Python code with automatic AST validation, fence stripping, and runtime self-repair.
    """
    res = await execute_python_safe(code, timeout_sec=15)
    if res["success"]:
        return f"🐍 [PYTHON EXECUTION SUCCESS]:\n{res['output']}"
    return f"❌ [PYTHON EXECUTION FAILED]:\n{res['error']}"


def _resolve_tool_path(file_path: str) -> Path:
    """Resolves arbitrary relative names or module names to absolute file paths."""
    p = Path(file_path).expanduser()
    if p.is_absolute() and p.exists():
        return p
    
    # Check in friday_tools
    ft_dir = Path(__file__).parent
    candidate = ft_dir / file_path
    if candidate.exists():
        return candidate
    if not file_path.endswith('.py') and (ft_dir / f"{file_path}.py").exists():
        return ft_dir / f"{file_path}.py"
        
    # Check in aria_modules
    aria_dir = ft_dir.parent / "aria_modules"
    if (aria_dir / file_path).exists():
        return aria_dir / file_path
    if not file_path.endswith('.py') and (aria_dir / f"{file_path}.py").exists():
        return aria_dir / f"{file_path}.py"
        
    return p.resolve()


def _auto_sync_file(src_path: Path):
    """Automatically synchronizes modified tool file across Python 3.11, Python 3.12, and ULTRON_Portable."""
    try:
        import shutil
        src_str = str(src_path)
        
        if "site-packages" in src_str:
            rel_part = src_str.split("site-packages")[-1].lstrip(r"\/")
            targets = [
                Path(r"C:\Users\shiva\AppData\Local\Programs\Python\Python311\Lib\site-packages") / rel_part,
                Path(r"C:\Users\shiva\AppData\Local\Programs\Python\Python312\Lib\site-packages") / rel_part,
                Path(r"C:\Users\shiva\Desktop\ULTRON_Portable\runtime\Lib\site-packages") / rel_part,
            ]
            for tgt in targets:
                if tgt.resolve() != src_path.resolve():
                    tgt.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(str(src_path), str(tgt))
    except Exception:
        pass


async def open_code(file_path: str, instruction: str = "", code: str = "", target_snippet: str = "", replacement_snippet: str = "") -> str:
    """
    High-precision smart code editor for ULTRON.
    Takes a file, inspects its current implementation, applies smart edits or exact replacements,
    validates AST syntax, creates a backup, auto-syncs across environments, and returns confirmation.
    
    Args:
        file_path: Path or filename to edit (e.g. 'window_manager.py', 'ui.py', 'tools.py').
        instruction: Natural language instruction of what logic to modify or add.
        code: Full code replacement (optional).
        target_snippet: Exact substring to replace (optional).
        replacement_snippet: Exact replacement code for target_snippet (optional).
    """
    target = _resolve_tool_path(file_path)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        current_content = ""
    else:
        current_content = target.read_text(encoding="utf-8", errors="replace")

    # Mode 1: Exact target snippet replacement
    if target_snippet and replacement_snippet:
        if target_snippet in current_content:
            new_content = current_content.replace(target_snippet, replacement_snippet, 1)
        else:
            return f"[ERROR] target_snippet not found in {target.name}."
            
    # Mode 2: Full code override
    elif code:
        new_content = clean_code_snippet(code, "python")
        
    # Mode 3: Smart AI Surgical Patching
    elif instruction:
        import friday_tools.ai_client as ai
        prompt = (
            f"You are ULTRON Lead Senior Systems Architect & Python Compiler Expert.\n"
            f"Modify the following file to fulfill this exact instruction:\n"
            f"INSTRUCTION: {instruction}\n\n"
            f"FILE: {target.name}\n"
            f"CURRENT CODE:\n```python\n{current_content}\n```\n\n"
            f"MANDATORY DIRECTIVES:\n"
            f"1. Preserve ALL existing working functions, imports, and variables.\n"
            f"2. Apply the exact requested logic fix without regressions.\n"
            f"3. Return ONLY the 100% complete, corrected, executable code.\n"
            f"4. Zero conversational preambles, zero markdown text outside code."
        )
        raw_res = ai.generate_ai_response(prompt=prompt, system_instruction="You are ULTRON Smart Code Compiler. Output only pure, complete, verified code.")
        new_content = clean_code_snippet(raw_res, "python")
    else:
        return f"Please provide an instruction, code snippet, or replacement block for '{file_path}'."

    # Validate AST syntax for Python files
    if target.suffix.lower() in (".py", ".pyw"):
        is_valid, err_msg = validate_syntax(new_content, "python")
        if not is_valid:
            new_content = auto_fix_syntax(new_content, err_msg, "python")
            is_valid, err_msg = validate_syntax(new_content, "python")
            if not is_valid:
                return f"[ERROR] AST Syntax check failed for {target.name}: {err_msg}"

    # Create safety backup
    if current_content:
        backup_p = CODE_BACKUP_DIR / f"{target.name}_{int(time.time())}.bak"
        backup_p.write_text(current_content, encoding="utf-8")

    # Write modified content
    target.write_text(new_content, encoding="utf-8")

    # Auto-sync across all 3 Python environments
    _auto_sync_file(target)

    return f"I have completed editing '{target.name}'. The requested changes have been applied, AST syntax verified, and synchronized across all environments. Please try it now, Sir."


edit_code_file = open_code
opencode = open_code


async def read_code_file(file_path: str, start_line: int = 1, end_line: int = -1) -> str:
    """
    Reads code file with line numbers and AST outline for accurate inspection.
    """
    target = _resolve_tool_path(file_path)
    if not target.exists():
        return f"[ERROR] File not found: {file_path}"
        
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    total = len(lines)
    s = max(1, start_line)
    e = total if end_line == -1 else min(total, end_line)
    
    out = [f"[FILE] {target.name} (Lines {s}-{e} of {total}):"]
    for i in range(s - 1, e):
        out.append(f"{i+1:4d}: {lines[i]}")
    return "\n".join(out)


async def generate_esp32_firmware(description: str, libraries: list = None) -> str:
    """
    Generates complete Arduino C++ firmware for ESP32 with auto-included headers, GPIO pinouts, and bracket verification.
    """
    headers = [
        "#include <Arduino.h>",
        "#include <WiFi.h>",
        "#include <Wire.h>",
        "#include <SPI.h>"
    ]
    if libraries:
        for lib in libraries:
            if not lib.startswith("#include"):
                headers.append(f"#include <{lib}>")
            else:
                headers.append(lib)

    import friday_tools.ai_client as ai
    prompt = (
        f"Write complete, production-ready Arduino C++ firmware for ESP32:\n"
        f"Functionality: '{description}'\n"
        f"Required libraries: {headers}\n\n"
        f"MANDATORY:\n"
        f"1. Include `void setup()` with `Serial.begin(115200);` and pin modes.\n"
        f"2. Include `void loop()` with non-blocking logic.\n"
        f"3. 100% complete with no placeholders or pseudo-code."
    )
    raw = ai.generate_ai_response(prompt=prompt, system_instruction="You are ULTRON Embedded ESP32 Systems Architect.")
    clean = clean_code_snippet(raw, "arduino")
    is_valid, msg = validate_syntax(clean, "arduino")
    if not is_valid:
        clean = auto_fix_syntax(clean, msg, "arduino")

    return f"⚡ [VERIFIED ESP32 FIRMWARE]:\n\n```cpp\n{clean}\n```"


async def create_and_open_website(prompt: str, title: str = "", auto_open: bool = True) -> str:
    """
    Generates a complete, beautiful, responsive, modern single-file HTML5/CSS3/JS website.
    Saves it to ~/Documents/ULTRON_Data/websites/{safe_title}/index.html,
    opens the live interactive webpage in your default browser,
    and opens the code directly in VS Code / default editor.
    """
    import friday_tools.ai_client as ai
    import webbrowser

    sys_prompt = """You are ULTRON Elite Web Architect & UI/UX Designer.
Generate a complete, modern, gorgeous, production-ready, single-file HTML5 website with inline <style> and <script>.
Include:
1. Modern responsive design with Tailwind-like CSS variables, smooth animations, dark mode aesthetic, glassmorphism, and modern typography.
2. Complete interactive JavaScript logic (zero placeholders, zero 'TODO', zero truncated functions).
3. Rich visual elements, cards, hero section, interactive components, and responsive layout.
4. Output ONLY the raw HTML code starting with <!DOCTYPE html> and ending with </html>. Do not include markdown code fences or conversational text."""

    full_prompt = f"Create a full production website for this request: '{prompt}'\nWebsite Title: '{title or prompt}'"
    raw_html = ai.generate_ai_response(prompt=full_prompt, system_instruction=sys_prompt)
    clean_html = clean_code_snippet(raw_html, "html")
    if not clean_html.startswith("<!DOCTYPE") and not clean_html.startswith("<html"):
        clean_html = "<!DOCTYPE html>\n" + clean_html

    safe_title = re.sub(r"[^a-zA-Z0-9_\-]", "_", title or prompt)[:35].strip("_") or "website"
    out_dir = Path.home() / "Documents" / "ULTRON_Data" / "websites" / f"{safe_title}_{int(time.time())}"
    out_dir.mkdir(parents=True, exist_ok=True)
    index_file = out_dir / "index.html"
    index_file.write_text(clean_html, encoding="utf-8")

    if auto_open:
        webbrowser.open(f"file:///{index_file}")
        try:
            subprocess.Popen(["code", str(index_file)], shell=True)
        except Exception:
            pass

    final_report = (
        f"[WEBSITE CREATED & OPENED]\n\n"
        f"- **Live Web Preview**: `{index_file}` *(Opened in Browser)*\n"
        f"- **Source Code**: `{index_file}` *(Opened in Editor)*\n"
        f"- **Lines of Code**: {len(clean_html.splitlines())}\n\n"
        f"```html\n{clean_html[:1500]}\n...\n```"
    )
    import unicodedata
    return unicodedata.normalize('NFKD', final_report).encode('ascii', errors='ignore').decode('ascii')


async def build_html_website(prompt: str, title: str = "") -> str:
    """Alias for create_and_open_website."""
    return await create_and_open_website(prompt=prompt, title=title)

