"""
ULTRON Homework Solver Module
Provides step-by-step homework solutions, visual problem solving from screen/webcam, and conceptual explanations.
"""

import asyncio
import io
import os
from typing import Optional


async def solve_homework(subject: str = 'general') -> str:
    """
    Captures the current screen and provides a complete step-by-step solution
    for any homework problem visible on display.
    """
    try:
        import pyautogui
        from aria_modules.vision_core import analyze_image_fast

        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80)
        img_bytes = buf.getvalue()

        prompt = (
            f"You are a brilliant tutor. The student has a {subject} question visible on screen. "
            "Read the question carefully and provide a COMPLETE step-by-step solution. "
            "Show all working. If it's math, show each step. If it's science, explain the concept. "
            "If it's an essay question, provide a structured answer."
        )

        return analyze_image_fast(img_bytes, prompt)
    except Exception as e:
        return f"❌ Error solving homework from screen: {e}"


async def solve_from_photo() -> str:
    """
    Captures an instant frame from the webcam (e.g. textbook page, handwritten notebook)
    and sends it to Gemini Vision for a comprehensive step-by-step solution.
    """
    try:
        import cv2
        from aria_modules.vision_core import analyze_image_fast
        from friday_tools.camera_vision_fast import get_instant_camera_frame

        frame = get_instant_camera_frame()
        if frame is None:
            return "❌ Error: Could not access webcam. Please check camera connection."

        success, encoded_img = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not success:
            return "❌ Error: Failed to encode webcam frame to JPEG format."

        img_bytes = encoded_img.tobytes()

        prompt = (
            "You are ULTRON Academic Problem Solver. The student has provided a photo of a homework or technical question. "
            "Read the question carefully and provide a COMPLETE step-by-step solution. "
            "Show all working. If it's math, show each step. If it's science, explain the concept. "
            "If it's an essay question, provide a structured answer."
        )

        return analyze_image_fast(img_bytes, prompt)
    except Exception as e:
        return f"❌ Error solving homework from photo: {e}"


async def _ai_text(prompt: str) -> str:
    # 1. Primary: Ollama / Qwen Coder Cloud API
    ollama_key = os.getenv("OLLAMA_API_KEY", "").strip() or "3cfdf2b08fa14833bed51e8640da422b.72X4A7EtBne6lmLR2wo2vwn6"
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen3-coder-next")
    
    if ollama_key:
        import requests
        endpoints = [
            ("https://open.bigmodel.cn/api/paas/v4/chat/completions", {"model": ollama_model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}),
            ("https://open.bigmodel.cn/api/paas/v4/chat/completions", {"model": "codegeex-4", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}),
            ("https://open.bigmodel.cn/api/paas/v4/chat/completions", {"model": "glm-4-flash", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}),
        ]
        for url, payload in endpoints:
            try:
                res = requests.post(url, json=payload, headers={"Authorization": f"Bearer {ollama_key}"}, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    if content:
                        return content
            except Exception:
                continue

    # 2. Gemini fallback
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            for m in ['gemini-3.6-flash', 'gemini-2.5-flash']:
                try:
                    model = genai.GenerativeModel(m)
                    res = model.generate_content(prompt)
                    if res and res.text:
                        return res.text.strip()
                except Exception:
                    continue
        except Exception:
            pass

    # 3. Groq fallback (GPT-120B / GPT-20B / Qwen)
    try:
        from friday_tools.ai_client import _get_groq_keys
        groq_keys = _get_groq_keys()
        if groq_keys:
            import groq
            for gkey in groq_keys:
                for gmodel in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]:
                    try:
                        client = groq.Groq(api_key=gkey)
                        chat = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model=gmodel,
                            max_tokens=1500,
                            temperature=0.6,
                        )
                        if chat.choices and chat.choices[0].message.content:
                            return chat.choices[0].message.content.strip()
                    except Exception:
                        continue
    except Exception:
        pass

    return "AI inference currently unavailable."


async def solve_math(equation: str) -> str:
    """
    Solves a mathematical equation or problem step by step with full working.
    """
    try:
        prompt = f"Solve this step by step showing all working: {equation}"
        return await _ai_text(prompt)
    except Exception as e:
        return f"Error solving math problem: {e}"


async def explain_concept(topic: str, level: str = 'high school') -> str:
    """
    Explains an academic or technical concept tailored to a specific comprehension level.
    """
    try:
        prompt = f"Explain {topic} at a {level} level. Use examples, analogies, and diagrams described in text. Make it easy to understand."
        return await _ai_text(prompt)
    except Exception as e:
        return f"Error explaining concept '{topic}': {e}"
