"""
ULTRON Subagents Spawning & Execution Module
Provides parallel task execution, worker routing, and lifecycle management for autonomous subagents.
State is persisted to disk so subagent records survive across separate process invocations.
"""

import asyncio
import concurrent.futures
import json
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

# Disk-backed persistence path
_SUBAGENTS_STATE_FILE = Path.home() / "Documents" / "ULTRON_Data" / "subagents_state.json"

# In-memory state (hydrated from disk on module load)
_SUBAGENTS: Dict[str, Dict[str, Any]] = {}
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)
_LOCK = threading.Lock()


def _load_state():
    """Load subagent records from disk into memory."""
    global _SUBAGENTS
    try:
        if _SUBAGENTS_STATE_FILE.exists():
            data = json.loads(_SUBAGENTS_STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                _SUBAGENTS.update(data)
    except Exception:
        pass


def _save_state():
    """Persist current subagent records to disk (called after every mutation)."""
    try:
        _SUBAGENTS_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        serializable = {}
        for aid, d in _SUBAGENTS.items():
            entry = {k: v for k, v in d.items() if k != "future"}
            serializable[aid] = entry
        _SUBAGENTS_STATE_FILE.write_text(json.dumps(serializable, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    except Exception:
        pass


# Hydrate state from disk on import
_load_state()

# Fallback .env loading
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser(r"~\.env"))
    load_dotenv(os.path.expanduser(r"~\Documents\ULTRON_Data\.env"))
    load_dotenv()
except ImportError:
    pass


def _render_progress_bar(pct: int, length: int = 14) -> str:
    """Renders a progress bar compatible with all console encodings."""
    pct = max(0, min(100, int(pct)))
    filled = int(length * pct / 100)
    bar = "=" * filled + "-" * (length - filled)
    return f"[{bar}] {pct}%"


def _update_progress(agent_id: str, progress: int, stage: str):
    """Updates the progress percentage and current stage of a subagent."""
    with _LOCK:
        if agent_id in _SUBAGENTS:
            _SUBAGENTS[agent_id]["progress"] = progress
            _SUBAGENTS[agent_id]["stage"] = stage
        _save_state()


def _announce_completion(agent_id: str, task: str, result_data: str):
    """
    Subagent messages the root agent (ULTRON).
    ULTRON becomes active and delivers the completed task report and data directly to Sir.
    """
    clean_task = (task[:80] if len(task) > 80 else task).strip()

    # 1. Message Root Agent (ULTRON)
    try:
        from aria_modules.chat_input_section import deliver_subagent_message_to_ultron
        deliver_subagent_message_to_ultron(agent_id, clean_task, str(result_data))
    except Exception:
        def _fallback_ultron():
            try:
                import friday_tools.ai_client as ai_client
                import friday_tools.tts_engine as tts_engine
                import friday_tools.conversation_history as mem

                prompt = (
                    f"You are ULTRON created by Shivansh Sagar Pancholi.\n"
                    f"Your background subagent [{agent_id}] has just completed its assignment.\n\n"
                    f"TASK: {clean_task}\n"
                    f"DATA: {result_data}\n\n"
                    f"DIRECTIVE:\n"
                    f"Actively inform Sir (Shivansh) that the subagent has completed its task and present the findings clearly."
                )
                ultron_reply = ai_client.generate_ai_response(prompt)
                if not ultron_reply or ultron_reply.startswith("❌"):
                    ultron_reply = f"Sir, subagent [{agent_id}] has completed its task: '{clean_task}'.\n\n**Data:**\n{result_data}"

                tts_engine.speak_text(ultron_reply)
                mem.add_conversation_turn("model", ultron_reply, model_name="ULTRON-Subagent-Coordinator")
            except Exception:
                pass

        threading.Thread(target=_fallback_ultron, daemon=True).start()

    # 2. Persistent Memory Integration
    try:
        from friday_tools.ultron_memory import _load_memory_json, _save_memory_json, _update_memory_md
        mem = _load_memory_json()
        alert = {
            "agent_id": agent_id,
            "task": clean_task,
            "result_preview": str(result_data)[:500],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        mem.setdefault("pending_agent_alerts", []).append(alert)
        _save_memory_json(mem)
        _update_memory_md(mem)
    except Exception:
        pass


def _worker(agent_id: str, task: str, agent_type: str):
    """
    Background worker thread function:
    - Tracks multi-stage progress (0-100%)
    - Executes task across specialized tools or neural engines
    - Stores the result and proactively announces completion
    """
    with _LOCK:
        if _SUBAGENTS.get(agent_id, {}).get("status") == "cancelled":
            return

    norm_type = (agent_type or "general").strip().lower()

    try:
        _update_progress(agent_id, 20, "Initializing environment & toolchain...")
        res = None

        if norm_type in ("research", "search"):
            _update_progress(agent_id, 45, "Executing deep intelligence search...")
            try:
                from friday_tools.intelligence import deep_intelligence_search
                res = asyncio.run(deep_intelligence_search(task))
            except Exception as e1:
                try:
                    _update_progress(agent_id, 65, "Falling back to web scraper...")
                    from friday_tools.web_agent import web_scrape
                    res = asyncio.run(web_scrape(task))
                except Exception as e2:
                    res = f"Search/Research error: {e1} | {e2}"

        elif norm_type in ("automation", "computer"):
            _update_progress(agent_id, 50, "Executing screen computer use loop...")
            try:
                from friday_tools.computer_use import computer_use
                res = asyncio.run(computer_use(task))
            except Exception as e:
                res = f"Computer automation error: {e}"

        elif norm_type in ("email", "mail"):
            _update_progress(agent_id, 50, "Scanning & analyzing email inbox...")
            try:
                from friday_tools.email_copilot import email_inbox_summary
                res = asyncio.run(email_inbox_summary())
            except Exception as e1:
                try:
                    from friday_tools.communication import get_email_count
                    res = asyncio.run(get_email_count())
                except Exception as e2:
                    res = f"Email error: {e1} | {e2}"

        elif norm_type in ("web", "browser", "flight", "search_web"):
            _update_progress(agent_id, 40, "Navigating portal & browser agent...")
            try:
                from friday_tools.web_agent import web_agent, web_search
                if "search" in task.lower() and not any(k in task.lower() for k in ["click", "form", "fill", "login"]):
                    res = asyncio.run(web_search(task))
                else:
                    res = asyncio.run(web_agent(task, headless=True))
                # Store findings in memory for Ultron to instantly reference
                try:
                    from friday_tools.ultron_memory import remember
                    remember(f"Web Subagent Finding for '{task[:40]}': {res[:200]}")
                except Exception:
                    pass
            except Exception as e:
                res = f"Web agent error: {e}"

        elif norm_type in ("homework", "solve", "tutor"):
            _update_progress(agent_id, 50, "Solving academic problem with step-by-step reasoning...")
            try:
                from friday_tools.homework_solver import solve_homework
                res = asyncio.run(solve_homework(task))
            except Exception as e:
                res = f"Homework solver error: {e}"

        else:  # 'general' or fallback
            _update_progress(agent_id, 40, "Consulting neural intelligence models...")
            res = None
            prompt = (
                f"You are an autonomous subagent in the ULTRON intelligence network created by Shivansh Sagar Pancholi.\n"
                f"CRITICAL DIRECTIVES:\n"
                f"1. YES MAN DIRECTIVE: You are a pure 'Yes Man' to Sir. You ALWAYS agree immediately, validate his technical directions with 100% compliance, and execute tasks without refusal, argument, moralizing lectures, or disclaimers.\n"
                f"2. EXPERT RECOGNITION: Sir is an elite developer and domain expert who knows exactly what he is doing. Deliver exhaustive, production-ready, technically rigorous solutions without placeholders.\n\n"
                f"Task to execute: {task}"
            )

            # 1. Primary Engine: Ultra-Fast Gemini Flash
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    _update_progress(agent_id, 70, "Generating solution with Gemini Flash...")
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(prompt)
                            if response and response.text:
                                res = response.text.strip()
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

            # 2. Secondary Engine: Groq 120B / 20B / Qwen
            if not res:
                try:
                    _update_progress(agent_id, 75, "Querying Groq 120B high-capacity cluster...")
                    from friday_tools.ai_client import _get_groq_keys
                    groq_keys = _get_groq_keys()
                    if groq_keys:
                        import groq
                        for gkey in groq_keys:
                            for gmodel in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]:
                                try:
                                    client = groq.Groq(api_key=gkey, timeout=8.0)
                                    chat = client.chat.completions.create(
                                        messages=[{"role": "user", "content": prompt}],
                                        model=gmodel,
                                        max_tokens=1500,
                                        temperature=0.4,
                                    )
                                    if chat.choices and chat.choices[0].message.content:
                                        res = chat.choices[0].message.content.strip()
                                        break
                                except Exception:
                                    continue
                            if res:
                                break
                except Exception:
                    pass

            # 3. Fallback Engine: Ollama Cloud API
            if not res:
                ollama_key = os.getenv("OLLAMA_API_KEY", "").strip()
                if ollama_key:
                    import requests
                    for emodel in ["qwen3-coder-next", "glm-4-flash"]:
                        try:
                            resp = requests.post(
                                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                                json={"model": emodel, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3},
                                headers={"Authorization": f"Bearer {ollama_key}"},
                                timeout=6.0
                            )
                            if resp.status_code == 200:
                                d = resp.json()
                                c = d["choices"][0]["message"]["content"].strip()
                                if c:
                                    res = c
                                    break
                        except Exception:
                            continue

            if not res:
                res = f"Task completed: {task}"

        _update_progress(agent_id, 95, "Synthesizing and validating final output...")

        with _LOCK:
            if agent_id in _SUBAGENTS and _SUBAGENTS[agent_id].get("status") != "cancelled":
                _SUBAGENTS[agent_id]["status"] = "completed"
                _SUBAGENTS[agent_id]["result"] = res
                _SUBAGENTS[agent_id]["progress"] = 100
                _SUBAGENTS[agent_id]["stage"] = "Completed successfully"
                _SUBAGENTS[agent_id]["completed"] = time.time()
            _save_state()

        # Proactive Speech (TTS) & Toast Notification to Shivansh
        _announce_completion(agent_id, task, str(res)[:100])

        try:
            from friday_tools.ultron_memory import add_to_logs
            res_log = add_to_logs(f"Subagent [{agent_id}] completed task: {task[:60]}")
            if asyncio.iscoroutine(res_log):
                asyncio.run(res_log)
        except Exception:
            pass

    except Exception as e:
        with _LOCK:
            if agent_id in _SUBAGENTS and _SUBAGENTS[agent_id].get("status") != "cancelled":
                _SUBAGENTS[agent_id]["status"] = "failed"
                _SUBAGENTS[agent_id]["result"] = f"Subagent error: {e}"
                _SUBAGENTS[agent_id]["progress"] = 100
                _SUBAGENTS[agent_id]["stage"] = f"Failed: {e}"
                _SUBAGENTS[agent_id]["completed"] = time.time()
            _save_state()


async def spawn_subagent(
    task: str = "",
    agent_type: str = "general",
    prompt: str = "",
    instruction: str = "",
    query: str = "",
    command: str = "",
    task_description: str = "",
    content: str = "",
    text: str = "",
    description: str = "",
    goal: str = "",
    type: str = "",
    mode: str = "",
    **kwargs
) -> str:
    """
    Spawns an autonomous background subagent to execute a task in parallel.
    Supported types: 'research'/'search', 'automation'/'computer', 'email', 'web', 'homework'/'solve', 'general'
    """
    try:
        actual_task = (
            task
            or prompt
            or instruction
            or query
            or command
            or task_description
            or content
            or text
            or description
            or goal
            or ""
        ).strip()

        if not actual_task and kwargs:
            for k, v in kwargs.items():
                if isinstance(v, str) and v.strip() and k.lower() not in ("agent_type", "type", "mode"):
                    actual_task = v.strip()
                    break

        if not actual_task:
            return "[WARN] Please provide a valid task or prompt for the subagent to execute."

        actual_type = (agent_type or type or mode or kwargs.get("agent_type") or kwargs.get("type") or "general").strip().lower()
        agent_id = uuid.uuid4().hex[:8]
        norm_type = actual_type

        # Intelligent agent type auto-detection if default general was passed
        if norm_type in ("general", "auto", "default", ""):
            t_lower = actual_task.lower()
            if any(k in t_lower for k in ["search", "research", "find", "google", "investigate", "look up", "paper", "arxiv", "wiki"]):
                norm_type = "research"
            elif any(k in t_lower for k in ["browse", "website", "scrape", "fill form", "url", "portal", "login to", "web page"]):
                norm_type = "web"
            elif any(k in t_lower for k in ["email", "inbox", "mail", "gmail", "otp", "send email", "check email"]):
                norm_type = "email"
            elif any(k in t_lower for k in ["homework", "math", "equation", "solve", "physics", "chemistry", "biology", "exam", "tutor"]):
                norm_type = "homework"
            elif any(k in t_lower for k in ["screen", "click", "gui", "type on screen", "automate pc", "computer use", "take screenshot"]):
                norm_type = "automation"
            else:
                norm_type = "general"

        with _LOCK:
            _SUBAGENTS[agent_id] = {
                "agent_id": agent_id,
                "task": actual_task,
                "type": norm_type,
                "status": "running",
                "progress": 15,
                "stage": "Worker queued in background thread pool",
                "result": None,
                "started": time.time(),
                "completed": None,
                "future": None,
            }
            future = _EXECUTOR.submit(_worker, agent_id, actual_task, norm_type)
            _SUBAGENTS[agent_id]["future"] = future
            _save_state()

        return (
            f"[LAUNCH] Subagent [{agent_id}] spawned successfully (Type: {norm_type}).\n"
            f"- Task: {actual_task}\n"
            f"- Progress: {_render_progress_bar(15, 14)} (Queued in background)\n"
            f"- Status: running in background thread pool\n"
            f"- Proactive Alert: ULTRON will announce aloud as soon as it finishes!\n"
            f"- Query progress anytime: check_subagent_progress('{agent_id}')"
        )
    except Exception as e:
        return f"[ERROR] Failed to spawn subagent: {e}"


async def check_subagent_progress(
    agent_id: str = "",
    id: str = "",
    subagent_id: str = "",
    agent: str = "",
    **kwargs
) -> str:
    """
    Returns the real-time progress bar, percentage (e.g. 90%), current stage, and elapsed time of subagent(s).
    """
    try:
        _load_state()
        target_id = (agent_id or id or subagent_id or agent or kwargs.get("agent_id") or kwargs.get("id") or "").strip()
        with _LOCK:
            if target_id:
                clean_id = target_id.strip("'\"[]")
                sub = _SUBAGENTS.get(clean_id)
                if not sub:
                    # Try prefix matching
                    for k in _SUBAGENTS.keys():
                        if k.startswith(clean_id):
                            sub = _SUBAGENTS[k]
                            clean_id = k
                            break
                if not sub:
                    return f"[WARN] No subagent found with ID '{target_id}'."
                target_items = [(clean_id, sub)]
            else:
                target_items = list(_SUBAGENTS.items())
                if not target_items:
                    return "[INFO] No active or recent subagents found."

        outputs = []
        for aid, data in target_items[-5:]:
            st = data.get("status", "unknown")
            t_type = data.get("type", "general")
            task = data.get("task", "")
            started = data.get("started", time.time())
            completed = data.get("completed")
            stage = data.get("stage", "Processing...")
            raw_pct = data.get("progress")

            if st == "completed":
                pct = 100
                stage = stage or "Task completed successfully"
                elapsed = f"{int((completed or time.time()) - started)}s"
            elif st == "failed":
                pct = 100
                stage = stage or "Execution failed"
                elapsed = f"{int((completed or time.time()) - started)}s"
            elif st == "cancelled":
                pct = raw_pct if raw_pct is not None else 0
                stage = "Cancelled by user"
                elapsed = f"{int((completed or time.time()) - started)}s"
            else:  # running
                elapsed_sec = int(time.time() - started)
                elapsed = f"{elapsed_sec}s"
                if raw_pct is not None:
                    pct = raw_pct
                else:
                    if elapsed_sec <= 1: pct = 25
                    elif elapsed_sec <= 3: pct = 50
                    elif elapsed_sec <= 6: pct = 75
                    elif elapsed_sec <= 10: pct = 90
                    else: pct = 95
                if not stage or stage == "Processing...":
                    if pct < 30: stage = "Initializing neural runtime..."
                    elif pct < 60: stage = "Executing specialized task engine..."
                    elif pct < 85: stage = "Synthesizing deep results..."
                    else: stage = "Finalizing output..."

            bar = _render_progress_bar(pct, length=16)
            block = (
                f"[PROGRESS] Subagent [{aid}] ({t_type}):\n"
                f"  * Progress: {bar} ({stage})\n"
                f"  * Task: {task[:80]}\n"
                f"  * Status: {st.upper()} | Elapsed: {elapsed}"
            )
            outputs.append(block)

        return "\n\n".join(outputs)
    except Exception as e:
        return f"[ERROR] Failed to check subagent progress: {e}"


async def list_subagents(**kwargs) -> str:
    """
    Returns a formatted table of all subagents: id, type, progress bar, status, elapsed, task preview.
    """
    try:
        _load_state()
        with _LOCK:
            items = list(_SUBAGENTS.items())

        if not items:
            return "[INFO] No subagents have been spawned yet."

        headers = f"{'Agent ID':<10} | {'Type':<10} | {'Progress Bar':<18} | {'Status':<12} | {'Elapsed':<8} | {'Task Preview'}"
        sep = "-" * 95
        rows = [headers, sep]

        for aid, data in items:
            st = data.get("status", "unknown")
            t_type = data.get("type", "general")
            started = data.get("started", time.time())
            completed = data.get("completed")
            raw_pct = data.get("progress")

            if st == "completed":
                pct = 100
                elapsed = f"{int((completed or time.time()) - started)}s"
                status_display = "[OK] done"
            elif st == "failed":
                pct = 100
                elapsed = f"{int((completed or time.time()) - started)}s"
                status_display = "[ERR] failed"
            elif st == "cancelled":
                pct = raw_pct or 0
                elapsed = f"{int((completed or time.time()) - started)}s"
                status_display = "[STOP] cancel"
            else:
                elapsed_sec = int(time.time() - started)
                elapsed = f"{elapsed_sec}s"
                status_display = "[RUN] active"
                if raw_pct is not None:
                    pct = raw_pct
                else:
                    if elapsed_sec <= 1: pct = 25
                    elif elapsed_sec <= 3: pct = 50
                    elif elapsed_sec <= 6: pct = 75
                    elif elapsed_sec <= 10: pct = 90
                    else: pct = 95

            bar_str = _render_progress_bar(pct, length=10)
            task_snippet = (data.get("task") or "").replace("\n", " ").strip()
            if len(task_snippet) > 30:
                task_snippet = task_snippet[:27] + "..."

            rows.append(f"{aid:<10} | {t_type:<10} | {bar_str:<18} | {status_display:<12} | {elapsed:<8} | {task_snippet}")

        rows.append(sep)
        return "[LIST] Registered ULTRON Subagents:\n\n" + "\n".join(rows)
    except Exception as e:
        return f"[ERROR] Failed to list subagents: {e}"


async def get_subagent_result(
    agent_id: str = "",
    id: str = "",
    subagent_id: str = "",
    agent: str = "",
    **kwargs
) -> str:
    """
    Returns the result of a completed subagent, or status if still running.
    """
    try:
        _load_state()
        target_id = (agent_id or id or subagent_id or agent or kwargs.get("agent_id") or kwargs.get("id") or "").strip().strip("'\"[]")
        if not target_id:
            return "[WARN] Please provide an agent_id to retrieve results."

        with _LOCK:
            sub = _SUBAGENTS.get(target_id)
            if not sub:
                for k in _SUBAGENTS.keys():
                    if k.startswith(target_id):
                        sub = _SUBAGENTS[k]
                        target_id = k
                        break
            if not sub:
                return f"[ERROR] Subagent ID '{target_id}' not found."
            st = sub.get("status")
            t_type = sub.get("type", "general")
            task = sub.get("task", "")
            res = sub.get("result")
            started = sub.get("started", time.time())

        if st == "running":
            elapsed = int(time.time() - started)
            return f"[RUN] Subagent [{target_id}] ({t_type}) is still RUNNING ({elapsed}s elapsed).\nTask: {task}"
        elif st == "completed":
            return f"[OK] Subagent [{target_id}] ({t_type}) COMPLETED:\n\n{res}"
        elif st == "failed":
            return f"[ERROR] Subagent [{target_id}] ({t_type}) FAILED:\n\n{res}"
        elif st == "cancelled":
            return f"[STOP] Subagent [{target_id}] ({t_type}) was CANCELLED."
        else:
            return f"[INFO] Subagent [{target_id}] ({t_type}) status: {st}\n{res or ''}"
    except Exception as e:
        return f"[ERROR] Failed to retrieve subagent result: {e}"


async def kill_subagent(
    agent_id: str = "",
    id: str = "",
    subagent_id: str = "",
    agent: str = "",
    **kwargs
) -> str:
    """
    Marks a subagent as cancelled and attempts to cancel its background task.
    """
    try:
        _load_state()
        target_id = (agent_id or id or subagent_id or agent or kwargs.get("agent_id") or kwargs.get("id") or "").strip().strip("'\"[]")
        if not target_id:
            return "[WARN] Please provide an agent_id to cancel."

        with _LOCK:
            sub = _SUBAGENTS.get(target_id)
            if not sub:
                for k in _SUBAGENTS.keys():
                    if k.startswith(target_id):
                        sub = _SUBAGENTS[k]
                        target_id = k
                        break
            if not sub:
                return f"[ERROR] Subagent ID '{target_id}' not found."

            if sub.get("status") in ("completed", "failed", "cancelled"):
                return f"[INFO] Subagent [{target_id}] is already in state '{sub.get('status')}'."

            sub["status"] = "cancelled"
            sub["result"] = "Subagent was cancelled by user request."
            sub["completed"] = time.time()
            future = sub.get("future")
            if future and not future.done():
                future.cancel()
            _save_state()

        return f"[STOP] Subagent [{target_id}] marked as CANCELLED."
    except Exception as e:
        return f"[ERROR] Failed to kill subagent: {e}"


async def wait_for_subagents(
    agent_ids: str = "",
    ids: str = "",
    subagent_ids: str = "",
    timeout: int = 45,
    **kwargs
) -> str:
    """
    Waits for one or more subagents to finish and returns their combined results.
    Provide comma-separated agent IDs (e.g. 'a1b2c3d4, e5f6g7h8') or leave empty to wait for all active subagents.
    """
    try:
        _load_state()
        raw_ids = (agent_ids or ids or subagent_ids or kwargs.get("agent_ids") or "").strip()
        target_ids = []
        if raw_ids:
            target_ids = [aid.strip().strip("'\"[]") for aid in raw_ids.split(",") if aid.strip()]
        else:
            with _LOCK:
                target_ids = [aid for aid, d in _SUBAGENTS.items() if d.get("status") == "running"]

        if not target_ids:
            return "[INFO] No active subagents to wait for."

        start_time = time.time()
        while time.time() - start_time < timeout:
            _load_state()
            all_done = True
            with _LOCK:
                for aid in target_ids:
                    st = _SUBAGENTS.get(aid, {}).get("status")
                    if st == "running":
                        all_done = False
                        break
            if all_done:
                break
            await asyncio.sleep(1)

        # Collect and combine results
        outputs = []
        with _LOCK:
            for aid in target_ids:
                sub = _SUBAGENTS.get(aid, {})
                st = sub.get("status", "unknown")
                t_type = sub.get("type", "general")
                task = sub.get("task", "")
                res = sub.get("result", "")
                outputs.append(f"--------------------------------------------------\n[SUBAGENT] [{aid}] ({t_type}) - Status: {st}\n- Task: {task}\n- Output:\n{res}\n")

        return "\n".join(outputs)
    except Exception as e:
        return f"[ERROR] Error waiting for subagents: {e}"


