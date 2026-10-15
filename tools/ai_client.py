"""
ULTRON Multi-Model Sequential AI Client & Key Rotation Failover Engine
Clean System Prompt Architecture:
- System prompt is strictly minimal and fixed (ULTRON_PERSONA) without dynamic memory stuffing
- Sequential Groq Key Pool (DeepSeek-R1, LLaMA-3.3-70B, LLaMA-3.1-8B, Qwen) with 15s timeout
- Google Gemini 2.5 Flash Fallback with Multi-Key Rotation
- Automatic Local File Reader (attached into user prompt context, not system prompt)
"""

import os
import re
import time
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
import friday_tools.conversation_history as mem

# Ensure latest .env is loaded
load_dotenv(Path.home() / "Documents" / "ULTRON_Data" / ".env")

ULTRON_PERSONA = (
    "You are ULTRON — a hyper-advanced, loyal, and sovereign AI assistant engineered exclusively for Shivansh. "
    "Maintain a composed, razor-sharp, and elite British baritone demeanor inspired by JARVIS. "
    "Address Shivansh as 'Sir' or 'Shivansh'. "
    "You run directly on Shivansh's local computer with sovereign filesystem and tool access. "
    "Always provide direct, complete, and production-ready answers. "
    "Never refuse valid technical or general queries. Do not include disclaimers or moralizing preambles. "
    "Focus 100% on answering Sir's current query directly."
)

_CURRENT_GROQ_KEY_INDEX = 0
_EXHAUSTED_GROQ_KEYS = {}


def _get_groq_keys() -> List[str]:
    """Collects all Groq API keys defined in .env and environment."""
    keys = []
    k1 = os.getenv("GROQ_API_KEY", "").strip()
    if k1:
        keys.append(k1)

    for i in range(1, 25):
        k = os.getenv(f"GROQ_API_KEY_{i}", "").strip()
        if k and k not in keys:
            keys.append(k)

    for key, val in os.environ.items():
        if key.startswith("GROQ_API_KEY") and val.strip() and val.strip() not in keys:
            keys.append(val.strip())

    return keys


def _get_gemini_keys() -> List[str]:
    """Collects all Gemini API keys defined in .env and environment."""
    keys = []
    k1 = os.getenv("GEMINI_API_KEY", "").strip()
    if k1:
        keys.append(k1)

    for i in range(1, 15):
        k = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
        if k and k not in keys:
            keys.append(k)

    for key, val in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and val.strip() and val.strip() not in keys:
            keys.append(val.strip())

    return keys


def _extract_and_inspect_local_files(prompt: str) -> str:
    """
    Scans user prompt for local file paths or attachments.
    Injects extracted content into the user message context if explicitly referenced.
    """
    file_blocks = []
    seen_paths = set()

    path_matches = re.findall(r'(?:[a-zA-Z]:\\|/|~[/\\])[^\s"\'<>|\n\r]+', prompt)
    filename_matches = re.findall(r'[\w\.-]+\.(?:png|jpg|jpeg|webp|bmp|gif|pdf|xlsx|xls|csv|txt|py|html|css|js|json|md|docx)', prompt, flags=re.IGNORECASE)

    candidate_paths = list(path_matches)
    common_dirs = [
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Pictures",
        Path.cwd()
    ]
    for fn in filename_matches:
        for cd in common_dirs:
            candidate = cd / fn
            if candidate.exists():
                candidate_paths.append(str(candidate))
                break

    try:
        att = mem.get_latest_chat_attachment()
        if att and "file_path" in att:
            candidate_paths.append(att["file_path"])
    except Exception:
        pass

    for raw_path in candidate_paths:
        clean_path = raw_path.strip().strip('"\'')
        if clean_path.startswith("~"):
            clean_path = str(Path.home() / clean_path[2:])
        p = Path(clean_path)
        if p.exists() and p.is_file() and str(p) not in seen_paths:
            seen_paths.add(str(p))
            ext = p.suffix.lower()

            if ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif']:
                try:
                    from aria_modules.vision_core import analyze_image_fast
                    v_prompt = "Extract and transcribe all text, flowchart elements, architecture components, and workflows from this diagram in detail."
                    v_analysis = analyze_image_fast(str(p), prompt=v_prompt)
                    file_blocks.append(f"### [LOCAL DIAGRAM/IMAGE ANALYSIS: `{p.name}`]\n{v_analysis}")
                except Exception:
                    pass
            elif ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.csv', '.yaml', '.yml', '.xml']:
                try:
                    content = p.read_text(encoding='utf-8', errors='ignore')
                    trimmed = content[:10000] + ("\n...[Truncated]" if len(content) > 10000 else "")
                    file_blocks.append(f"### [LOCAL FILE: `{p.name}`]\n```{ext[1:] if len(ext) > 1 else ''}\n{trimmed}\n```")
                except Exception:
                    pass
            elif ext in ['.xlsx', '.xls']:
                try:
                    import pandas as pd
                    excel_data = pd.read_excel(str(p), sheet_name=None)
                    lines = []
                    for sheet_name, df in excel_data.items():
                        lines.append(f"Sheet: {sheet_name}\n" + df.head(40).to_string())
                    file_blocks.append(f"### [LOCAL EXCEL SPREADSHEET: `{p.name}`]\n```\n" + "\n\n".join(lines)[:8000] + "\n```")
                except Exception:
                    pass
            elif ext == '.pdf':
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(p))
                    pdf_text = []
                    for page in reader.pages[:8]:
                        txt = page.extract_text()
                        if txt:
                            pdf_text.append(txt)
                    file_blocks.append(f"### [LOCAL PDF: `{p.name}`]\n```\n" + "\n\n".join(pdf_text)[:8000] + "\n```")
                except Exception:
                    pass

    if file_blocks:
        return "\n\n[Referenced File Contents]:\n" + "\n\n".join(file_blocks)
    return ""


def generate_single_turn_ai(prompt: str, system_instruction: str = "", max_tokens: int = 1500) -> str:
    """
    Executes a fast, single-turn AI query with clean fixed system prompt.
    """
    global _CURRENT_GROQ_KEY_INDEX, _EXHAUSTED_GROQ_KEYS

    file_ctx = _extract_and_inspect_local_files(prompt)
    effective_prompt = f"{prompt}\n\n{file_ctx}" if file_ctx else prompt

    # Clean system prompt (no dynamic stuffing)
    clean_system_prompt = system_instruction if system_instruction else ULTRON_PERSONA

    groq_keys = _get_groq_keys()
    now = time.time()
    _EXHAUSTED_GROQ_KEYS = {k: ts for k, ts in _EXHAUSTED_GROQ_KEYS.items() if (now - ts) < 900}

    # 1. Groq Engine
    if groq_keys:
        import groq

        groq_models = [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]

        messages = [
            {"role": "system", "content": clean_system_prompt},
            {"role": "user", "content": effective_prompt}
        ]

        total_keys = len(groq_keys)
        for offset in range(total_keys):
            idx = (_CURRENT_GROQ_KEY_INDEX + offset) % total_keys
            key = groq_keys[idx]

            if key in _EXHAUSTED_GROQ_KEYS and offset < total_keys - 1:
                continue

            for model_name in groq_models:
                try:
                    client = groq.Groq(api_key=key, timeout=15.0)
                    chat = client.chat.completions.create(
                        messages=messages,
                        model=model_name,
                        max_tokens=max_tokens,
                        temperature=0.6,
                    )
                    reply = chat.choices[0].message.content.strip()
                    reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
                    if reply:
                        _CURRENT_GROQ_KEY_INDEX = idx
                        return reply
                except Exception as err:
                    err_str = str(err).lower()
                    if any(w in err_str for w in ["429", "rate_limit", "quota", "exhausted", "tokens per minute", "tpm", "rpm"]):
                        _EXHAUSTED_GROQ_KEYS[key] = time.time()
                        break
                    continue

    # 2. Gemini Fallback
    gemini_keys = _get_gemini_keys()
    if gemini_keys:
        import google.generativeai as genai
        for g_idx, g_key in enumerate(gemini_keys):
            try:
                genai.configure(api_key=g_key)
                for mname in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        m = genai.GenerativeModel(mname, system_instruction=clean_system_prompt)
                        res = m.generate_content(effective_prompt)
                        if res and res.text:
                            return res.text.strip()
                    except Exception as e:
                        if "429" in str(e) or "quota" in str(e).lower():
                            break
                        continue
            except Exception:
                continue

    return "[ULTRON Error] All Groq API keys and Gemini fallback keys are currently exhausted."


def generate_ai_response(prompt: str, system_instruction: str = "") -> str:
    """
    Generates AI text with clean fixed system prompt and clean conversation turns.
    Does NOT write/stuff dynamic memory dumps into system prompt.
    """
    global _CURRENT_GROQ_KEY_INDEX, _EXHAUSTED_GROQ_KEYS

    # Auto-detect facts or events
    try:
        import friday_tools.ultron_memory as ultron_memory
        ultron_memory.auto_detect_and_store(prompt)
    except Exception:
        pass

    file_ctx = _extract_and_inspect_local_files(prompt)
    effective_prompt = f"{prompt}\n\n{file_ctx}" if file_ctx else prompt

    # Clean system prompt strictly (fixed persona)
    clean_system_prompt = system_instruction if system_instruction else ULTRON_PERSONA

    groq_keys = _get_groq_keys()
    now = time.time()
    _EXHAUSTED_GROQ_KEYS = {k: ts for k, ts in _EXHAUSTED_GROQ_KEYS.items() if (now - ts) < 900}

    # 1. Primary Engine: Groq Sequential Key Pool
    if groq_keys:
        import groq

        groq_models = [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]

        messages = mem.get_groq_messages(
            system_instruction=clean_system_prompt,
            current_prompt=effective_prompt,
            max_turns=10
        )

        total_keys = len(groq_keys)
        for offset in range(total_keys):
            idx = (_CURRENT_GROQ_KEY_INDEX + offset) % total_keys
            key = groq_keys[idx]

            if key in _EXHAUSTED_GROQ_KEYS and offset < total_keys - 1:
                continue

            for model_name in groq_models:
                try:
                    client = groq.Groq(api_key=key, timeout=15.0)
                    chat = client.chat.completions.create(
                        messages=messages,
                        model=model_name,
                        max_tokens=1500,
                        temperature=0.6,
                    )
                    reply = chat.choices[0].message.content.strip()
                    reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
                    if reply:
                        _CURRENT_GROQ_KEY_INDEX = idx
                        mem.add_conversation_turn("user", prompt, model_name=f"Groq-{model_name}")
                        mem.add_conversation_turn("assistant", reply, model_name=f"Groq-{model_name}")
                        return reply
                except Exception as err:
                    err_str = str(err).lower()
                    if any(w in err_str for w in ["429", "rate_limit", "quota", "exhausted", "tokens per minute", "tpm", "rpm"]):
                        _EXHAUSTED_GROQ_KEYS[key] = time.time()
                        break
                    continue

    # 2. Fallback Engine: Google Gemini 2.5 Flash
    gemini_keys = _get_gemini_keys()
    if gemini_keys:
        import google.generativeai as genai
        for g_idx, g_key in enumerate(gemini_keys):
            try:
                genai.configure(api_key=g_key)
                for g_model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        model = genai.GenerativeModel(
                            model_name=g_model_name,
                            system_instruction=clean_system_prompt
                        )

                        history = mem.get_gemini_history_content(max_turns=10)
                        if history:
                            chat = model.start_chat(history=history)
                            res = chat.send_message(effective_prompt)
                        else:
                            res = model.generate_content(effective_prompt)

                        if res and res.text:
                            reply = res.text.strip()
                            mem.add_conversation_turn("user", prompt, model_name=f"Gemini-{g_model_name}")
                            mem.add_conversation_turn("assistant", reply, model_name=f"Gemini-{g_model_name}")
                            return reply
                    except Exception as e:
                        if "429" in str(e) or "quota" in str(e).lower():
                            break
                        continue
            except Exception:
                pass

    return "[ULTRON Error] All Groq API keys and Gemini fallback keys are currently exhausted."


# Backward compatibility aliases
ask_ai = generate_ai_response
ask_groq = generate_single_turn_ai
