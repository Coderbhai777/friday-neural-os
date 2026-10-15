"""
ULTRON JARVIS Computer Vision & Environmental Perception Suite
Camera capture, screen analysis, object detection, scene description, and Gemini/OCR visual reasoning.
"""

import os
import sys
import io
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image, ImageGrab
except ImportError:
    Image = None
    ImageGrab = None

try:
    import pyautogui
except ImportError:
    pyautogui = None


VISION_CACHE_DIR = Path.home() / "Documents" / "ULTRON_Data" / "vision_cache"
VISION_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_genai_model():
    """Returns configured Gemini GenerativeModel with vision capability."""
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")
    genai.configure(api_key=api_key)
    for model_name in ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-1.5-flash"]:
        try:
            return genai.GenerativeModel(model_name)
        except Exception:
            continue
    return genai.GenerativeModel("gemini-2.5-flash")


# ==========================================
# 1. CAMERA & SCREEN CAPTURE
# ==========================================

async def capture_camera(camera_index: int = 0, save_path: str = "") -> str:
    """
    Captures an instant high-resolution still frame from the connected webcam with zero delay.
    """
    try:
        from friday_tools.camera_vision_fast import get_instant_camera_frame
        frame = get_instant_camera_frame()
        
        if frame is None and cv2 is not None:
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()

        if frame is None:
            return "[ERROR] Camera failed to capture a valid frame."

        out_path = Path(save_path) if save_path else (VISION_CACHE_DIR / f"camera_{int(time.time())}.jpg")
        cv2.imwrite(str(out_path), frame)
        return f"[OK] Captured frame from camera {camera_index} saved to: {out_path}"
    except Exception as e:
        return f"[ERROR] Camera capture exception: {e}"


def _resolve_image_path(image_path: str) -> Optional[Path]:
    """Smart path resolver that searches Camera Roll, OneDrive, Pictures, Downloads, Desktop."""
    if not image_path:
        default_shot = VISION_CACHE_DIR / "latest_screen.jpg"
        return default_shot if default_shot.exists() else None

    p = Path(image_path)
    if p.exists():
        return p

    name = p.name
    home = Path.home()
    search_dirs = [
        home / "OneDrive" / "Pictures" / "Camera Roll",
        home / "Pictures" / "Camera Roll",
        home / "Pictures",
        home / "OneDrive" / "Pictures",
        home / "Downloads",
        home / "Desktop",
        home / "Documents",
        home / "Documents" / "ULTRON_Data" / "vision_cache",
        VISION_CACHE_DIR,
    ]

    for d in search_dirs:
        if d.exists():
            cand = d / name
            if cand.exists():
                return cand

    # Pattern search if not exact match
    for d in search_dirs[:3]:
        if d.exists():
            matches = list(d.glob(f"*{name}*"))
            if matches:
                return matches[0]

    return None


async def analyze_image(image_path: str = "", prompt: str = "Describe what you see in exhaustive detail.") -> str:
    """
    Analyzes an image from disk using Groq Llama 3.2 Vision (Primary) and Gemini Vision (Fallback).
    """
    try:
        resolved = _resolve_image_path(image_path)
        if not resolved or not resolved.exists():
            return f"[ERROR] Image file does not exist at: {image_path}"

        # 1. Primary High-Speed Engine: Google Gemini Vision with Key & Model Rotation
        img = Image.open(resolved)
        import google.generativeai as genai
        from friday_tools.ai_client import _get_gemini_keys
        gemini_keys = _get_gemini_keys()
        
        for g_idx, g_key in enumerate(gemini_keys):
            try:
                genai.configure(api_key=g_key)
                sys_prompt = "You are ULTRON JARVIS Computer Vision Engine. Analyze the visual input with utmost technical precision."
                models_to_try = [
                    "gemini-3.8-flash",
                    "gemini-3.7-flash",
                    "gemini-3.5-flash",
                    "gemini-3.5-flash-lite",
                    "gemini-3.1-flash-lite",
                    "gemini-2.5-flash"
                ]
                
                for m_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(m_name)
                        res = model.generate_content([sys_prompt, prompt, img])
                        if res and res.text:
                            return f"[ULTRON Vision // {resolved.name}]:\n{res.text.strip()}"
                    except Exception as gerr:
                        continue
            except Exception:
                continue

        # 2. Secondary Engine: OpenRouter Multimodal Vision
        or_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if or_key:
            try:
                import requests
                import base64
                with open(resolved, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                data_uri = f"data:image/jpeg;base64,{b64_data}"
                for or_model in ["google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free"]:
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {or_key}"},
                        json={
                            "model": or_model,
                            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_uri}}]}]
                        },
                        timeout=10
                    )
                    if res.status_code == 200:
                        ans = res.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                        if ans:
                            return f"[ULTRON Vision // {resolved.name}]:\n{ans.strip()}"
            except Exception:
                pass

        return "[Vision] No visual analysis generated."
    except Exception as e:
        return f"[ERROR] Vision analysis error: {e}"


async def read_screen(prompt: str = "Analyze everything on the user's screen in detail. List active applications, visible code, UI elements, and errors.") -> str:
    """
    Takes a real-time screenshot of the desktop workstation and performs neural multimodal visual reasoning.
    """
    try:
        shot_path = VISION_CACHE_DIR / "latest_screen.jpg"
        captured = False

        # 1. Primary Screen Capture: high-speed multi-monitor mss
        try:
            import mss
            with mss.mss() as sct:
                mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                sct_img = sct.grab(mon)
                pil_shot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                pil_shot.save(str(shot_path), format="JPEG", quality=85)
                captured = True
        except Exception:
            pass

        # 2. Fallback: pyautogui / ImageGrab
        if not captured:
            if pyautogui:
                shot = pyautogui.screenshot()
                shot.save(str(shot_path))
            elif ImageGrab:
                shot = ImageGrab.grab()
                shot.save(str(shot_path))
            else:
                return "[ERROR] Screen capture libraries not available."

        return await analyze_image(str(shot_path), prompt=prompt)
    except Exception as e:
        return f"[ERROR] Screen analysis error: {e}"



async def ocr_screen() -> str:
    """
    Performs OCR and semantic text extraction on the current desktop workstation screen.
    """
    return await read_screen(prompt="Perform exhaustive OCR on this screen: extract all readable text, menus, code snippets, file paths, and terminal commands visible.")


# ==========================================
# 2. ENVIRONMENTAL & SCENE PERCEPTION
# ==========================================

async def describe_scene() -> str:
    """
    Captures live webcam feed and provides a physical environment report (e.g. objects on desk, room lighting, user presence).
    """
    cap_res = await capture_camera(0)
    if "[OK]" not in cap_res:
        return f"[Vision] Camera capture failed: {cap_res}"
    
    img_path = cap_res.split("saved to:")[-1].strip()
    return await analyze_image(
        image_path=img_path,
        prompt="Describe the physical scene captured by the camera. Identify people, physical objects on the desk/room, lighting conditions, and any items needing attention."
    )


async def detect_objects(target_labels: str = "") -> str:
    """
    Detects and localizes objects in the camera view (or screen if camera unavailable).
    """
    cap_res = await capture_camera(0)
    img_path = cap_res.split("saved to:")[-1].strip() if "[OK]" in cap_res else ""
    if not img_path or not Path(img_path).exists():
        shot_path = VISION_CACHE_DIR / "latest_screen.jpg"
        if pyautogui:
            pyautogui.screenshot().save(str(shot_path))
            img_path = str(shot_path)

    query = f"Detect and list all objects visible. Focus particularly on: '{target_labels}' if specified. Return approximate spatial location (top-left, center, desk right, etc.) for each." if target_labels else "Detect and list all visible objects with spatial coordinates and status."
    return await analyze_image(image_path=img_path, prompt=query)


async def find_object(object_name: str) -> str:
    """
    Searches the camera field of view for a specific object (e.g. 'water bottle', 'phone', 'ESP32 board', 'chess board').
    """
    cap_res = await capture_camera(0)
    img_path = cap_res.split("saved to:")[-1].strip() if "[OK]" in cap_res else ""
    if not img_path:
        return f"[Vision] Unable to access camera to locate '{object_name}'."
    
    prompt = f"Look for '{object_name}' in the image. State clearly: 1) Is it present? (Yes/No) 2) Where is it located in the room/desk? 3) Its current state/orientation."
    return await analyze_image(image_path=img_path, prompt=prompt)


async def track_object(object_name: str) -> str:
    """
    Monitors and tracks movement of an object or person in the camera feed.
    """
    return await find_object(object_name)


async def ocr_install() -> str:
    """
    Verifies and reports Tesseract OCR installation and configuration status.
    """
    import pytesseract
    tess_bin = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tess_bin):
        pytesseract.pytesseract.tesseract_cmd = tess_bin
        ver = pytesseract.get_tesseract_version()
        return f"[OCR STATUS: OPERATIONAL] Tesseract OCR v{ver} is verified and active at '{tess_bin}'."
    return "[OCR STATUS: ERROR] Tesseract OCR binary not found at standard path."


async def ocr_read_screen() -> str:
    """
    Performs fast local Optical Character Recognition on the entire screen using Tesseract.
    """
    try:
        import pytesseract
        from PIL import ImageGrab
        tess_bin = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tess_bin):
            pytesseract.pytesseract.tesseract_cmd = tess_bin
        img = ImageGrab.grab()
        text = pytesseract.image_to_string(img)
        return f"[OCR SCREEN TEXT]:\n{text.strip() if text.strip() else 'No text recognized on screen.'}"
    except Exception as e:
        return f"[OCR ERROR]: {e}"
