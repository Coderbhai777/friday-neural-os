"""
ULTRON JARVIS Tiered Security Policy & Clearance Matrix
Enforces SAFE / SENSITIVE / DANGEROUS / BLOCKED operational classification.
Protects dangerous operations behind explicit confirmation gates while permitting high-speed safe automation.
"""

import os
import json
from typing import Dict, Any, Tuple, Optional

# ==========================================
# POLICY CLASSIFICATION MATRIX
# ==========================================

SAFE_TOOLS = {
    "get_cpu_usage", "get_ram_usage", "get_gpu_usage", "get_disk_usage", "get_network_status",
    "get_battery_status", "get_temperature", "get_system_info", "get_world_state", "get_hud_state",
    "web_search", "open_webpage", "extract_webpage", "summarize_page", "search_documentation",
    "read_file", "search_code", "read_screen", "describe_scene", "ocr_screen", "find_object",
    "open_youtube", "play_music", "get_room_temperature", "list_capabilities", "find_capability",
    "get_user_context", "get_environment_state", "get_device_state", "get_active_tasks", "get_current_goal",
    "list_todos", "read_calendar", "list_upcoming_events", "scan_serial_ports", "scan_lab"
}

SENSITIVE_TOOLS = {
    "delete_file", "delete_upcoming_event", "clear_all_events", "upload_firmware", "esp32_flash_firmware",
    "lock_pc", "sleep_pc", "restart_pc", "turn_light_on", "turn_light_off", "set_light_brightness",
    "control_ac", "control_fan", "move_servo", "grab_object", "control_motor", "send_whatsapp_message",
    "send_telegram_message", "email_send_reply", "email_smart_compose", "git_commit", "create_pull_request"
}

DANGEROUS_TOOLS = {
    "shutdown_system", "clean_system", "empty_recycle_bin", "port_scan", "vulnerability_scanner",
    "sniff_network_packets", "disconnect_device_from_internet", "limit_device_bandwidth", "network_kill_switch",
    "extract_browser_passwords", "execute_cmd", "execute_powershell"
}

BLOCKED_TOOLS = {
    "wifi_deauth_attack", "dns_spoofing_attack", "local_network_brute_force", "smb_eternalblue_scan"
}


def evaluate_action_safety(tool_name: str, params: dict = None) -> Tuple[str, str]:
    """
    Evaluates safety tier of a requested tool execution:
    - SAFE: Immediate automatic execution
    - SENSITIVE: Requires single-click or voice confirmation
    - DANGEROUS: Requires root confirmation
    - BLOCKED: Prohibited in autonomous mode
    """
    t = tool_name.lower().strip()
    
    if t in BLOCKED_TOOLS:
        return "BLOCKED", f"🚫 [POLICY BLOCKED]: Capability '{tool_name}' is restricted to controlled lab authorization."
        
    if t in DANGEROUS_TOOLS:
        return "DANGEROUS", f"⚠️ [DANGEROUS OPERATION]: '{tool_name}' requires explicit creator root confirmation."
        
    if t in SENSITIVE_TOOLS:
        return "SENSITIVE", f"🔔 [SENSITIVE ACTION]: '{tool_name}' requires operational confirmation."
        
    return "SAFE", f"✅ [SAFE]: '{tool_name}' cleared for immediate autonomous execution."


async def enforce_policy(tool_name: str, params: dict = None) -> str:
    """Enforces safety policy before executing a tool."""
    tier, msg = evaluate_action_safety(tool_name, params)
    return f"🛡️ [SECURITY POLICY EVALUATION]:\nTier: {tier}\nStatus: {msg}"


async def list_policy_tiers() -> str:
    """Lists summary of the security clearance tiers."""
    return (
        "🛡️ [ULTRON TIERED CAPABILITY CLEARANCE MATRIX]:\n"
        f"• SAFE (Auto-Execute): {len(SAFE_TOOLS)} capabilities (Telemetry, Vision, Search, Read)\n"
        f"• SENSITIVE (Confirmation Required): {len(SENSITIVE_TOOLS)} capabilities (Actuators, Flashing, Sending)\n"
        f"• DANGEROUS (Multi-Factor Root): {len(DANGEROUS_TOOLS)} capabilities (Power, System Sweeps)\n"
        f"• BLOCKED (Lab Only): {len(BLOCKED_TOOLS)} capabilities (Offensive Network Injections)"
    )
