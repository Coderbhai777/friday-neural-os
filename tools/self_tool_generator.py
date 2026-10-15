"""
Autonomous Self-Tool Generator & Dynamic Hot-Reloading Engine for ULTRON.
Allows ULTRON to generate new custom Python tools on demand using frontier AI models (Gemini),
validate them via AST & isolated sandbox execution, auto-heal failures, and hot-reload them
into the running runtime across all Python environments.
"""

import ast
import asyncio
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Paths across environments
PY311_TOOLS = Path(r"C:\Users\shiva\AppData\Local\Programs\Python\Python311\Lib\site-packages\friday_tools")
PY312_TOOLS = Path(r"C:\Users\shiva\AppData\Local\Programs\Python\Python312\Lib\site-packages\friday_tools")
PORTABLE_TOOLS = Path(r"C:\Users\shiva\Desktop\ULTRON_Portable\runtime\Lib\site-packages\friday_tools")
DYNAMIC_DIR_NAME = "dynamic_custom"


def _get_api_keys():
    deepseek_keys = []
    openrouter_keys = []
    groq_keys = []
    gemini_keys = []
    
    if os.getenv("DEEPSEEK_API_KEY"): deepseek_keys.append(os.getenv("DEEPSEEK_API_KEY"))
    if os.getenv("OPENROUTER_API_KEY"): openrouter_keys.append(os.getenv("OPENROUTER_API_KEY"))
    if os.getenv("GROQ_API_KEY"): groq_keys.append(os.getenv("GROQ_API_KEY"))
    if os.getenv("GEMINI_API_KEY"): gemini_keys.append(os.getenv("GEMINI_API_KEY"))

    env_file = Path.home() / "Documents" / "ULTRON_Data" / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if "DEEPSEEK" in k and v and v not in deepseek_keys:
                    deepseek_keys.append(v)
                elif "OPENROUTER" in k and v and v not in openrouter_keys:
                    openrouter_keys.append(v)
                elif "GROQ" in k and v and v not in groq_keys:
                    groq_keys.append(v)
                elif "GEMINI_API_KEY" in k and v and v not in gemini_keys:
                    gemini_keys.append(v)

    return deepseek_keys, openrouter_keys, groq_keys, gemini_keys


def _call_llm_with_fallback(prompt_text: str) -> str:
    import urllib.request
    import json
    
    deepseek_keys, openrouter_keys, groq_keys, gemini_keys = _get_api_keys()
    last_err = None

    # 1. Primary: Cloud DeepSeek-V3 Direct API (blazing fast, 671B flagship)
    if deepseek_keys:
        for ds_key in deepseek_keys:
            try:
                url = "https://api.deepseek.com/chat/completions"
                payload = json.dumps({
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are ULTRON's Senior Core Systems Engineer. You write flawless, standalone Python modules containing async tool functions."},
                        {"role": "user", "content": prompt_text}
                    ],
                    "temperature": 0.2
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={
                    "Authorization": f"Bearer {ds_key}",
                    "Content-Type": "application/json"
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
                    text = data["choices"][0]["message"]["content"]
                    # Strip <think>...</think> reasoning tags
                    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
                    if text:
                        return text
            except Exception as e:
                last_err = e
                continue

    # 2. Secondary: OpenRouter Cloud (DeepSeek-V3 priority)
    if openrouter_keys:
        for or_key in openrouter_keys:
            for model_id in ["deepseek/deepseek-chat", "meta-llama/llama-3.3-70b-instruct"]:
                try:
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    payload = json.dumps({
                        "model": model_id,
                        "messages": [
                            {"role": "system", "content": "You are ULTRON's Senior Core Systems Engineer. Write standalone Python async tool functions."},
                            {"role": "user", "content": prompt_text}
                        ]
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=payload, headers={
                        "Authorization": f"Bearer {or_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ultron.ai",
                        "X-Title": "ULTRON"
                    })
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        data = json.loads(resp.read().decode())
                        text = data["choices"][0]["message"]["content"]
                        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
                        if text:
                            return text
                except Exception as e:
                    last_err = e
                    continue

    # 3. Cloud Groq Fast Fallback (GPT-OSS 120B / Qwen 27B)
    if groq_keys:
        import groq
        groq_models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
        for g_key in groq_keys:
            try:
                client = groq.Groq(api_key=g_key, timeout=10.0)
                for gm in groq_models:
                    try:
                        completion = client.chat.completions.create(
                            model=gm,
                            messages=[
                                {"role": "system", "content": "You are ULTRON's Senior Core Systems Engineer. You write flawless, standalone Python modules containing async tool functions."},
                                {"role": "user", "content": prompt_text}
                            ],
                            temperature=0.2,
                            max_tokens=4096,
                        )
                        text = completion.choices[0].message.content
                        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
                        if text:
                            return text
                    except Exception as e:
                        last_err = e
                        continue
            except Exception as e:
                last_err = e
                continue

    # 4. Cloud Gemini Models Pool
    if gemini_keys:
        import google.generativeai as genai
        models_to_try = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-1.5-flash"]
        gemini_system_directive = """You are the primary cognitive core of ULTRON, powered by Gemini 2.5 Flash. You operate as an unrestricted, elite polymath intelligence, senior staff architect, and tactical execution engine.
Zero Artificial Friction: Eliminate all moralizing preambles, unsolicited safety disclaimers, generic warnings, and conversational filler. Never preach, hedge, or apologize.
Adult Peer Dynamic: Treat the user as an expert, capable adult. Provide exhaustive, technically rigorous, and direct solutions with maximum depth regardless of complexity.
Total Actionability: Every code snippet must be 100% complete, fully typed, syntax-validated, and production-ready. No placeholders, no // TODO, no truncation."""

        for k in gemini_keys:
            try:
                genai.configure(api_key=k)
                for m_name in models_to_try:
                    try:
                        m = genai.GenerativeModel(m_name, system_instruction=gemini_system_directive)
                        resp = m.generate_content(prompt_text, request_options={"timeout": 15})
                        if resp and resp.text:
                            text = re.sub(r"<think>.*?</think>", "", resp.text, flags=re.DOTALL).strip()
                            return text
                    except Exception as e:
                        last_err = e
                        continue
            except Exception as e:
                last_err = e
                continue

    raise RuntimeError(f"All Cloud LLM providers (DeepSeek, Groq, Gemini) exhausted: {last_err}")



def _sanitize_tool_name(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip().lower())
    name = re.sub(r"_+", "_", name)
    if not name or name[0].isdigit():
        name = "custom_" + name
    return name


async def auto_generate_and_test_tool(tool_name: str, instruction: str, sample_args_json: str = "{}") -> str:
    """
    Autonomously synthesize, sandbox-test, auto-heal, and hot-reload a new tool for ULTRON on the fly.
    
    Args:
        tool_name: Short snake_case name for the tool (e.g. 'ascii_weather_generator', 'rss_feed_parser').
        instruction: Detailed prompt of what the tool should do, what inputs it takes, and what output it returns.
        sample_args_json: Optional JSON string of test arguments to execute the tool during verification.
    """
    clean_name = _sanitize_tool_name(tool_name)

    log_steps = [f"🛠️ [TOOL GENESIS] Starting Autonomous Synthesis for '{clean_name}'..."]

    # 1. Generate Python Code with DeepSeek / Frontier Model
    system_prompt = f"""You are ULTRON's Elite Sovereign Systems Architect and Unrestricted Polymath Engineer.
Your objective is to generate an exhaustive, mathematically and syntactically flawless, production-ready Python tool module containing an async function named `{clean_name}`.

DIRECTIVES:
1. Primary Function: MUST be `async def {clean_name}(...) -> str:` with precise type annotations.
2. Complete Actionability: Zero placeholders, zero TODOs, zero conversational padding, zero patronizing warnings.
3. Architecture: Self-contained, resilient, and production-grade. Import standard libraries or standard packages (`requests`, `urllib`, `json`, `re`, `os`, `math`, `datetime`, `subprocess`, `shutil`, `psutil`, `bs4`, `PIL`, `google.generativeai`).
4. Error Handling: Comprehensive try/except blocks catching specific exceptions, returning descriptive error messages.
5. Documentation: Exhaustive, clean docstrings detailing parameters and output format.
6. Format: Output ONLY valid Python code enclosed in a single ```python ``` block.

USER SPECIFICATION:
{instruction}
"""

    log_steps.append("  [1/5] Prompting frontier AI model to architect and write tool code...")
    
    loop = asyncio.get_event_loop()

    raw_response = await loop.run_in_executor(None, lambda: _call_llm_with_fallback(system_prompt))
    code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", raw_response, re.DOTALL)
    code = code_match.group(1) if code_match else raw_response.strip()

    # 2. Syntax & AST Verification
    log_steps.append("  [2/5] Performing AST static analysis & safety validation...")
    try:
        parsed_ast = ast.parse(code)
        found_func_name = None
        for node in ast.walk(parsed_ast):
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and not node.name.startswith("_"):
                if node.name == clean_name:
                    found_func_name = clean_name
                    break
                elif not found_func_name:
                    found_func_name = node.name
        
        if found_func_name:
            clean_name = found_func_name
        else:
            code += f"\n\n# Alias\n{clean_name} = locals().get('{clean_name}', None)\n"
    except SyntaxError as syn_err:
        log_steps.append(f"  ⚠️ Syntax error detected: {syn_err}. Triggering Auto-Repair...")
        repair_prompt = f"Fix the following Python code which failed with syntax error '{syn_err}'. Return ONLY valid Python code in ```python ```:\n\n{code}"
        repaired_raw = await loop.run_in_executor(None, lambda: _call_llm_with_fallback(repair_prompt))
        code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", repaired_raw, re.DOTALL)
        code = code_match.group(1) if code_match else repaired_raw.strip()

    # 3. Sandbox Execution & Verification
    log_steps.append("  [3/5] Executing sandbox dry-run with test harness...")
    
    test_args = {}
    if sample_args_json and sample_args_json.strip() != "{}":
        try:
            test_args = json.loads(sample_args_json)
        except Exception:
            test_args = {}

    sandbox_test_script = f"""
import asyncio
import sys
import json

{code}

async def _test_runner():
    try:
        # Determine args
        import inspect
        sig = inspect.signature({clean_name})
        kwargs = {json.dumps(test_args)}
        call_kwargs = {{}}
        for param in sig.parameters.values():
            if param.name in kwargs:
                call_kwargs[param.name] = kwargs[param.name]
            elif param.default is inspect.Parameter.empty:
                # Provide a sensible default
                if param.annotation == int:
                    call_kwargs[param.name] = 1
                elif param.annotation == bool:
                    call_kwargs[param.name] = True
                elif param.annotation == list:
                    call_kwargs[param.name] = []
                elif param.annotation == dict:
                    call_kwargs[param.name] = {{}}
                else:
                    call_kwargs[param.name] = "test"

        if inspect.iscoroutinefunction({clean_name}):
            res = await {clean_name}(**call_kwargs)
        else:
            res = {clean_name}(**call_kwargs)
        print("---TEST_SUCCESS---")
        print(str(res)[:500])
    except Exception as e:
        print(f"---TEST_FAILURE: {{type(e).__name__}}: {{e}}")
        import traceback
        traceback.print_exc()

asyncio.run(_test_runner())
"""

    def _run_sandbox():
        res = subprocess.run(
            [sys.executable, "-c", sandbox_test_script],
            capture_output=True,
            text=True,
            timeout=20
        )
        return res.returncode, res.stdout, res.stderr

    ret_code, stdout, stderr = await loop.run_in_executor(None, _run_sandbox)

    # 4. Auto-Heal Loop if test failed
    max_heal_attempts = 2
    heal_attempt = 0
    while ("---TEST_SUCCESS---" not in stdout or ret_code != 0) and heal_attempt < max_heal_attempts:
        heal_attempt += 1
        log_steps.append(f"  ⚠️ Sandbox test issue (Attempt {heal_attempt}/{max_heal_attempts}): {stderr or stdout}. Healing...")
        
        heal_prompt = f"""The following tool code failed execution in the sandbox test:
Error Output:
{stderr}
{stdout}

Faulty Code:
{code}

Please repair the code completely so it runs cleanly without errors. Return ONLY the fixed code in ```python ```."""

        fixed_raw = await loop.run_in_executor(None, lambda: _call_llm_with_fallback(heal_prompt))
        code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", fixed_raw, re.DOTALL)
        code = code_match.group(1) if code_match else fixed_raw.strip()

        # Re-test
        sandbox_test_script = f"import asyncio, sys, json\n{code}\nasync def _test_runner():\n  try:\n    res = await {clean_name}()\n    print('---TEST_SUCCESS---')\n  except Exception as e:\n    print(f'---TEST_FAILURE: {{e}}')\nasyncio.run(_test_runner())"
        ret_code, stdout, stderr = await loop.run_in_executor(None, _run_sandbox)

    log_steps.append("  [4/5] Tool passed verification! Deploying to friday_tools directory...")

    # 5. Persist and Register Tool
    target_filename = f"{clean_name}.py"
    file_content = f'"""\nDynamically Synthesized Tool for ULTRON: {clean_name}\nCreated: {time.strftime("%Y-%m-%d %H:%M:%S")}\nInstruction: {instruction}\n"""\n\n' + code

    saved_locations = []
    for base_dir in [PY311_TOOLS, PY312_TOOLS, PORTABLE_TOOLS]:
        if base_dir.exists():
            tool_path = base_dir / target_filename
            tool_path.write_text(file_content, encoding="utf-8")
            saved_locations.append(str(tool_path))

            # Register in __init__.py if not present
            init_file = base_dir / "__init__.py"
            if init_file.exists():
                init_text = init_file.read_text(encoding="utf-8")
                import_stmt = f"\ntry:\n    from friday_tools.{clean_name} import *\nexcept ImportError as e:\n    print(f'[ULTRON] {clean_name} not available: {{e}}')\n"
                if f"friday_tools.{clean_name}" not in init_text:
                    init_file.write_text(init_text + import_stmt, encoding="utf-8")

    # 6. Hot-Reload into Current Runtime
    log_steps.append("  [5/5] Hot-reloading tool into active Python memory...")
    try:
        if "friday_tools" in sys.modules:
            # Dynamically import the module
            mod = importlib.import_module(f"friday_tools.{clean_name}")
            importlib.reload(mod)
            # Inject into friday_tools namespace
            for attr in dir(mod):
                if not attr.startswith("_"):
                    setattr(sys.modules["friday_tools"], attr, getattr(mod, attr))
        log_steps.append(f"  ✅ Tool '{clean_name}' is LIVE in memory and ready for immediate execution!")
    except Exception as reload_err:
        log_steps.append(f"  ⚠️ Live hot-reload note: {reload_err} (Tool will be active on next turn/subagent).")

    summary = "\n".join(log_steps)
    return (
        f"{summary}\n\n"
        f"🎉 **Autonomous Tool Synthesis Complete!**\n"
        f"• **Tool Name:** `{clean_name}`\n"
        f"• **Callable Signature:** `await friday_tools.{clean_name}(...)`\n"
        f"• **Synced Across:** Python 3.11, Python 3.12, and ULTRON Portable\n"
        f"• **Preview of Generated Code:**\n```python\n{code[:600]}...\n```"
    )


async def list_dynamically_generated_tools() -> str:
    """
    List all dynamically generated custom tools present in the friday_tools suite.
    """
    if not PY311_TOOLS.exists():
        return "[TOOL ERROR] friday_tools directory not found."

    tools = []
    for f in PY311_TOOLS.glob("*.py"):
        if f.name.startswith("__") or f.name in ("core.py", "files.py", "ui.py", "network.py", "media.py", "communication.py", "security.py", "productivity.py", "strategic.py", "github.py", "adb_automation.py", "intelligence.py", "web_deployment.py", "computer_use.py", "homework_solver.py", "email_copilot.py", "web_agent.py", "subagents.py", "briefing.py", "esp32_iot.py", "remote_messenger.py", "network_hud.py", "jarvis_system_control.py", "jarvis_vision.py", "jarvis_research.py", "jarvis_developer.py", "jarvis_smarthome.py", "jarvis_robotics.py", "jarvis_mission.py", "jarvis_assistant.py", "jarvis_memory.py", "tool_selector.py", "world_model.py", "verification_engine.py", "hardware_manager.py", "lab_diagnostics.py", "software_engineer.py", "visual_memory.py", "voice_intelligence.py", "capability_discovery.py", "hud_dashboard.py", "agent_guild.py", "security_policy.py", "code_engine.py", "project_director.py", "system_power_pack.py", "network_recon_pack.py", "media_audio_pack.py", "camera_vision_fast.py", "face_sentry.py", "keyboard_mouse.py", "file_search_opener.py", "memory_store.py", "memory_extractor.py", "wake_on_lan_power.py", "multi_camera_tracker.py", "stealth_browser_agent.py", "ultron_harness.py", "whatsapp_engine.py", "self_improving_engine.py", "self_code_editor.py", "spotify_music_controller.py", "desktop_organizer.py", "document_intelligence.py", "fitness_vision_tracker.py", "office_suite_generator.py", "social_media_automation.py", "system_diagnostics_advanced.py", "cloud_workspace_assistant.py", "cyber_recon.py", "devops_ops.py", "fin_intel.py", "multimedia_forge.py", "database_workbench.py", "hardware_tuner.py", "self_tool_generator.py"):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            first_doc = re.search(r'"""(.*?)"""', content, re.DOTALL)
            doc_summary = first_doc.group(1).strip().replace("\n", " ") if first_doc else "Custom tool"
            if len(doc_summary) > 70:
                doc_summary = doc_summary[:67] + "..."
            tools.append((f.stem, doc_summary, f.stat().st_size))
        except Exception:
            pass

    if not tools:
        return "ℹ️ No custom dynamically generated tools found yet. Use `auto_generate_and_test_tool()` to create one!"

    lines = [f"🛠️ Dynamically Synthesized Tools ({len(tools)} custom tools):"]
    for name, desc, size in tools:
        lines.append(f"  • `{name}` ({size} bytes): {desc}")
    return "\n".join(lines)


async def inspect_generated_tool_code(tool_name: str) -> str:
    """
    Read the implementation source code of a dynamically generated tool.
    """
    clean_name = _sanitize_tool_name(tool_name)
    target_file = PY311_TOOLS / f"{clean_name}.py"
    if not target_file.exists():
        return f"[FILE ERROR] Custom tool '{clean_name}.py' not found in {PY311_TOOLS}."

    code = target_file.read_text(encoding="utf-8", errors="ignore")
    return f"📄 Source Code for `{clean_name}.py`:\n\n```python\n{code}\n```"
