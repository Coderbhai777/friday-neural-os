"""
JARVIS Audible Alarm & Voice Announcer Subsystem
Created for Shivansh Sagar Pancholi

Features:
- Windows-native high-fidelity sci-fi audible chimes and alarm klaxons (via sound_engine / winsound).
- Seamless integration with existing RyanNeural British voice (via tts_engine).
- Coordinated announcement queue: prevents audio collision or speech overlap when multiple events fire.
- Differentiates alarm behaviors for timers vs. reminders.
- Thread-safe alarm acknowledgement, snooze, and immediate interruption.
"""

import os
import sys
import time
import queue
import threading
from typing import Optional, Dict, Any

# Import existing audio and TTS engines
try:
    from friday_tools.sound_engine import play_sound_async
except ImportError:
    try:
        from tools.sound_engine import play_sound_async
    except ImportError:
        def play_sound_async(st="chime"):
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

try:
    from friday_tools.tts_engine import speak_text_sync, stop_speech
except ImportError:
    try:
        from tools.tts_engine import speak_text_sync, stop_speech
    except ImportError:
        def speak_text_sync(text):
            print(f"[JARVIS SPEECH]: {text}")
        def stop_speech():
            pass


class AlarmAnnouncer:
    """Thread-safe alarm and voice announcement dispatcher with sequential queue."""

    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._is_ringing = False
        self._stop_requested = False
        self._lock = threading.Lock()
        self._worker_thread: Optional[threading.Thread] = None
        self._current_event_id: Optional[str] = None
        self._ensure_worker()

    def _ensure_worker(self):
        with self._lock:
            if self._worker_thread is None or not self._worker_thread.is_alive():
                self._worker_thread = threading.Thread(target=self._queue_consumer, daemon=True)
                self._worker_thread.start()

    def enqueue_alert(self, event: Dict[str, Any]):
        """Queues an event to be alerted and spoken aloud."""
        self._ensure_worker()
        self._queue.put(event)

    def stop_alarm(self):
        """Immediately silences any active alarm chime and voice playback."""
        with self._lock:
            self._stop_requested = True
            self._is_ringing = False
        stop_speech()

    @property
    def is_ringing(self) -> bool:
        return self._is_ringing

    @property
    def current_event_id(self) -> Optional[str]:
        return self._current_event_id

    def _queue_consumer(self):
        """Sequential queue consumer running in background daemon thread."""
        while True:
            try:
                event = self._queue.get()
                if not event:
                    continue

                event_id = event.get("id")
                event_type = event.get("type", "reminder")
                title = event.get("title", "Task")
                is_missed = event.get("missed", False)
                duration = event.get("duration_seconds")

                with self._lock:
                    self._stop_requested = False
                    self._is_ringing = True
                    self._current_event_id = event_id

                # 1. Play Audible Sound Alert
                try:
                    if event_type == "timer":
                        # Elegant ascending confirmation chime for completed timer
                        play_sound_async("done")
                    else:
                        # Klaxon / alert chime for reminder / alarm
                        play_sound_async("alarm")
                except Exception:
                    pass

                # Short delay for chime to complete before speaking
                time.sleep(0.9)

                if self._stop_requested:
                    with self._lock:
                        self._is_ringing = False
                        self._current_event_id = None
                    self._queue.task_done()
                    continue

                # 2. Formulate Natural Voice Announcement
                if event_type == "timer":
                    dur_text = ""
                    if duration:
                        mins, secs = divmod(duration, 60)
                        if mins and secs:
                            dur_text = f" of {mins} minutes and {secs} seconds"
                        elif mins:
                            dur_text = f" of {mins} minute{'s' if mins > 1 else ''}"
                        else:
                            dur_text = f" of {secs} seconds"
                    voice_msg = f"Sir, your {title} timer{dur_text} is complete."
                elif is_missed:
                    voice_msg = f"Sir, attention please: an overdue reminder for '{title}' was scheduled and is now due."
                else:
                    voice_msg = f"Sir, it's time to {title}."

                # 3. Speak Message Aloud
                try:
                    speak_text_sync(voice_msg)
                except Exception as e:
                    print(f"[JARVIS Audio Alert Error]: {e}")

                # 4. Mark completed in scheduler service
                try:
                    from tools.scheduler_service import JarvisScheduler
                    JarvisScheduler.mark_event_completed_or_recur(event_id)
                except Exception:
                    try:
                        from friday_tools.scheduler_service import JarvisScheduler
                        JarvisScheduler.mark_event_completed_or_recur(event_id)
                    except Exception:
                        pass

                with self._lock:
                    self._is_ringing = False
                    self._current_event_id = None

                self._queue.task_done()
                time.sleep(0.5)

            except Exception as e:
                time.sleep(1.0)


# Global singleton announcer
ANNOUNCER = AlarmAnnouncer()


def trigger_event_alert(event: Dict[str, Any]):
    """Public function to enqueue an event alert."""
    ANNOUNCER.enqueue_alert(event)


def stop_active_alarm():
    """Public function to stop ongoing audio."""
    ANNOUNCER.stop_alarm()
