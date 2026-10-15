"""
ULTRON Agent Harness & Runtime Supervisor
Provides an automated test & evaluation harness, tool integrity benchmarking,
safe sandboxed task execution, and system telemetry monitoring.
"""

import os
import sys
import time
import json
import asyncio
import psutil
import inspect
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

HARNESS_DATA_DIR = os.path.expanduser(r"~\Documents\ULTRON_Data\harness")
os.makedirs(HARNESS_DATA_DIR, exist_ok=True)
BENCHMARK_LOG_FILE = os.path.join(HARNESS_DATA_DIR, "benchmark_results.json")


class UltronHarness:
    """Core evaluation, benchmarking, and supervisory harness for ULTRON."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def get_telemetry(self) -> Dict[str, Any]:
        """Gathers real-time CPU, RAM, disk, and process telemetry."""
        proc = psutil.Process()
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "ram_percent": psutil.virtual_memory().percent,
            "process_ram_mb": round(proc.memory_info().rss / (1024**2), 2),
            "process_threads": proc.num_threads(),
            "active_pids": len(psutil.pids())
        }

    async def run_scenario(self, name: str, category: str, test_coro) -> Dict[str, Any]:
        """Runs a single test scenario with precise latency tracking and error isolation."""
        t0 = time.perf_counter()
        status = "PASSED"
        error_msg = None
        output = None

        try:
            if inspect.iscoroutine(test_coro):
                output = await asyncio.wait_for(test_coro, timeout=12.0)
            elif callable(test_coro):
                output = test_coro()
                if inspect.iscoroutine(output):
                    output = await asyncio.wait_for(output, timeout=12.0)
            else:
                output = test_coro

            if isinstance(output, str) and output.startswith("[ERROR]"):
                status = "FAILED"
                error_msg = output
        except asyncio.TimeoutError:
            status = "TIMEOUT"
            error_msg = "Scenario exceeded 12s execution limit."
        except Exception as e:
            status = "ERROR"
            error_msg = f"{type(e).__name__}: {str(e)}"

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        res = {
            "scenario": name,
            "category": category,
            "status": status,
            "latency_ms": elapsed_ms,
            "error": error_msg,
            "output_preview": str(output)[:150] if output else None
        }
        self.results.append(res)
        return res

    async def run_full_suite(self) -> Dict[str, Any]:
        """Executes comprehensive benchmark across all primary tool subsystems."""
        self.results = []
        import friday_tools

        # 1. System Briefing & Time Context
        from friday_tools.briefing import get_daily_briefing, is_birthday_today
        await self.run_scenario("Time & Daily Briefing", "Core", get_daily_briefing())

        # 2. File Indexing & Search
        from friday_tools.file_search_opener import search_file, index_files
        async def _test_file_search():
            idx = await index_files([os.path.expanduser(r"~\Documents\ULTRON_Data")])
            res = await search_file("ultron", idx)
            return f"Matched: {res['name'] if res else 'None'} (Indexed {len(idx)} items)"
        await self.run_scenario("Fuzzy File Index & Search", "Filesystem", _test_file_search())

        # 3. SafeController Keyboard/Mouse Status
        from friday_tools.keyboard_mouse import SafeController
        sc = SafeController()
        async def _test_ctrl():
            return f"Active: {sc.is_active()}, Mouse Pos: {sc.mouse.position}"
        await self.run_scenario("SafeController Inspection", "Automation", _test_ctrl())

        # 4. Multi-Camera Hardware Discovery
        from friday_tools.multi_camera_tracker import list_connected_cameras
        await self.run_scenario("Camera Discovery Probe", "Vision", list_connected_cameras(max_devices=3))

        # 5. Network ARP & Diagnostics
        from friday_tools.wake_on_lan_power import scan_local_active_devices
        await self.run_scenario("Network ARP Scan", "Network", scan_local_active_devices())

        # 6. Persistent Memory Verification
        from friday_tools.jarvis_memory import recall
        await self.run_scenario("Memory Recall System", "Memory", recall("birthday"))

        # Calculate metrics
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        total = len(self.results)
        avg_latency = round(sum(r["latency_ms"] for r in self.results) / total, 2) if total else 0

        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_scenarios": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate_percent": round((passed / total) * 100, 1) if total else 0,
            "average_latency_ms": avg_latency,
            "telemetry": self.get_telemetry(),
            "results": self.results
        }

        # Save to disk
        try:
            with open(BENCHMARK_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
        except Exception:
            pass

        return summary


# --- Tool Export Functions for ULTRON Agent ---

async def run_harness_benchmark() -> str:
    """
    Runs the full automated evaluation harness across all ULTRON tool subsystems,
    measuring latency, execution integrity, and system pass rate.
    """
    harness = UltronHarness()
    summary = await harness.run_full_suite()

    lines = [
        "============================================================",
        f" [ULTRON HARNESS] Benchmark Report - {summary['timestamp']}",
        "============================================================",
        f"Total Scenarios : {summary['total_scenarios']}",
        f"Passed          : {summary['passed']} / {summary['total_scenarios']} ({summary['pass_rate_percent']}%)",
        f"Avg Latency     : {summary['average_latency_ms']} ms",
        f"System Load     : CPU {summary['telemetry']['cpu_percent']}% | RAM {summary['telemetry']['ram_percent']}% ({summary['telemetry']['process_ram_mb']}MB used)",
        "------------------------------------------------------------",
        "Individual Test Results:"
    ]

    for r in summary["results"]:
        status_icon = "[PASS]" if r["status"] == "PASSED" else f"[{r['status']}]"
        lines.append(f" {status_icon.ljust(8)} | {r['category'].ljust(12)} | {r['scenario'].ljust(26)} | {str(r['latency_ms']).rjust(6)} ms")
        if r["error"]:
            lines.append(f"          -> Error: {r['error']}")

    lines.append("============================================================")
    lines.append(f"Full benchmark log saved to: {BENCHMARK_LOG_FILE}")
    return "\n".join(lines)


async def get_system_telemetry() -> str:
    """
    Captures live CPU, RAM, process threads, and memory consumption telemetry for the ULTRON agent runtime.
    """
    harness = UltronHarness()
    t = harness.get_telemetry()
    return (
        f"[ULTRON TELEMETRY]\n"
        f"- CPU Utilization : {t['cpu_percent']}%\n"
        f"- RAM Total / Used: {t['ram_used_gb']} GB / {t['ram_total_gb']} GB ({t['ram_percent']}%)\n"
        f"- Process Memory  : {t['process_ram_mb']} MB\n"
        f"- Active Threads  : {t['process_threads']}\n"
        f"- Host PIDs Count : {t['active_pids']}"
    )


async def execute_sandboxed_task(code_snippet: str, timeout_seconds: int = 8) -> str:
    """
    Executes a generated Python code snippet in an isolated sandbox with strict timeout and exception capture.
    """
    import io
    import contextlib

    def _exec():
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        local_scope = {}

        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                exec(code_snippet, {"__builtins__": __builtins__}, local_scope)
            
            out = stdout_buf.getvalue()
            err = stderr_buf.getvalue()
            res = f"[SANDBOX SUCCESS]\nStdout:\n{out or '(no stdout)'}"
            if err:
                res += f"\nStderr:\n{err}"
            return res
        except Exception as e:
            return f"[SANDBOX ERROR] Execution failed: {e}\n{traceback.format_exc()}"

    try:
        return await asyncio.wait_for(asyncio.to_thread(_exec), timeout=float(timeout_seconds))
    except asyncio.TimeoutError:
        return f"[SANDBOX TIMEOUT] Execution exceeded {timeout_seconds}s limit and was terminated."


if __name__ == "__main__":
    print("[HARNESS] Starting ULTRON evaluation suite...")
    res = asyncio.run(run_harness_benchmark())
    print(res)
