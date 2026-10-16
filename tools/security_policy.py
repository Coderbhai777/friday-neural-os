# -*- coding: utf-8 -*-
"""
ULTRON JARVIS Tiered Security Policy & Clearance Matrix (Section 7 Compliant)
Enforces LOW / MEDIUM / HIGH / BLOCKED risk classification.
Requires explicit authorization for high-risk operations.
Provides global emergency stop to immediately cancel all active loops.
"""

import os
import threading
from typing import Dict, Any, Tuple, Optional, Set

# Risk Constants
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_BLOCKED = "BLOCKED"

# ==========================================
# 1. RISK CATEGORIES MATRIX
# ==========================================

LOW_RISK_ACTIONS: Set[str] = {
    # Opening apps, navigating websites, searching, scrolling, reading
    "open_application", "open_website", "navigate_url", "search_web", "read_page",
    "take_screenshot", "scroll_screen", "read_file", "list_files", "inspect_structure",
    "get_status", "get_metrics", "find_element", "verify_state", "create_test_file",
    "run_permitted_test", "describe_scene", "ocr_screen", "find_object"
}

MEDIUM_RISK_ACTIONS: Set[str] = {
    # Installing dependencies, modifying existing projects, changing preferences, moving/overwriting files
    "install_dependency", "modify_project_file", "change_preference",
    "move_file", "overwrite_file", "execute_script", "compile_code",
    "restart_application", "set_light_brightness", "git_commit"
}

HIGH_RISK_ACTIONS: Set[str] = {
    # Deleting important files, emptying recycle bin, sending messages/emails, purchases, security changes
    "delete_file", "empty_recycle_bin", "send_email", "send_whatsapp_message",
    "send_telegram_message", "make_purchase", "publish_content", "change_security_setting",
    "modify_startup_behavior", "execute_admin_command", "disable_protection",
    "shutdown_system", "restart_system", "clean_system", "extract_passwords",
    "format_disk", "kill_process_force"
}

BLOCKED_ACTIONS: Set[str] = {
    "wifi_deauth_attack", "dns_spoofing_attack", "local_network_brute_force", "smb_eternalblue_scan",
    "bypass_uac", "bypass_captcha", "steal_credentials"
}


# ==========================================
# 2. EMERGENCY STOP CONTROLLER
# ==========================================

class EmergencyStopController:
    """Thread-safe global emergency stop mechanism."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._stopped = False
        self._reason = ""

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = EmergencyStopController()
            return cls._instance

    def trigger(self, reason: str = "User initiated emergency stop") -> str:
        with self._lock:
            self._stopped = True
            self._reason = reason
        print(f"\n[EMERGENCY STOP TRIGGERED]: {reason}\nAll autonomous actions immediately halted.")
        return f"[EMERGENCY STOP ACTIVATED]: {reason}"

    def reset(self) -> str:
        with self._lock:
            self._stopped = False
            self._reason = ""
        return "[EMERGENCY STOP CLEARED]: System returned to normal operating mode."

    def is_stopped(self) -> bool:
        with self._lock:
            return self._stopped

    def get_reason(self) -> str:
        with self._lock:
            return self._reason


class EmergencyStopException(Exception):
    """Raised when an action is attempted while emergency stop is active."""
    pass


class AuthorizationRequiredException(Exception):
    """Raised when a HIGH RISK action is attempted without explicit authorization."""
    pass


_EMERGENCY_STOP = EmergencyStopController.get_instance()


def trigger_emergency_stop(reason: str = "User initiated emergency stop") -> str:
    return _EMERGENCY_STOP.trigger(reason)


def reset_emergency_stop() -> str:
    return _EMERGENCY_STOP.reset()


def is_emergency_stopped() -> bool:
    return _EMERGENCY_STOP.is_stopped()


# ==========================================
# 3. SAFETY EVALUATION
# ==========================================

def evaluate_action_risk(action_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
    """
    Evaluates an action's risk tier according to Section 7:
    - LOW: Open apps, navigate web, search, read, sandbox test
    - MEDIUM: Dependency installation, modifying files, changing preferences
    - HIGH: Deleting important files, emptying recycle bin, sending messages, admin commands
    - BLOCKED: Network exploits, credential theft, security bypassing
    """
    if is_emergency_stopped():
        return RISK_BLOCKED, f"🛑 Emergency Stop is active: {_EMERGENCY_STOP.get_reason()}"

    act = action_name.lower().strip()

    # Check blocked
    if act in BLOCKED_ACTIONS or any(b in act for b in ["deauth", "eternalblue", "brute_force", "bypass_uac"]):
        return RISK_BLOCKED, f"🚫 [POLICY BLOCKED]: '{action_name}' violates autonomous safety boundaries."

    # Check high risk
    if act in HIGH_RISK_ACTIONS or any(h in act for h in ["delete", "empty_recycle", "send_email", "send_message", "purchase", "admin", "format", "shutdown"]):
        # Special case: deleting inside designated sandbox folder is medium risk
        if act == "delete_file" and params and "sandbox" in str(params.get("path", "")).lower():
            return RISK_MEDIUM, f"⚠️ [MEDIUM RISK]: Sandbox file deletion permitted within isolated test space."
        return RISK_HIGH, f"⚠️ [HIGH RISK]: '{action_name}' requires explicit creator root authorization."

    # Check medium risk
    if act in MEDIUM_RISK_ACTIONS or any(m in act for m in ["install", "overwrite", "modify", "compile", "script"]):
        return RISK_MEDIUM, f"🔔 [MEDIUM RISK]: '{action_name}' modifies workspace state or dependencies."

    # Default to low risk
    return RISK_LOW, f"✅ [LOW RISK]: '{action_name}' cleared for immediate execution."


def check_action_permitted(action_name: str, params: Optional[Dict[str, Any]] = None, is_authorized: bool = False) -> Tuple[bool, str]:
    """
    Checks if an action is permitted to execute given the current authorization state.
    Returns (permitted: bool, reason: str).
    """
    if is_emergency_stopped():
        return False, f"Emergency Stop is ACTIVE: {_EMERGENCY_STOP.get_reason()}"

    risk_tier, msg = evaluate_action_risk(action_name, params)

    if risk_tier == RISK_BLOCKED:
        return False, msg

    if risk_tier == RISK_HIGH:
        if not is_authorized:
            return False, f"AUTHORIZATION REQUIRED: {msg} Confirm target and intended consequence."
        return True, f"AUTHORIZED HIGH RISK: {msg}"

    if risk_tier == RISK_MEDIUM:
        return True, f"PERMITTED MEDIUM RISK: {msg}"

    return True, f"PERMITTED LOW RISK: {msg}"


# Backward compatibility aliases
def evaluate_action_safety(tool_name: str, params: dict = None) -> Tuple[str, str]:
    tier, msg = evaluate_action_risk(tool_name, params)
    return tier, msg


async def enforce_policy(tool_name: str, params: dict = None) -> str:
    tier, msg = evaluate_action_risk(tool_name, params)
    return f"🛡️ [SECURITY POLICY EVALUATION]:\nTier: {tier}\nStatus: {msg}"


async def list_policy_tiers() -> str:
    return (
        "🛡️ [ULTRON SECTION 7 POLICY CLEARANCE MATRIX]:\n"
        f"• LOW RISK (Auto-Execute): Apps, Web Navigation, Search, Read, Sandboxed Files\n"
        f"• MEDIUM RISK (Workspace Action): Dependencies, Project Code, Overwrite\n"
        f"• HIGH RISK (Explicit Auth Required): Deletion, Outbox Messaging, Admin Execution, Power\n"
        f"• BLOCKED (Strictly Prohibited): Exploits, Credential Theft, UAC Bypass\n"
        f"• Emergency Stop: {'ACTIVE 🛑' if is_emergency_stopped() else 'READY ✅'}"
    )
