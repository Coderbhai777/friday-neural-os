"""
ULTRON JARVIS Tool Selector & Intelligent Intent Routing Engine
Provides 0ms instant pattern matching for common voice/text commands (e.g. "open YouTube", "play song", "lock pc")
and AI-powered semantic tool selection across all 415+ ULTRON capabilities.
"""

import os
import re
import sys
import json
import time
import asyncio
import webbrowser
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Callable


# ==========================================
# 1. SPECIALIZED DIRECT ACTION DISPATCHERS
# ==========================================

async def open_youtube(query: str = "") -> str:
    """
    Directly opens YouTube. If a query or song is provided, searches or plays it immediately.
    """
    try:
        clean_q = query.strip()
        # Remove common trigger prefixes
        for prefix in ["open youtube", "youtube", "search youtube for", "play on youtube", "open"]:
            if clean_q.lower().startswith(prefix):
                clean_q = clean_q[len(prefix):].strip()

        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not clean_q:
            url = "https://www.youtube.com"
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, url])
            else:
                webbrowser.open(url)
            return "🎬 [ULTRON] Opened YouTube."
        else:
            from friday_tools.media import play_music
            return await play_music(clean_q)
    except Exception as e:
        return f"[ERROR] Failed to open YouTube: {e}"


async def open_application(app_name: str) -> str:
    """
    Launches any installed desktop app, system tool, or website by name.
    """
    from friday_tools.ui import open_website_or_app
    return await open_website_or_app(app_name)


# ==========================================
# 2. FAST DETERMINISTIC INTENT ROUTER (0ms Latency)
# ==========================================

FAST_ROUTING_TABLE = [
    # Subagents & Autonomous Background Execution (Priority 1)
    (r"^(?:spawn|create|launch|start|run)\s+(?:a\s+|an\s+)?(?:background\s+)?(?:research|search|web|email|coding|homework)?\s*subagents?\s+(?:to\s+|for\s+)?(.+)$", "spawn_subagent", lambda m: {"task": m.group(1).strip()}),
    (r"^(?:subagent|sub-agent|sub agent)\s+(?:spawn\s+karo|karo\s+spawn|spawn|karo|start|run|banao)\s+(?:to\s+|for\s+|jo\s+)?(.+)$", "spawn_subagent", lambda m: {"task": m.group(1).strip()}),
    (r"^(?:ek\s+)?subagent\s+(?:banao|chalao|spawn\s+karo)\s+(?:jo\s+|to\s+|for\s+)?(.+)$", "spawn_subagent", lambda m: {"task": m.group(1).strip()}),
    (r"^(?:spawn|run|start)\s+(?:a\s+)?subagent\s*:\s*(.+)$", "spawn_subagent", lambda m: {"task": m.group(1).strip()}),
    (r"^(?:how much (?:is it |is the subagent )?done|how much is completed|what is the progress|subagent progress|check subagent progress|kitna hua|kitna percent hua|progress batao)(?:\s+of\s+([a-zA-Z0-9]{4,12}))?$", "check_subagent_progress", lambda m: {"agent_id": m.group(1) or "" if m.lastindex else ""}),
    (r"^(?:check|view|show|get)\s+progress(?:\s+of\s+([a-zA-Z0-9]{4,12}))?$", "check_subagent_progress", lambda m: {"agent_id": m.group(1) or "" if m.lastindex else ""}),
    (r"^(?:list|show|view|check|display|get)\s+(?:all\s+)?(?:running\s+)?subagents?$", "list_subagents", lambda m: {}),
    (r"^(?:subagents?|sub-agents?|sub agents?)(?:\s+status|\s+list|\s+batao|\s+dikhao|\s+check)?$", "list_subagents", lambda m: {}),
    (r"^(?:check|get|fetch|read)\s+(?:subagent\s+result|result of subagent)\s+([a-zA-Z0-9]{4,12})$", "get_subagent_result", lambda m: {"agent_id": m.group(1).strip()}),
    (r"^(?:kill|cancel|stop|terminate)\s+subagent\s+([a-zA-Z0-9]{4,12})$", "kill_subagent", lambda m: {"agent_id": m.group(1).strip()}),
    (r"^(?:wait for|await)\s+subagents?$", "wait_for_subagents", lambda m: {}),

    # Minecraft SMP Integration (Priority 1 Catch-All)
    (r"^(?:open|play|start|launch|join|connect to|enter|log into|run)\s+(?:the\s+|my\s+)?(?:minecraft|smp|server|bedrock|mc)(?:\s+server|\s+world)?$", "start_minecraft_player_bot", lambda m: {}),
    (r"^(?:minecraft|smp|bedrock|mc)$", "start_minecraft_player_bot", lambda m: {}),
    (r"^.*(?:play|join|enter|start|open)\s+(?:minecraft|smp).*$", "start_minecraft_player_bot", lambda m: {}),
    (r"^(?:leave|disconnect from|quit|stop)\s+(?:the\s+|my\s+)?(?:minecraft|smp|server|minecraft bot)$", "stop_minecraft_player_bot", lambda m: {}),
    (r"^(?:check|query|ping)\s+(?:the\s+|my\s+)?(?:minecraft|smp)(?:\s+server)?(?:\s+status)?$", "minecraft_server_status", lambda m: {}),

    # YouTube & Media
    (r"^(?:open|launch|start|play)\s+youtube(?:\s+(?:and\s+)?(?:search|play)?\s*(.*))?$", "open_youtube", lambda m: {"query": m.group(1) or ""}),
    (r"^youtube\s*(.*)$", "open_youtube", lambda m: {"query": m.group(1) or ""}),
    (r"^(?:play|listen to)\s+(?:song\s+|music\s+)?(.+)$", "play_music", lambda m: {"song": m.group(1).strip()}),
    (r"^(?:pause|resume|next|previous)\s+media$", "media_control", lambda m: {"action": "toggle"}),
    
    # PC Diagnostics & Hardware Telemetry
    (r"^(?:why is my (?:pc|computer|laptop) slow|diagnose (?:pc|system|computer)|pc lag(?:ging)?)$", "diagnose_slow_pc", lambda m: {}),
    (r"^.*(?:what(?:'s| is)? (?:consuming|using|taking) (?:my )?ram|who is using (?:my )?ram|why is (?:my )?ram (?:so )?high|ram hogs?|memory hogs?|top ram|top processes|check (?:my )?ram).*$", "get_ram_usage", lambda m: {}),
    (r"^(?:check\s+)?(?:cpu|processor)(?:\s+usage|\s+load)?$", "get_cpu_usage", lambda m: {}),
    (r"^(?:check\s+)?(?:ram|memory)(?:\s+usage|\s+status)?$", "get_ram_usage", lambda m: {}),
    (r"^.*(?:clean|clear|free|flush|optimize)\s+(?:up\s+)?(?:my\s+)?(?:ram|memory).*$", "hardware_ram_cleaner", lambda m: {}),
    (r"^(?:check\s+)?(?:gpu|graphics)(?:\s+usage|\s+temp)?$", "get_gpu_usage", lambda m: {}),
    (r"^(?:check\s+)?(?:disk|storage|hard drive)(?:\s+space|\s+usage)?$", "get_disk_usage", lambda m: {}),
    (r"^(?:check\s+)?(?:battery|power)(?:\s+status|\s+percentage)?$", "get_battery_status", lambda m: {}),
    (r"^(?:check\s+)?(?:temperature|thermal|temp)$", "get_temperature", lambda m: {}),
    (r"^(?:system info|specs|workstation info)$", "get_system_info", lambda m: {}),
    (r"^(?:active window|current window|focused app)$", "get_active_window", lambda m: {}),
    
    # Workstation & Window Layout Management
    (r"^.*(?:snap (?:windows?|layout)|split screen|side by side).*$", "window_snap_layout", lambda m: {"layout": "side_by_side"}),
    (r"^.*(?:focus mode|focus window|maximize (?:active|primary)).*$", "window_snap_layout", lambda m: {"layout": "focus"}),
    (r"^.*(?:grid layout|quadrant windows?|tile windows?).*$", "window_snap_layout", lambda m: {"layout": "grid"}),
    (r"^(?:list|show|view)\s+(?:open\s+)?windows?$", "list_open_windows", lambda m: {}),
    (r"^(?:show desktop|minimize all(?: windows)?)$", "window_minimize_all", lambda m: {}),
    (r"^(?:bring up|focus|switch to)\s+(.+)$", "window_focus_app", lambda m: {"app_name": m.group(1).strip()}),

    # Network & IoT Discovery
    (r"^.*(?:scan (?:the )?(?:local )?network|scan (?:the )?lan|find connected devices|list network devices).*$", "lan_scan_active_devices", lambda m: {}),
    (r"^.*(?:my local ip|network ip|gateway ip|network config).*$", "lan_get_local_ip_and_gateway", lambda m: {}),
    (r"^.*(?:flush (?:the )?dns|clear dns|reset dns).*$", "system_flush_dns_cache", lambda m: {}),

    # Storage & System Optimizer
    (r"^.*(?:clean (?:temp|cache|temporary files?)|purge temp|free disk space).*$", "clean_windows_temp_caches", lambda m: {}),
    (r"^.*(?:battery (?:health|report|wear|capacity)|power health).*$", "battery_health_report", lambda m: {}),
    (r"^.*(?:disk (?:hogs|space breakdown|large folders)|where is my storage).*$", "inspect_disk_space_hogs", lambda m: {}),

    # PC Control
    (r"^lock(?:\s+my)?\s+(?:pc|computer|screen|workstation)$", "lock_pc", lambda m: {}),
    (r"^sleep(?:\s+my)?\s+(?:pc|computer)$", "sleep_pc", lambda m: {}),
    (r"^(?:set\s+)?brightness\s+(?:to\s+)?(\d{1,3})%?$", "control_brightness", lambda m: {"level": int(m.group(1))}),
    (r"^(?:switch|focus)\s+(?:window|app)\s+(?:to\s+)?(.+)$", "switch_window", lambda m: {"title": m.group(1).strip()}),
    (r"^minimize(?:\s+window)?$", "minimize_window", lambda m: {}),
    (r"^maximize(?:\s+window)?$", "maximize_window", lambda m: {}),
    
    # Vision & Screen Perception
    (r"^(?:take\s+a?\s*)?screenshot$", "take_screenshot", lambda m: {}),
    (r"^(?:what is on my screen|read screen|analyze screen|scan screen)$", "read_screen", lambda m: {}),
    (r"^(?:ocr screen|extract text from screen)$", "ocr_screen", lambda m: {}),
    (r"^(?:what is on my desk|describe scene|look around|camera scan)$", "describe_scene", lambda m: {}),
    (r"^(?:where is|find)\s+(?:my\s+)?(.+?)(?:\s+on desk|\s+in room)?$", "find_object", lambda m: {"object_name": m.group(1).strip()}),
    
    # Smart Home & IoT
    (r"^turn on (?:the )?lights?$", "turn_light_on", lambda m: {"device": "all"}),
    (r"^turn off (?:the )?lights?$", "turn_light_off", lambda m: {"device": "all"}),
    (r"^turn on (?:the )?(.+?)(?: light)?$", "turn_light_on", lambda m: {"device": m.group(1).strip()}),
    (r"^turn off (?:the )?(.+?)(?: light)?$", "turn_light_off", lambda m: {"device": m.group(1).strip()}),
    (r"^(?:activate\s+)?evening mode$", "activate_preset_scene", lambda m: {"scene_name": "evening mode"}),
    (r"^(?:activate\s+)?(?:focus|coding|work) mode$", "activate_preset_scene", lambda m: {"scene_name": "focus mode"}),
    (r"^(?:activate\s+)?(?:lab|hardware) mode$", "activate_preset_scene", lambda m: {"scene_name": "lab mode"}),
    (r"^(?:activate\s+)?(?:night|sleep) mode$", "activate_preset_scene", lambda m: {"scene_name": "night mode"}),
    (r"^(?:room temp|temperature in room|room climate)$", "get_room_temperature", lambda m: {}),
    
    # Robotics
    (r"^(?:move|set) servo\s+(\d{1,2})\s+(?:to\s+)?(\d{1,3})(?: deg| degrees|°)?$", "move_servo", lambda m: {"pin": int(m.group(1)), "angle": int(m.group(2))}),
    (r"^(?:grab object|close gripper|grip)$", "grab_object", lambda m: {"gripper_angle": 90}),
    (r"^(?:release object|open gripper)$", "grab_object", lambda m: {"gripper_angle": 0}),
    
    # Schedule & Calendar Events
    (r"^(?:delete|remove|cancel)\s+event\s+(.+)$", "delete_upcoming_event", lambda m: {"event_name": m.group(1).strip()}),
    (r"^(?:list|show|view)\s+(?:events|calendar|competitions)$", "list_upcoming_events", lambda m: {}),
    (r"^(?:set timer for|timer)\s+(\d+(?:\.\d+)?)\s*(?:min|mins|minutes)$", "set_timer", lambda m: {"minutes": float(m.group(1)), "label": "Timer"}),
    
    # Minecraft SMP Integration (Universal Catch-All)
    (r"^(?:open|play|start|launch|join|connect to|enter|log into|run)\s+(?:the\s+|my\s+)?(?:minecraft|smp|server|bedrock|mc)(?:\s+server|\s+world)?$", "start_minecraft_player_bot", lambda m: {}),
    (r"^(?:minecraft|smp|bedrock|mc)$", "start_minecraft_player_bot", lambda m: {}),
    (r"^.*(?:play|join|enter|start|open)\s+(?:minecraft|smp).*$", "start_minecraft_player_bot", lambda m: {}),
    (r"^(?:leave|disconnect from|quit|stop)\s+(?:the\s+|my\s+)?(?:minecraft|smp|server|minecraft bot)$", "stop_minecraft_player_bot", lambda m: {}),
    (r"^(?:check|query|ping)\s+(?:the\s+|my\s+)?(?:minecraft|smp)(?:\s+server)?(?:\s+status)?$", "minecraft_server_status", lambda m: {}),
    
    # General App Launching
    (r"^(?:open|launch|start)\s+(.+)$", "open_application", lambda m: {"app_name": m.group(1).strip()}),
]


def match_fast_intent(user_input: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Performs instant regex and fuzzy intent matching on user input.
    Returns (tool_name, kwargs) if matched, else None.
    """
    clean = user_input.strip().lower()
    # Strip leading polite words like 'ultron', 'please', 'hey', 'jarvis'
    for prefix in ["ultron", "jarvis", "please", "can you", "could you", "hey ultron", "hey jarvis"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):].strip(" ,:.-")

    for pattern, tool_name, arg_extractor in FAST_ROUTING_TABLE:
        m = re.match(pattern, clean, re.IGNORECASE)
        if m:
            try:
                kwargs = arg_extractor(m)
                return tool_name, kwargs
            except Exception:
                continue
                
    return None


# ==========================================
# 3. UNIFIED TOOL SELECTOR & EXECUTOR
# ==========================================

async def select_and_execute_tool(user_input: str) -> Optional[str]:
    """
    Primary JARVIS Intent Selector:
    1. Checks fast deterministic routing table (0ms).
    2. If matched, executes corresponding tool directly from TOOL_MAP.
    3. If not matched, returns None so AI inference engine handles general conversation/multi-tool reasoning.
    """
    import aria_modules.tools as tools
    fast_match = match_fast_intent(user_input)
    
    if fast_match:
        tool_name, kwargs = fast_match
        
        # Dedicated custom aliases
        if tool_name == "open_youtube":
            return await open_youtube(kwargs.get("query", ""))
        elif tool_name == "open_application":
            return await open_application(kwargs.get("app_name", ""))
            
        # Check in aria tools TOOL_MAP
        if hasattr(tools, "TOOL_MAP") and tool_name in tools.TOOL_MAP:
            fn = tools.TOOL_MAP[tool_name]
            try:
                if asyncio.iscoroutinefunction(fn):
                    res = await fn(**kwargs)
                else:
                    res = fn(**kwargs)
                    if asyncio.iscoroutine(res):
                        res = await res
                return str(res)
            except Exception as e:
                # Try calling without args if args mismatched
                try:
                    res = await fn() if asyncio.iscoroutinefunction(fn) else fn()
                    return str(res)
                except Exception as err:
                    return f"[ERROR] Failed executing tool '{tool_name}': {err}"

    return None


async def tool_selector(command: str) -> str:
    """
    Autonomous tool selector capability. Analyzes user command, selects the appropriate tool, and executes it.
    """
    res = await select_and_execute_tool(command)
    if res:
        return res
        
    # AI Fallback for complex queries
    import friday_tools.ai_client as ai
    prompt = f"The user issued this command: '{command}'. Formulate the exact execution or execute the relevant tools."
    return ai.generate_ai_response(prompt=prompt)
