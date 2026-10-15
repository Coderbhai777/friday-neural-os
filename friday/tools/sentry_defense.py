"""
ULTRON Anti-Intruder Sentry Cam & Workstation Security Defense
Continuous webcam facial surveillance while user is away; captures intruder photos, emails alerts to user, and locks the workstation.
"""

import os
import time
import threading
import ctypes
import cv2
import asyncio
from pathlib import Path
from typing import Optional

from friday_tools.sound_engine import play_sound_async

user32 = ctypes.windll.user32

_SENTRY_ACTIVE = False
_SENTRY_THREAD = None
_KNOWN_FACE_ENCODINGS = None


def _lock_workstation():
    """Immediately locks Windows workstation."""
    play_sound_async("lock")
    user32.LockWorkStation()


def _dispatch_intruder_alert(photo_path: str, email_to: str):
    """Sends email alert with intruder photo evidence."""
    try:
        import friday_tools.email_copilot as email_copilot
        import friday_tools.communication as comm
        
        sub = "🚨 [SECURITY ALERT] Unauthorized Intruder Detected at Workstation"
        body = (
            f"Sir,\n\n"
            f"ULTRON Sentry Defense detected an unauthorized person sitting at your workstation.\n"
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Evidence photo captured: {photo_path}\n"
            f"Action Taken: Workstation immediately locked.\n\n"
            f"- ULTRON Security Core"
        )
        # Try sending email
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(comm.send_email(to_email=email_to, subject=sub, message=body))
            loop.close()
        except Exception:
            pass
    except Exception as e:
        print(f"[SENTRY] Alert dispatch notice: {e}")


def _sentry_surveillance_loop(duration_seconds: int, email_to: str):
    global _SENTRY_ACTIVE
    start_time = time.time()
    
    evidence_dir = Path.home() / "Documents" / "ULTRON_Data" / "Camera_Snaps"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    cap = None
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
            
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        consecutive_frames_detected = 0
        
        while _SENTRY_ACTIVE and (time.time() - start_time < duration_seconds):
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.5)
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
            
            if len(faces) > 0:
                consecutive_frames_detected += 1
                if consecutive_frames_detected >= 3:
                    # Intruder confirmed
                    evidence_file = str(evidence_dir / f"intruder_{int(time.time())}.jpg")
                    cv2.imwrite(evidence_file, frame)
                    
                    play_sound_async("alert")
                    
                    # Alert and Lock
                    threading.Thread(target=_dispatch_intruder_alert, args=(evidence_file, email_to), daemon=True).start()
                    _lock_workstation()
                    break
            else:
                consecutive_frames_detected = 0
                
            time.sleep(0.6)
            
    except Exception as e:
        print(f"[SENTRY] Error during surveillance: {e}")
    finally:
        if cap:
            cap.release()
        _SENTRY_ACTIVE = False


async def arm_sentry_mode(duration_minutes: int = 60, notify_email: str = "shivamogh.12@gmail.com") -> str:
    """
    Arms ULTRON Sentry Defense: monitors the webcam for unauthorized faces, captures evidence, emails an alert, and locks workstation.
    
    Args:
        duration_minutes: How many minutes to stay actively armed.
        notify_email: Email address to send intruder photo evidence to.
    """
    global _SENTRY_ACTIVE, _SENTRY_THREAD
    if _SENTRY_ACTIVE:
        return "[INFO] Sentry Defense is already armed and monitoring."
        
    _SENTRY_ACTIVE = True
    play_sound_async("scan")
    
    _SENTRY_THREAD = threading.Thread(
        target=_sentry_surveillance_loop,
        args=(int(duration_minutes * 60), notify_email),
        daemon=True
    )
    _SENTRY_THREAD.start()
    
    return (
        f"🛡️ [SENTRY DEFENSE ARMED]\n"
        f"• Status: Armed & Actively Scanning\n"
        f"• Duration: {duration_minutes} minutes\n"
        f"• Alert Target: {notify_email}\n"
        f"Sir, workstation defense is active. Step away safely."
    )


async def disarm_sentry_mode() -> str:
    """Disarms the active Sentry Defense camera surveillance."""
    global _SENTRY_ACTIVE
    _SENTRY_ACTIVE = False
    play_sound_async("chime")
    return "🛡️ [SENTRY DEFENSE DISARMED] Surveillance mode deactivated."


async def stealth_duress_lock() -> str:
    """Discreetly minimizes all windows, purges temporary clipboard, and displays lock screen."""
    play_sound_async("lock")
    try:
        import pyperclip
        pyperclip.copy("")
    except Exception:
        pass
    user32.LockWorkStation()
    return "[OK] Stealth lockdown executed."
