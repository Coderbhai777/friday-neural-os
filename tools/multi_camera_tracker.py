"""
ULTRON Multi-Camera & Multi-Display Vision Tracker Module
Enables dynamic discovery of all connected webcams/capture devices, source switching,
high-speed frame acquisition, and multi-monitor screen spatial tracking.
"""

import cv2
import asyncio
import os
from typing import List, Dict, Any, Optional

async def list_connected_cameras(max_devices: int = 5) -> str:
    """
    Probes video capture devices on index 0 to max_devices to find all active webcams, virtual cameras, and USB capture cards.
    """
    def _probe_sync():
        available = []
        for idx in range(max_devices):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                if ret or w > 0:
                    available.append(f"- Camera Index {idx}: Active ({w}x{h} resolution)")
        return available

    cams = await asyncio.to_thread(_probe_sync)
    if not cams:
        return "[CAMERAS] No video capture devices detected."
    return f"[CONNECTED CAMERAS] Found {len(cams)} video source(s):\n" + "\n".join(cams)


async def capture_camera_snapshot(camera_index: int = 0, output_filename: str = "camera_snapshot.jpg") -> str:
    """
    Captures a high-resolution snapshot from the specified camera index and saves it to ULTRON_Data.
    """
    def _capture():
        out_dir = os.path.expanduser(r"~\Documents\ULTRON_Data\snapshots")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, output_filename)

        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            return f"[ERROR] Could not open camera at index {camera_index}."

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Warmup
        for _ in range(5):
            cap.read()

        ret, frame = cap.read()
        cap.release()

        if ret and frame is not None:
            cv2.imwrite(out_path, frame)
            return f"[OK] Captured snapshot from camera {camera_index} -> {out_path}."
        return f"[ERROR] Failed to capture frame from camera {camera_index}."

    return await asyncio.to_thread(_capture)
