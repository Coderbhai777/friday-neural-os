"""
ULTRON High-Speed Camera Vision & Person Identification Engine
Provides sub-second camera frame capture with zero hardware lockups,
and multimodal identity & scene recognition using Groq Vision (Primary) & Gemini Flash Vision (Fallback).
"""

import os
import io
import time
import base64
from pathlib import Path
from typing import Optional

try:
    import cv2
except ImportError:
    cv2 = None

from PIL import Image

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

VISION_DIR = Path.home() / "Documents" / "ULTRON_Data" / "vision_cache"
VISION_DIR.mkdir(parents=True, exist_ok=True)


def get_instant_camera_frame():
    """
    Grabs the camera frame with zero lag:
    1. Grabs live frame cache from AirGestureWorker / Sagar Orb if active.
    2. Fallback to direct OpenCV DirectShow grab (<150ms) across camera indices.
    """
    # Strategy 1: Shared frame buffer from active worker
    try:
        from aria_modules.sagar_orb_widget import get_latest_camera_frame
        frame = get_latest_camera_frame()
        if frame is not None:
            return frame
    except Exception:
        pass

    if cv2 is None:
        return None

    # Strategy 2: DirectShow capture across camera indices (0, 1)
    for idx in [0, 1]:
        try:
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(idx)
            
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                # Read 2 frames to flush auto-exposure buffer
                cap.read()
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    return frame
        except Exception:
            continue

    return None


async def identify_person_in_camera(
    question: str = "Who is in front of the camera?",
    prompt: str = "",
    query: str = "",
    **kwargs
) -> str:
    """
    Instantly activates the camera to identify the person, facial features, expression, clothing, and activity.
    """
    actual_question = (question or prompt or query or "Who is in front of the camera? Describe them accurately.").strip()

    frame = get_instant_camera_frame()
    if frame is None:
        return "[CAMERA ERROR] Could not access webcam. Ensure the camera is connected and not locked by another application."

    try:
        # Convert BGR (OpenCV) to RGB (PIL)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)

        # Scale down for fast transmission
        max_dim = 1024
        if max(img.width, img.height) > max_dim:
            scale = max_dim / max(img.width, img.height)
            img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)

        # Save cached frame
        cache_path = VISION_DIR / "latest_camera_person.jpg"
        img.save(str(cache_path), format="JPEG", quality=85)

        # Encode to base64 JPEG
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        img_bytes = buf.getvalue()

        from aria_modules.vision_core import analyze_image_fast
        
        sys_prompt = (
            f"Examine the person in front of the camera. "
            f"Confirm if the person is Shivansh (the creator/master), describe their facial features, clothing, expression, and current action. "
            f"Specific inquiry: {actual_question}"
        )
        
        res = analyze_image_fast(img_bytes, prompt=sys_prompt)
        if res and "❌" not in res and "Vision analysis completed without text response" not in res:
            return f"[CAMERA IDENTIFICATION]\n{res}"

        return f"[CAMERA IDENTIFICATION]\n{res}"
    except Exception as e:
        return f"[CAMERA ERROR] Error during person identification: {e}"


async def capture_fast_camera_image(
    prompt: str = "Describe everything visible in front of the camera.",
    save_path: str = "",
    question: str = "",
    **kwargs
) -> str:
    """
    Sub-second camera snapshot and multimodal scene description.
    """
    actual_prompt = (prompt or question or "Describe everything visible in front of the camera.").strip()
    frame = get_instant_camera_frame()
    if frame is None:
        return "[CAMERA ERROR] Could not capture frame from webcam."

    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)

        out_path = Path(save_path) if save_path else (VISION_DIR / f"camera_fast_{int(time.time())}.jpg")
        img.save(str(out_path), format="JPEG", quality=85)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        img_bytes = buf.getvalue()

        from aria_modules.vision_core import analyze_image_fast
        res = analyze_image_fast(img_bytes, prompt=actual_prompt)
        return f"[CAMERA SCENE]\nSaved: {out_path}\nAnalysis:\n{res}"
    except Exception as e:
        return f"[CAMERA ERROR] Fast capture error: {e}"


async def who_is_in_camera(**kwargs) -> str:
    """
    Convenience wrapper for asking who is currently in front of the camera.
    """
    return await identify_person_in_camera(question="Who is in front of the camera?", **kwargs)
