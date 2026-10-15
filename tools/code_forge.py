"""
ULTRON CODE-FORGE Engine
Autonomous multi-file software synthesis, self-debugging sandbox loop,
AST code auditing, test suite orchestrator, and smart Git commit generator.
"""

import os
import re
import sys
import ast
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from dotenv import load_dotenv
    env_paths = [
        Path.home() / "Documents" / "ULTRON_Data" / ".env",
        Path.home() / ".env",
        Path(".env")
    ]
    for ep in env_paths:
        if ep.exists():
            load_dotenv(dotenv_path=ep, override=False)
except Exception:
    pass


def _get_ai_response(prompt: str, system_prompt: str = "You are ULTRON CODE-FORGE, elite autonomous software architect and debugger.") -> str:
    """Invokes AI reasoning engine for code synthesis and debugging."""
    try:
        from friday_tools.ai_client import ask_ai
        return ask_ai(f"{system_prompt}\n\n{prompt}")
    except Exception:
        # Fallback to direct Groq or Gemini
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                client = Groq(api_key=api_key)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4096
                )
                return completion.choices[0].message.content or ""
        except Exception:
            pass
        
        try:
            import google.generativeai as genai
            g_key = os.getenv("GEMINI_API_KEY")
            if g_key:
                genai.configure(api_key=g_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                res = model.generate_content(f"{system_prompt}\n\n{prompt}")
                return res.text or ""
        except Exception as e:
            return f"[CODE-FORGE AI ERROR] Failed to query AI engine: {e}"
        
        return "[CODE-FORGE AI ERROR] No AI backend available."


async def forge_create_feature(prompt: str, project_dir: str = ".") -> str:
    """
    Synthesizes and writes multi-file features or entire project architectures based on requirements.
    Creates directories, files, unit tests, and configuration files automatically.
    """
    base_path = Path(project_dir).resolve()
    base_path.mkdir(parents=True, exist_ok=True)

    system_prompt = (
        "You are CODE-FORGE Multi-File Project Synthesizer. Output full, complete, production-grade code.\n"
        "Format your response as a series of file blocks strictly following this format:\n\n"
        "FILE: <relative_file_path>\n"
        "```<language>\n"
        "<code>\n"
        "```\n\n"
        "Include all required files, documentation, imports, and tests. No placeholders, no TODOs."
    )

    ai_prompt = f"Project Target Directory: {base_path}\nFeature/Project Requirement:\n{prompt}"
    response = _get_ai_response(ai_prompt, system_prompt=system_prompt)

    if "[CODE-FORGE AI ERROR]" in response:
        return response

    # Parse FILE: blocks
    file_pattern = re.compile(r"FILE:\s*([^\n\r]+)\s*```[a-zA-Z0-9_\-\.]*\n(.*?)```", re.DOTALL)
    matches = file_pattern.findall(response)

    created_files = []
    if matches:
        for rel_path_str, code_content in matches:
            clean_rel_path = rel_path_str.strip().strip("'\"`")
            target_file = base_path / clean_rel_path
            try:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(code_content.strip() + "\n")
                created_files.append(str(clean_rel_path))
            except Exception as e:
                created_files.append(f"{clean_rel_path} (Failed: {e})")

        return (
            f"⚡ [CODE-FORGE SYNTHESIS COMPLETE]\n"
            f"• Project Root: {base_path}\n"
            f"• Files Generated ({len(created_files)}):\n" +
            "\n".join([f"  - {f}" for f in created_files]) +
            f"\n\n{'='*55}\nArchitectural Overview:\n" +
            re.sub(r"FILE:\s*[^\n]+\s*```.*?```", "", response, flags=re.DOTALL).strip()
        )
    else:
        # If no explicit FILE blocks were parsed, save directly to generated_feature.py
        target_file = base_path / "generated_feature.py"
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(response.strip() + "\n")
            return f"⚡ [CODE-FORGE SYNTHESIS COMPLETE]\nGenerated script saved to: {target_file}\n\n{response[:500]}..."
        except Exception as e:
            return f"[CODE-FORGE ERROR] Failed to write generated file: {e}\n\nResponse:\n{response}"


async def forge_auto_debug(target_script_or_command: str, max_rounds: int = 5) -> str:
    """
    Autonomous self-debugging sandbox loop.
    Executes code in a subprocess, intercepts stdout/stderr tracebacks, diagnoses root cause,
    generates surgical AI patches, applies them directly to source files, and verifies resolution.
    """
    logs = [
        f"🛠️ [CODE-FORGE SELF-HEALING SANDBOX INITIALIZED]",
        f"• Target Command / Script: {target_script_or_command}",
        f"• Max Debug Rounds: {max_rounds}",
        "=" * 60
    ]

    current_round = 1
    # Check if target is a python script path or a general shell command
    is_script = os.path.exists(target_script_or_command) and target_script_or_command.endswith(".py")

    while current_round <= max_rounds:
        logs.append(f"\n[ROUND {current_round}/{max_rounds}] Executing...")

        if is_script:
            cmd = [sys.executable, target_script_or_command]
            cwd = str(Path(target_script_or_command).parent.resolve())
        else:
            cmd = target_script_or_command
            cwd = os.getcwd()

        try:
            proc = subprocess.run(
                cmd,
                shell=not is_script,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cwd
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            logs.append("❌ Process timed out after 30 seconds.")
            stderr = "TimeoutExpired: Process exceeded execution limit of 30s."
            exit_code = -1
        except Exception as e:
            stderr = f"Subprocess invocation failure: {e}"
            exit_code = -1
            stdout = ""

        if exit_code == 0 and "Traceback" not in stderr and "Error" not in stderr:
            logs.append(f"✅ [SUCCESS] Execution completed cleanly with exit code 0.")
            if stdout:
                logs.append(f"Output:\n{stdout[:1000]}")
            break

        logs.append(f"⚠️ [FAILURE DETECTED] Exit Code: {exit_code}")
        error_context = stderr if stderr else stdout
        logs.append(f"Traceback/Error Extract:\n{error_context[:1200]}")

        # Extract offending file if possible
        failed_file = None
        if is_script:
            failed_file = target_script_or_command
        else:
            file_match = re.findall(r'File "([^"]+)", line (\d+)', error_context)
            if file_match:
                for match_path, _ in reversed(file_match):
                    if os.path.exists(match_path):
                        failed_file = match_path
                        break

        if not failed_file or not os.path.exists(failed_file):
            logs.append(f"❌ Could not isolate specific editable source file from traceback. Aborting auto-patch.")
            break

        # Read source code of the failing file
        try:
            with open(failed_file, "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception as e:
            logs.append(f"❌ Failed to read source file {failed_file}: {e}")
            break

        logs.append(f"🔍 Analyzing {os.path.basename(failed_file)} with AI Auto-Patcher...")

        patch_prompt = f"""
        Fix this error in the Python file.
        File: {failed_file}
        Error Traceback:
        {error_context}

        Current Source Code:
        ```python
        {source_code}
        ```

        Output ONLY the complete, fixed Python code for this file wrapped in ```python ... ```.
        Do not output explanations or conversational filler.
        """

        patched_response = _get_ai_response(patch_prompt, system_prompt="You are an autonomous code repair engine. Fix all syntax, logic, and runtime errors cleanly.")
        
        # Extract code from response
        code_match = re.search(r"```python\s*(.*?)\s*```", patched_response, re.DOTALL)
        if not code_match:
            code_match = re.search(r"```\s*(.*?)\s*```", patched_response, re.DOTALL)
            
        fixed_code = code_match.group(1).strip() if code_match else patched_response.strip()

        if not fixed_code or len(fixed_code) < 10:
            logs.append(f"❌ AI returned empty or invalid patch.")
            break

        # Backup and overwrite
        try:
            backup_path = f"{failed_file}.bak_{int(time.time())}"
            shutil.copy2(failed_file, backup_path)
            with open(failed_file, "w", encoding="utf-8") as f:
                f.write(fixed_code + "\n")
            logs.append(f"🔧 Applied patch to {os.path.basename(failed_file)} (Backup saved: {os.path.basename(backup_path)}).")
        except Exception as e:
            logs.append(f"❌ Failed to apply patch to file: {e}")
            break

        current_round += 1

    logs.append("\n" + "=" * 60)
    logs.append("🏁 Auto-debug process finished.")
    return "\n".join(logs)


async def forge_test_suite(project_path: str = ".", runner: str = "pytest") -> str:
    """
    Executes automated test suites across the project using PyTest or Unittest.
    Aggregates test outcomes, performance duration, failing assertions, and coverage metrics.
    """
    target = Path(project_path).resolve()
    if not target.exists():
        return f"[CODE-FORGE ERROR] Target path '{project_path}' does not exist."

    cmd = [sys.executable, "-m", runner, str(target), "-v"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(target if target.is_dir() else target.parent))
        output = proc.stdout if proc.stdout else proc.stderr
        exit_code = proc.returncode

        status_tag = "✅ [ALL TESTS PASSED]" if exit_code == 0 else f"❌ [TEST SUITE FAILURES DETECTED - Exit Code {exit_code}]"
        
        return (
            f"🧪 [CODE-FORGE TEST SUITE ORCHESTRATOR]\n"
            f"• Target: {target}\n"
            f"• Runner: {runner}\n"
            f"• Status: {status_tag}\n"
            f"{'='*60}\n"
            f"{output.strip()}"
        )
    except subprocess.TimeoutExpired:
        return f"[CODE-FORGE TEST ERROR] Test suite execution timed out after 60s."
    except Exception as e:
        return f"[CODE-FORGE TEST ERROR] Failed to run test runner: {e}"


async def forge_code_audit_and_refactor(file_path: str) -> str:
    """
    Performs static AST inspection, code quality auditing, cyclomatic complexity profiling,
    vulnerability scanning (eval/exec/secrets/SQLi), and generates optimized clean code.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        return f"[CODE-FORGE ERROR] File '{file_path}' does not exist."

    try:
        with open(path, "r", encoding="utf-8") as f:
            code_text = f.read()
    except Exception as e:
        return f"[CODE-FORGE ERROR] Failed to read file: {e}"

    # AST Static Analysis
    ast_issues = []
    has_syntax_error = False
    tree = None
    try:
        tree = ast.parse(code_text, filename=str(path))
    except SyntaxError as se:
        has_syntax_error = True
        ast_issues.append(f"Syntax Error on line {se.lineno}: {se.msg}")

    if tree:
        for node in ast.walk(tree):
            # Check unsafe calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ("eval", "exec"):
                        ast_issues.append(f"Security Alert: Dynamic execution function `{node.func.id}` detected on line {node.lineno}.")
            # Check bare excepts
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    ast_issues.append(f"Quality Warning: Bare `except:` detected on line {node.lineno}. Use specific exception types.")

    # AI Audit & Refactor
    audit_prompt = f"""
    Perform a senior software engineer code review and clean refactoring of this file:
    File: {path.name}
    AST Issues Detected: {ast_issues if ast_issues else 'None'}

    Source Code:
    ```python
    {code_text}
    ```

    Provide:
    1. 🛡️ Security & Vulnerability Assessment
    2. ⚡ Performance & Complexity Analysis
    3. 📐 Clean Code & Architecture Suggestions
    4. 💎 Complete Refactored Code (wrapped in ```python ... ```)
    """

    ai_review = _get_ai_response(audit_prompt, system_prompt="You are a Principal Software Architect & Security Auditor.")

    return (
        f"🛡️ [CODE-FORGE STATIC AUDIT & REFACTOR REVIEW]\n"
        f"• File: {path}\n"
        f"• Size: {len(code_text.splitlines())} lines | {len(code_text)} bytes\n"
        f"• Static AST Checks: {'❌ Syntax Errors' if has_syntax_error else '✅ Syntax Valid'}\n"
        f"{'='*60}\n"
        f"{ai_review}"
    )


async def forge_git_smart_commit(repo_dir: str = ".", custom_message: str = "") -> str:
    """
    Analyzes repository status and staged/unstaged diffs, synthesizes Conventional Commit messages
    (feat/fix/refactor/perf/test/docs), stages modifications, and creates an atomic Git commit.
    """
    cwd = Path(repo_dir).resolve()
    if not (cwd / ".git").exists():
        # Check parent directories for .git
        current = cwd
        found = False
        while current != current.parent:
            if (current / ".git").exists():
                cwd = current
                found = True
                break
            current = current.parent
        if not found:
            return f"[CODE-FORGE ERROR] '{repo_dir}' is not inside a valid Git repository."

    try:
        # Check git status
        status_proc = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=cwd)
        status_out = status_proc.stdout.strip()
        if not status_out:
            return f"ℹ️ [CODE-FORGE GIT] Working tree clean. No modified or untracked files to commit."

        # Stage all changes
        subprocess.run(["git", "add", "."], capture_output=True, text=True, cwd=cwd)

        # Get staged diff
        diff_proc = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, cwd=cwd)
        diff_out = diff_proc.stdout.strip()

        commit_msg = custom_message.strip()
        if not commit_msg:
            # Generate smart commit message via AI
            diff_sample = diff_out[:4000] if diff_out else status_out[:1000]
            prompt = (
                f"Generate a concise Conventional Commit message (e.g. 'feat(core): ...' or 'fix(auth): ...') "
                f"based on this git diff:\n\n{diff_sample}\n\n"
                f"Output ONLY the single commit message title and an optional 2-bullet description. No other text."
            )
            commit_msg = _get_ai_response(prompt, system_prompt="You are an expert Git version control engineer.")
            commit_msg = commit_msg.strip().replace('"', '\\"')

        # Commit
        commit_proc = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True, cwd=cwd)
        commit_out = commit_proc.stdout.strip() if commit_proc.stdout else commit_proc.stderr.strip()

        return (
            f"📦 [CODE-FORGE SMART GIT COMMIT]\n"
            f"• Repository: {cwd}\n"
            f"• Commit Message: {commit_msg}\n"
            f"{'='*55}\n"
            f"{commit_out}"
        )
    except Exception as e:
        return f"[CODE-FORGE GIT ERROR] Failed to execute git operations: {e}"
