"""
ULTRON System Optimizer & Storage Maintenance Engine
Safe purge of Windows caches, disk space hog analyzer, battery degradation auditor, and DNS resolver flusher.
"""

import os
import sys
import time
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import psutil
except ImportError:
    psutil = None


async def clean_windows_temp_caches() -> str:
    """
    Safely purges Windows User Temp, System Temp, crash dumps, and obsolete cache files to reclaim disk space.
    """
    def _clean():
        temp_paths = [
            Path(os.environ.get("TEMP", r"C:\Users\Default\AppData\Local\Temp")),
            Path(r"C:\Windows\Temp"),
            Path(r"C:\Windows\Prefetch"),
            Path.home() / "AppData" / "Local" / "CrashDumps"
        ]

        deleted_files = 0
        freed_bytes = 0
        errors = 0

        for t_dir in temp_paths:
            if t_dir.exists():
                for item in t_dir.glob("*"):
                    try:
                        if item.is_file() or item.is_symlink():
                            sz = item.stat().st_size
                            item.unlink(missing_ok=True)
                            freed_bytes += sz
                            deleted_files += 1
                        elif item.is_dir():
                            sz = sum(f.stat().st_size for f in item.glob("**/*") if f.is_file())
                            shutil.rmtree(item, ignore_errors=True)
                            freed_bytes += sz
                            deleted_files += 1
                    except Exception:
                        errors += 1

        freed_mb = freed_bytes / (1024 * 1024)
        return (
            f"🧹 **WINDOWS TEMP & CACHE PURGE COMPLETE:**\n"
            f"• **Files / Folders Removed:** {deleted_files:,}\n"
            f"• **Disk Space Reclaimed:** **{freed_mb:.2f} MB** ({freed_mb / 1024:.2f} GB)\n"
            f"• **Locked / In-Use Files Skipped:** {errors}\n"
            f"• **Status:** System cache directories flushed."
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _clean)


async def inspect_disk_space_hogs(root_path: str = "C:\\Users\\shiva", top_n: int = 8) -> str:
    """
    Scans a folder or user profile and ranks the largest subdirectories eating storage space.
    
    Args:
        root_path: Root directory to inspect (e.g. 'C:/Users/shiva', 'C:/Program Files').
        top_n: Number of largest folders to report.
    """
    def _scan():
        target = Path(root_path).expanduser().resolve()
        if not target.exists():
            return f"Path `{target}` does not exist."

        dir_sizes = []
        for item in target.iterdir():
            if item.is_dir() and not item.name.startswith(("$", "System Volume Information")):
                try:
                    total_sz = 0
                    for root, _, files in os.walk(item):
                        for f in files:
                            try:
                                total_sz += os.path.getsize(os.path.join(root, f))
                            except Exception:
                                pass
                    dir_sizes.append((item.name, total_sz, item))
                except Exception:
                    pass

        dir_sizes.sort(key=lambda x: x[1], reverse=True)
        top = dir_sizes[:top_n]

        lines = [f"📊 **STORAGE SPACE BREAKDOWN FOR `{target}`:**"]
        for idx, (name, sz_bytes, p) in enumerate(top, 1):
            gb = sz_bytes / (1024**3)
            mb = sz_bytes / (1024**2)
            sz_str = f"**{gb:.2f} GB**" if gb >= 1.0 else f"**{mb:.1f} MB**"
            lines.append(f"  {idx}. 📁 `{name}` ➔ {sz_str} (`{p}`)")

        return "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scan)


async def battery_health_report() -> str:
    """
    Generates and parses official Windows battery telemetry, including design capacity, full charge capacity, and health wear percentage.
    """
    def _get_battery():
        if not psutil:
            return "[BATTERY] psutil unavailable."
        
        batt = psutil.sensors_battery()
        if not batt:
            return "🖥️ [POWER TELEMETRY] Desktop Workstation detected (AC mains power, no battery)."

        status_str = "Plugged In & Charging" if batt.power_plugged else "On Battery Power (Discharging)"
        time_left = f"{batt.secsleft // 60} mins" if batt.secsleft > 0 and batt.secsleft != psutil.POWER_TIME_UNLIMITED else "Calculating..."

        # Generate deep battery report via powercfg
        wear_info = ""
        try:
            report_path = Path.home() / "battery_report.xml"
            subprocess.run(["powercfg", "/batteryreport", "/xml", f"/output", str(report_path)], capture_output=True, timeout=5)
            if report_path.exists():
                import xml.etree.ElementTree as ET
                tree = ET.parse(report_path)
                root = tree.getroot()
                design_cap = root.find(".//DesignCapacity")
                full_cap = root.find(".//FullChargeCapacity")
                cycle_count = root.find(".//CycleCount")
                
                if design_cap is not None and full_cap is not None:
                    d_val = float(design_cap.text or 0)
                    f_val = float(full_cap.text or 0)
                    if d_val > 0:
                        health_pct = (f_val / d_val) * 100
                        cycles = cycle_count.text if cycle_count is not None else "N/A"
                        wear_info = f"\n• **Battery Health (Capacity Retention):** **{health_pct:.1f}%** ({f_val:,.0f} mWh of {d_val:,.0f} mWh design)\n• **Charge Cycle Count:** {cycles}"
                report_path.unlink(missing_ok=True)
        except Exception:
            pass

        return (
            f"🔋 **ULTRON BATTERY & POWER HEALTH REPORT:**\n"
            f"• **Current Charge Level:** **{batt.percent}%**\n"
            f"• **Power State:** {status_str}\n"
            f"• **Estimated Runtime Remaining:** {time_left}"
            f"{wear_info}"
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_battery)


async def system_flush_dns_cache() -> str:
    """
    Flushes the Windows DNS Resolver Cache to resolve network connection timeouts or stale domain IP mappings.
    """
    def _flush():
        try:
            res = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=5)
            return f"🌐 [DNS RESOLVER FLUSHED]:\n{res.stdout.strip()}"
        except Exception as e:
            return f"[ERROR] Failed to flush DNS: {e}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _flush)
