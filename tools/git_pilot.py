"""
ULTRON Autonomous Git Pilot & Semantic Commit Reviewer
Automates git staging, semantic conventional commit message generation, merge reviews, and auto-sync.
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Optional

from friday_tools.sound_engine import play_sound_async


def _run_git(args: list, cwd: str = ".") -> tuple:
    try:
        p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


async def git_smart_commit(repo_path: str = ".", auto_push: bool = False, custom_hint: str = "") -> str:
    """
    Analyzes staged/unstaged changes in a Git repository, generates a conventional semantic commit message, and commits.
    
    Args:
        repo_path: Root directory of Git repository.
        auto_push: If True, pushes the commit to origin main/master.
        custom_hint: Optional guidance on what was changed.
    """
    play_sound_async("scan")
    
    # 1. Check status
    rc, status, err = _run_git(["status", "--short"], cwd=repo_path)
    if rc != 0 or not status:
        return f"[INFO] No changes detected to commit in '{repo_path}'."
        
    # 2. Stage all
    _run_git(["add", "-A"], cwd=repo_path)
    
    # 3. Get Diff
    rc, diff, _ = _run_git(["diff", "--cached"], cwd=repo_path)
    if not diff:
        diff = status
        
    # 4. Generate Semantic Commit Message with AI
    commit_msg = f"chore: automated update by ULTRON"
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            f"You are a Git commit expert. Generate a single concise conventional commit message (e.g. feat: ..., fix: ..., refactor: ..., docs: ...).\n"
            f"Hint: {custom_hint}\n"
            f"Git Diff:\n{diff[:3000]}\n"
            f"Return ONLY the commit message string, nothing else."
        )
        res = model.generate_content(prompt)
        if res.text:
            commit_msg = res.text.strip().replace('"', '').replace("`", "")
    except Exception:
        pass
        
    # 5. Commit
    rc, out, err = _run_git(["commit", "-m", commit_msg], cwd=repo_path)
    if rc != 0:
        return f"[FAIL] Git commit failed: {err}"
        
    push_status = ""
    if auto_push:
        rc_p, out_p, err_p = _run_git(["push"], cwd=repo_path)
        push_status = f"\n• Push: {'[OK] Pushed to remote' if rc_p == 0 else f'[FAIL] {err_p}'}"
        
    play_sound_async("chime")
    return (
        f"🌿 [GIT PILOT COMMIT COMPLETE]\n"
        f"• Repository: {os.path.abspath(repo_path)}\n"
        f"• Message: \"{commit_msg}\"{push_status}"
    )


async def git_review_changes(repo_path: str = ".") -> str:
    """Provides an AI-powered code review and risk analysis of all uncommitted Git changes."""
    rc, diff, _ = _run_git(["diff"], cwd=repo_path)
    if not diff:
        rc, diff, _ = _run_git(["diff", "--cached"], cwd=repo_path)
    if not diff:
        return "[INFO] Working tree clean. No uncommitted changes to review."
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            f"Perform an expert code review on this Git diff. Flag bugs, security risks, performance regressions, and recommend improvements:\n\n{diff[:4000]}"
        )
        res = model.generate_content(prompt)
        return f"🔍 [GIT CODE REVIEW]\n\n{res.text}"
    except Exception as e:
        return f"[FAIL] Code review error: {e}"
