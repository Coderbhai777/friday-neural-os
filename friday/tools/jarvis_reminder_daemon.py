"""
JARVIS Standalone Background Scheduler Daemon
Created for Shivansh Sagar Pancholi

Operates continuously in the background on Windows, even when the main JARVIS
UI window is closed, minimized, or terminated.

Features:
- Single-instance enforcement via PID file & Windows process handle verification.
- 1-second precision tick loop for sub-second timer and reminder accuracy.
- Zero-overhead sleeping when no events are imminent.
- Survives GUI restarts and independent of the PyQt5/Electron interface.
- Graceful detachment via pythonw.exe with no intrusive command prompt window.
"""

import os
import sys
import time
import signal
import psutil
import subprocess
from pathlib import Path
from typing import Optional

# Ensure project directories are in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from tools.scheduler_service import JarvisScheduler, get_data_dir
    from tools.jarvis_alarm_announcer import trigger_event_alert
except ImportError:
    from friday_tools.scheduler_service import JarvisScheduler, get_data_dir
    from friday_tools.jarvis_alarm_announcer import trigger_event_alert


# Protect pythonw.exe where stdout and stderr are None
try:
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
except Exception:
    pass

PID_FILE = get_data_dir() / "jarvis_reminder_daemon.pid"
STOP_FLAG_FILE = get_data_dir() / "stop_daemon.flag"


def is_process_running(pid: int) -> bool:
    """Checks if a process with given PID is alive."""
    if not pid or pid <= 0:
        return False
    try:
        return psutil.pid_exists(pid)
    except Exception:
        return False


def get_running_daemon_pid() -> Optional[int]:
    """Returns the PID of the active daemon if running, else None."""
    if not PID_FILE.exists():
        return None
    try:
        content = PID_FILE.read_text(encoding="utf-8").strip()
        pid = int(content)
        if is_process_running(pid):
            return pid
        else:
            # Stale PID file
            PID_FILE.unlink(missing_ok=True)
            return None
    except Exception:
        return None


def write_pid_file():
    """Writes the current process PID to the lockfile."""
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")


def remove_pid_file():
    """Removes the daemon PID file."""
    try:
        if PID_FILE.exists():
            PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def run_daemon_loop():
    """Main continuous scheduling loop for the background daemon."""
    # Remove any stale stop flag
    STOP_FLAG_FILE.unlink(missing_ok=True)

    # Check single instance
    existing_pid = get_running_daemon_pid()
    if existing_pid and existing_pid != os.getpid():
        print(f"[JARVIS Daemon] Daemon already active on PID {existing_pid}. Exiting.")
        return

    log_file = get_data_dir() / "jarvis_daemon.log"

    def _log(msg):
        entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(entry)
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception:
            pass

    write_pid_file()
    running = True

    def _sig_handler(sig, frame):
        nonlocal running
        _log("Termination signal received.")
        running = False

    try:
        signal.signal(signal.SIGINT, _sig_handler)
        signal.signal(signal.SIGTERM, _sig_handler)
    except Exception:
        pass

    _log(f"[JARVIS Daemon] Started successfully (PID: {os.getpid()})")

    try:
        # Initial overdue recovery scan
        try:
            _log("Checking for pending/overdue events...")
            due_on_startup = JarvisScheduler.process_due_events(max_missed_threshold_minutes=60)
            for ev in due_on_startup:
                _log(f"Firing startup event: {ev['title']} ({ev['type']})")
                trigger_event_alert(ev)
        except Exception as e:
            _log(f"Startup scan error: {e}")

        while running:
            # Check stop flag
            if STOP_FLAG_FILE.exists():
                _log("Stop flag detected. Shutting down.")
                STOP_FLAG_FILE.unlink(missing_ok=True)
                break

            try:
                # Process due events
                due_events = JarvisScheduler.process_due_events()
                for ev in due_events:
                    _log(f"Event triggered: {ev['title']} (ID: {ev['id']})")
                    trigger_event_alert(ev)
            except Exception as e:
                _log(f"Error in scheduler tick: {e}")

            time.sleep(1.0)
    except Exception as exc:
        _log(f"Fatal daemon loop error: {exc}")
    finally:
        remove_pid_file()
        _log("Background Scheduler Daemon stopped.")


def start_daemon_detached() -> bool:
    """Spawns the background daemon detached without a console window."""
    existing_pid = get_running_daemon_pid()
    if existing_pid:
        return True  # Already running

    # Locate pythonw.exe or python.exe
    py_executable = sys.executable
    if "python.exe" in py_executable.lower():
        cand_pythonw = py_executable.lower().replace("python.exe", "pythonw.exe")
        if os.path.exists(cand_pythonw):
            py_executable = cand_pythonw

    script_path = str(Path(__file__).resolve())

    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

    try:
        boot_log = open(get_data_dir() / "daemon_boot.log", "a", encoding="utf-8")
        subprocess.Popen(
            [py_executable, script_path, "--run"],
            cwd=str(BASE_DIR),
            creationflags=creationflags,
            stdout=boot_log,
            stderr=boot_log,
            close_fds=True
        )
        # Poll up to 5 seconds for PID file to be written
        for _ in range(25):
            time.sleep(0.2)
            if get_running_daemon_pid() is not None:
                return True
        return get_running_daemon_pid() is not None
    except Exception as e:
        print(f"[JARVIS Daemon] Failed to spawn background daemon: {e}")
        return False


def stop_daemon() -> bool:
    """Gracefully terminates the background daemon."""
    pid = get_running_daemon_pid()
    if not pid:
        return True

    # Signal stop via flag file
    STOP_FLAG_FILE.touch()
    time.sleep(1.5)

    # Force kill if still lingering
    if is_process_running(pid):
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=2.0)
        except Exception:
            pass

    remove_pid_file()
    STOP_FLAG_FILE.unlink(missing_ok=True)
    return not is_process_running(pid)


if __name__ == "__main__":
    if "--run" in sys.argv or len(sys.argv) == 1:
        run_daemon_loop()
    elif "--stop" in sys.argv:
        if stop_daemon():
            print("[OK] JARVIS Daemon stopped.")
        else:
            print("[FAIL] Could not stop JARVIS Daemon.")
    elif "--status" in sys.argv:
        pid = get_running_daemon_pid()
        if pid:
            print(f"[OK] JARVIS Daemon running (PID: {pid}).")
        else:
            print("[INFO] JARVIS Daemon is not running.")
    elif "--start" in sys.argv:
        if start_daemon_detached():
            print(f"[OK] JARVIS Daemon spawned in background (PID: {get_running_daemon_pid()}).")
        else:
            print("[FAIL] Failed to start JARVIS Daemon.")
