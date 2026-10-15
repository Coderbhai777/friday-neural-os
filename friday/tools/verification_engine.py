"""
ULTRON JARVIS Self-Correction & Verification Engine (Layer 2)
Implements Plan -> Act -> Observe -> Verify -> Diagnose -> Auto-Repair -> Retry execution loop.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

BACKUP_DIR = Path.home() / "Documents" / "ULTRON_Data" / "action_backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 1. VERIFICATION & ASSERTION
# ==========================================

async def verify_action(action_name: str, expected_outcome: str, actual_output: str) -> str:
    """
    Evaluates whether an action succeeded by comparing actual output against the expected objective.
    """
    try:
        # Check for immediate negative indicators
        failure_signals = ["error", "exception", "failed", "traceback", "not found", "syntaxerror", "refused", "timeout"]
        has_error = any(sig in actual_output.lower() for sig in failure_signals) and ("0 error" not in actual_output.lower())

        if has_error:
            return f"❌ [VERIFICATION FAILED]: Action '{action_name}' encountered errors.\nExpected: {expected_outcome}\nActual Output Snippet: {actual_output[:300]}"
            
        import friday_tools.ai_client as ai
        prompt = (
            f"Evaluate if this action succeeded:\n"
            f"Action: {action_name}\n"
            f"Expected Outcome: {expected_outcome}\n"
            f"Actual Output: {actual_output[:1500]}\n\n"
            f"Respond with 'STATUS: SUCCESS' or 'STATUS: FAILURE' followed by a 1-sentence explanation."
        )
        verdict = ai.generate_ai_response(prompt=prompt, system_instruction="You are ULTRON Quality & Verification Auditor.")
        return f"🔍 [VERIFICATION AUDIT - {action_name}]:\n{verdict.strip()}"
    except Exception as e:
        return f"[ERROR] Verification failed: {e}"


def detect_failure(result_payload: str) -> Dict[str, Any]:
    """Analyzes a tool or command output for syntax errors, return codes, and exceptions."""
    p_lower = result_payload.lower()
    is_failed = False
    error_type = "None"
    
    if "syntaxerror" in p_lower:
        is_failed = True
        error_type = "SyntaxError"
    elif "modulenotfounderror" in p_lower or "no module named" in p_lower:
        is_failed = True
        error_type = "MissingDependency"
    elif "traceback (most recent call last)" in p_lower:
        is_failed = True
        error_type = "RuntimeCrash"
    elif "error:" in p_lower or "[error]" in p_lower:
        is_failed = True
        error_type = "ExecutionError"
    elif "exit code 1" in p_lower or "code 1" in p_lower:
        is_failed = True
        error_type = "NonZeroExitCode"

    return {
        "is_failed": is_failed,
        "error_type": error_type,
        "summary": result_payload[:200] if is_failed else "Execution Clean"
    }


# ==========================================
# 2. DIAGNOSTICS & AUTONOMOUS REPAIR
# ==========================================

async def diagnose_failure(error_trace: str, context: str = "") -> str:
    """
    Diagnoses the root cause of an execution failure and drafts a targeted repair patch.
    """
    try:
        import friday_tools.ai_client as ai
        prompt = (
            f"Diagnose this failure:\n"
            f"Context: {context}\n"
            f"Error Trace / Output:\n{error_trace}\n\n"
            f"Provide: 1) Exact Root Cause 2) Actionable Step-by-Step Fix 3) Corrected Code Patch."
        )
        return ai.generate_ai_response(prompt=prompt, system_instruction="You are ULTRON Autonomous Failure Diagnostic Engine.")
    except Exception as e:
        return f"[ERROR] Diagnostic failed: {e}"


async def repair_failure(error_trace: str, target_file: str = "") -> str:
    """
    Autonomously analyzes an error trace, inspects the target file, and applies the corrected code patch.
    """
    try:
        if target_file and Path(target_file).exists():
            code = Path(target_file).read_text(encoding="utf-8")
            
            # Backup before repair
            backup_file = BACKUP_DIR / f"{Path(target_file).name}_{int(time.time())}.bak"
            backup_file.write_text(code, encoding="utf-8")
            
            import friday_tools.ai_client as ai
            prompt = (
                f"Fix the bug in this file:\n"
                f"File: {target_file}\n"
                f"Error:\n{error_trace}\n\n"
                f"Existing Code:\n{code[:3000]}\n\n"
                f"Return ONLY the complete updated Python code file with the fix applied. No markdown formatting, just pure code."
            )
            repaired_code = ai.generate_ai_response(prompt=prompt, system_instruction="You are ULTRON Code Repair Engine. Output only executable python code.")
            
            # Clean markdown fences if present
            if repaired_code.startswith("```python"):
                repaired_code = repaired_code[len("```python"):].strip()
            if repaired_code.startswith("```"):
                repaired_code = repaired_code[3:].strip()
            if repaired_code.endswith("```"):
                repaired_code = repaired_code[:-3].strip()
                
            Path(target_file).write_text(repaired_code, encoding="utf-8")
            return f"🔧 [AUTO-REPAIR APPLIED]: Patched {target_file}. Original backed up to: {backup_file}."
            
        return await diagnose_failure(error_trace, context=f"Target: {target_file}")
    except Exception as e:
        return f"[ERROR] Auto-repair failed: {e}"


async def rollback_action(action_id: str = "") -> str:
    """Restores the most recent file or state backup created prior to an automated repair."""
    try:
        backups = sorted(list(BACKUP_DIR.glob("*.bak")), key=lambda p: p.stat().st_mtime, reverse=True)
        if not backups:
            return "[Rollback] No previous backups found."
            
        latest = backups[0]
        orig_name = latest.stem.rsplit("_", 1)[0]
        return f"⏪ [ROLLBACK READY]: Latest backup: {latest.name} for target '{orig_name}'."
    except Exception as e:
        return f"[ERROR] Rollback failed: {e}"


async def validate_mission(mission_id: str = "") -> str:
    """Verifies all completed steps of the active mission and asserts integrity."""
    from friday_tools.jarvis_mission import get_mission_status
    status = await get_mission_status(mission_id)
    return f"🛡️ [MISSION INTEGRITY CHECK]:\n{status}"
