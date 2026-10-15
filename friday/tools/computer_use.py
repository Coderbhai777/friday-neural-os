"""
ULTRON Autonomous Computer Use & Screen Perception Engine
Enables continuous visual screen perception, zero-click OCR/vision analysis,
and autonomous UI element location & clicking via Gemini Vision + MSS + PyAutoGUI.
"""

import asyncio
import io
import json
import os
import re
import time
from typing import Optional
from PIL import Image

def take_screenshot() -> Image.Image:
    """Fast, reliable screen capture using MSS (Primary) with PIL and PyAutoGUI fallbacks."""
    try:
        import mss
        with mss.mss() as sct:
            mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            s_img = sct.grab(mon)
            return Image.frombytes("RGB", s_img.size, s_img.bgra, "raw", "BGRX")
    except Exception:
        try:
            from PIL import ImageGrab
            return ImageGrab.grab(all_screens=True)
        except Exception:
            import pyautogui
            return pyautogui.screenshot()


def _parse_json_action(text: str) -> dict:
    """Helper to extract and parse JSON object from model output."""
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean).strip()

    try:
        return json.loads(clean)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", clean)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Could not extract valid JSON from response: {text}")


async def screen_analyze(question: str = "Describe everything currently visible on the screen in detail.") -> str:
    """
    Instantly captures the active desktop screen and uses Multi-Modal Vision to analyze and answer questions.
    Requires zero buttons or manual input.
    """
    try:
        from aria_modules.vision_core import analyze_image_fast

        img = take_screenshot()
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        img_bytes = buf.getvalue()

        actual_prompt = question.strip() if question.strip() else "Describe everything currently visible on the screen in detail."
        res = analyze_image_fast(img_bytes, prompt=actual_prompt)
        return res
    except Exception as e:
        return f"[SCREEN VISION ERROR] {e}"


async def find_and_click(element: str) -> str:
    """
    Captures the screen, locates the UI element using Gemini Vision coordinates, and clicks it accurately.
    """
    try:
        import pyautogui
        from aria_modules.vision_core import analyze_image_fast

        pyautogui.FAILSAFE = False

        img = take_screenshot()
        screen_w, screen_h = img.size

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        img_bytes = buf.getvalue()

        prompt = (
            f"Find the UI element described as '{element}' on this screen and return its exact pixel coordinates.\n"
            f"Screen Resolution: {screen_w}x{screen_h} pixels.\n"
            'Return ONLY valid raw JSON with this exact schema: {"x": int, "y": int, "reasoning": str}\n'
            f"Ensure x is between 0 and {screen_w}, and y is between 0 and {screen_h}."
        )

        response = analyze_image_fast(img_bytes, prompt)
        if not response or response.startswith("❌"):
            return f"Could not locate '{element}' on screen: {response}"

        data = _parse_json_action(response)
        x = int(float(data.get("x", screen_w // 2)))
        y = int(float(data.get("y", screen_h // 2)))

        # Clamp coordinates to screen boundaries
        x = max(0, min(screen_w - 1, x))
        y = max(0, min(screen_h - 1, y))

        pyautogui.moveTo(x, y, duration=0.25)
        pyautogui.click(x, y)
        reasoning = data.get("reasoning", "Element found and clicked")
        return f"Clicked on '{element}' at ({x}, {y}). {reasoning}"

    except Exception as e:
        return f"[CLICK ERROR] Failed to find and click '{element}': {e}"


async def computer_use(task: str, max_steps: int = 8) -> str:
    """
    Autonomous computer control agent loop for multi-step tasks.
    """
    try:
        import pyautogui
        from aria_modules.vision_core import analyze_image_fast

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.3

        actions_taken = []

        for step in range(1, max_steps + 1):
            img = take_screenshot()
            screen_w, screen_h = img.size

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80)
            img_bytes = buf.getvalue()

            prompt = (
                f'You are an autonomous computer control agent executing the task: "{task}"\n'
                f"Current Step: {step}/{max_steps}\n"
                f"Screen Resolution: {screen_w}x{screen_h} pixels\n\n"
                "Analyze the current screen and decide the next single action to accomplish the task.\n"
                "Return ONLY a JSON object with this exact structure:\n"
                "{\n"
                '  "action": "click" | "type" | "hotkey" | "scroll" | "done",\n'
                '  "x": int,\n'
                '  "y": int,\n'
                '  "text": str,\n'
                '  "keys": str,\n'
                '  "amount": int,\n'
                '  "reasoning": str\n'
                "}\n"
            )

            raw_response = analyze_image_fast(img_bytes, prompt)
            try:
                action_data = _parse_json_action(raw_response)
            except Exception:
                actions_taken.append(f"Step {step}: Vision response parsing error")
                continue

            action = str(action_data.get("action", "")).strip().lower()
            reasoning = str(action_data.get("reasoning", "")).strip()

            if action == "click":
                x = max(0, min(screen_w - 1, int(float(action_data.get("x", screen_w // 2)))))
                y = max(0, min(screen_h - 1, int(float(action_data.get("y", screen_h // 2)))))
                pyautogui.moveTo(x, y, duration=0.2)
                pyautogui.click(x, y)
                actions_taken.append(f"Clicked ({x}, {y})")

            elif action == "type":
                text_to_type = str(action_data.get("text", ""))
                pyautogui.write(text_to_type)
                actions_taken.append(f"Typed '{text_to_type}'")

            elif action == "hotkey":
                keys_str = str(action_data.get("keys", ""))
                keys = [k.strip() for k in keys_str.split("+") if k.strip()]
                if keys:
                    pyautogui.hotkey(*keys)
                    actions_taken.append(f"Pressed {'+'.join(keys)}")

            elif action == "scroll":
                amount = int(float(action_data.get("amount", -200)))
                pyautogui.scroll(amount)
                actions_taken.append(f"Scrolled {amount}")

            elif action == "done":
                actions_taken.append("Task completed")
                return f"{reasoning}\n\nExecution: " + ", ".join(actions_taken)

            await asyncio.sleep(0.8)

        return f"Completed steps for task '{task}'.\n\nActions: " + ", ".join(actions_taken)

    except Exception as e:
        return f"[COMPUTER USE ERROR] {e}"
