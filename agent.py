from dotenv import load_dotenv
load_dotenv()

import os
import sys
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
try:
    from mem0 import MemoryClient
    mem0 = MemoryClient(api_key=os.getenv("MEM0_API_KEY")) if os.getenv("MEM0_API_KEY") else None
except Exception:
    mem0 = None

USER_ID = "SHIVANSH"

@dataclass
class RunContext:
    room: Any = None
    session: Any = None
    extra: Dict[str, Any] = field(default_factory=dict)

from .prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from .tools import *
from .brain import AntiGravityEngine

# ==============================
# TOOLS
# ==============================
ALL_TOOLS = [
    get_weather, search_web, send_email, current_time,
    system_status, system_uptime, battery_status, check_internet, system_health_report,
    publish_to_sandbox,
    control_bluetooth, control_windows_settings,
    play_music, youtube_search_results, select_video_by_index,
    track_active_application, weekly_app_usage_report,
    remember, recall, forget, update_memory, view_brain, delete_log, clear_old_logs,
    save_contact, get_contact_phone, list_all_contacts, delete_contact, search_contacts,
    create_file, read_file, delete_file, rename_file, list_directory, create_folder,
    open_file_or_folder, create_project_files,
    get_active_window, minimize_window, maximize_window, close_active_window,switch_window,
    open_website_or_app, run_command, lock_system,
    execute_powershell, execute_cmd,
    keyboard_mouse_control, volume_control, take_screenshot,
    read_clipboard, copy_to_clipboard, open_clipboard_history,
    running_processes, terminate_process,
    scan_network_devices, get_detailed_network_info, get_active_connections,
    get_router_info, network_bandwidth_usage, get_network_speed,
    ping_device, trace_route, port_scan, get_remote_device_info, get_device_services,
    ip_information, list_wifi_networks, connect_wifi, disconnect_wifi,
    flush_dns, renew_ip_address, control_network_adapter,
    disconnect_device_from_internet, reconnect_device_to_internet,
    check_admin_privileges, enable_packet_forwarding,
    get_router_admin_page, network_kill_switch,
    monitor_network_traffic, limit_device_bandwidth, remove_bandwidth_limit,
    get_network_devices_with_names,
    wake_on_lan, remote_shutdown, remote_restart, execute_remote_command,
    remote_desktop_connect, send_network_message,
    share_folder_on_network, remove_network_share, list_network_shares,
    access_network_share, map_network_drive, disconnect_network_drive,
    remote_file_copy,
    restart_system, shutdown_system, sleep_system, hibernate_system,
    login_with_gmail, generate_image,
    set_brightness, show_notification, schedule_task,
    universal_phone_unlocker, proximal_phone_unlocker, send_whatsapp_message, send_whatsapp_image, check_gmail_for_otp, manage_google_account,
    get_email_count, get_recent_email_senders, read_specific_email, reply_to_latest_email,
    get_saved_wifi_passwords, analyze_screen_content, summarize_website,
    github_get_user_info, github_list_repositories, github_get_repo_count, github_create_repository, github_delete_repository,
    get_youtube_subscribers, open_youtube_studio,
    generate_intelligence_briefing, satellite_recon, defense_protocol_alpha, perform_signal_intelligence_scan,
    send_whatsapp_message_background, make_phone_call, track_phone_number, get_latest_call_info, generate_phone_location_map, get_exact_location_via_adb, identify_object_from_camera,
    share_youtube_video_background, get_youtube_video_link,
    whatsapp_call, google_duo_call, start_google_meet, add_smart_reminder, set_timer, set_alarm,
    create_reminder, get_timer, list_active_timers, cancel_timer, list_reminders,
    snooze_reminder, dismiss_alarm, cancel_reminder, reschedule_reminder,
    play_chess_move_autonomously,
    vulnerability_scanner, local_network_brute_force, metasploit_demo_console, sniff_network_packets,
    wifi_deauth_attack,
    arp_poison_router_attack, dns_spoofing_attack, smb_eternalblue_scan,
    stealth_microphone_record, extract_browser_passwords, system_rootkit_scan,
    play_game_action, play_game_scenario, analyze_and_play, play_full_game, wireless_adb_connect, get_screen_info_via_adb,
    maintain_247_phone_link, get_phone_battery_and_status, generate_adb_pairing_qr,
    analyze_data_structure, generate_predictive_suggestions, update_edith_logic,
    deep_intelligence_search, execute_autonomous_chain, local_knowledge_cache, access_antigravity_neural_link,
    enable_focus_mode, disable_focus_mode,
    house_party_protocol, suit_integrity_diagnostics, holographic_threat_assessment,
    activate_stealth_mode, locate_avenger_base,
    deploy_to_firebase, build_and_deploy_app, activate_app_backend,
    play_game_pc,
]

import asyncio

# Global storage for the current session to allow proactive notifications
active_session = None

# ==============================
# BACKGROUND WORKER
# ==============================
async def reminder_worker():
    while True:
        try:
            await check_and_notify_reminders(active_session)
        except:
            pass
        await asyncio.sleep(60) # Check every minute

async def phone_link_worker():
    """Background task to maintain the 24/7 wireless ADB link."""
    while True:
        try:
            phone_ip = os.getenv("PHONE_IP")
            if phone_ip:
                # Check current status
                from .tools.adb_automation import adb_cmd
                res = adb_cmd(["devices"])
                if phone_ip not in res.stdout:
                    # Not connected, try to connect
                    adb_cmd(["connect", f"{phone_ip}:5555"])
        except Exception as e:
            print(f"⚠️ Phone Link Worker Error: {e}")
        await asyncio.sleep(300) # Check every 5 minutes


# INTENT ROUTER

def route_intent(q: str):
    q = q.lower()
    if "on tv" in q: return control_lg_tv, {"command": "on_youtube", "value": q.replace("on tv", "").replace("play", "").strip()}
    if "get link" in q or "give me the link" in q:
        return get_youtube_video_link, {"query": q.replace("get link", "").replace("give me the link", "").replace("for", "").strip()}
    if "share youtube" in q or "send youtube" in q:
         # Extract query and phone (if possible, else agent will ask)
         return share_youtube_video_background, {"query": q.replace("share youtube", "").replace("send youtube", "").strip()}
    if q.startswith("play"): 
        # Better mapping: play X -> play_music (which opens first result)
        # search X -> youtube_search_results (which shows list)
        return play_music, {"song": q.replace("play", "").strip()}
    if q.startswith("search youtube"):
        return youtube_search_results, {"query": q.replace("search youtube", "").strip()}
    if "email" in q: return send_email, {"query": q}
    if "unlock phone" in q: 
        if "wireless" in q or "second" in q: return proximal_phone_unlocker, {}
        return universal_phone_unlocker, {}
    if "unlock nearby" in q or "bluetooth unlock" in q or "wireless unlock" in q: return proximal_phone_unlocker, {}
    if "weather" in q: return get_weather, {"city": q.split()[-1]}
    if "time" in q: return current_time, {}
    if "internet" in q: return check_internet, {}
    if "weekly report" in q: return weekly_app_usage_report, {}
    if q.startswith("open") and "video" not in q: return open_website_or_app, {"query": q}
    if "shutdown" in q: return shutdown_system, {}
    if "restart" in q: return restart_system, {}
    if "hacking scan" in q: return vulnerability_scanner, {"target": q.split()[-1]}
    if "brute force" in q: return local_network_brute_force, {"target_ip": q.split()[-1]}
    if "metasploit" in q: return metasploit_demo_console, {}
    if q == "home" or "lg tv home" in q: return control_lg_tv, {"command": "home"}
    
    # --- JARVIS ADVANCED TIMER & REMINDER INTENTS ---
    if "how much time" in q and "timer" in q or "time left" in q and "timer" in q or "timer status" in q or "check timer" in q:
        clean_label = q.replace("how much time is left on my", "").replace("how much time left on", "").replace("time left on", "").replace("timer status", "").replace("check timer", "").replace("timer", "").strip() or "Timer"
        return get_timer, {"task_or_id": clean_label}

    if "cancel timer" in q or "stop timer" in q or "delete timer" in q:
        clean_label = q.replace("cancel timer", "").replace("stop timer", "").replace("delete timer", "").replace("my", "").replace("called", "").replace("for", "").strip() or "Timer"
        return cancel_timer, {"task_or_id": clean_label}

    if "list timers" in q or "show timers" in q or "active timers" in q or "pending timers" in q:
        return list_active_timers, {}

    if "timer" in q:
        import re
        seconds = 60
        match = re.search(r'(\d+)\s*(sec|min|hour)', q)
        if match:
            val = int(match.group(1))
            unit = match.group(2)
            if "min" in unit: seconds = val * 60
            elif "hour" in unit: seconds = val * 3600
            else: seconds = val
        # Extract label e.g. "called tea" or "for tea"
        task_label = "Timer"
        label_match = re.search(r'(?:called|named|for)\s+([a-zA-Z0-9_\s]+?)(?:\s+for|\s+in|$)', q)
        if label_match and not any(w in label_match.group(1) for w in ["sec", "min", "hour", "minute", "second"]):
            task_label = label_match.group(1).strip()
        elif "for" in q:
            after_for = q.split("for", 1)[1].strip()
            if not any(w in after_for for w in ["sec", "min", "hour", "minute", "second"]):
                task_label = after_for
        return set_timer, {"duration_seconds": seconds, "task": task_label}

    if "snooze" in q:
        import re
        min_match = re.search(r'(\d+)\s*min', q)
        snooze_mins = int(min_match.group(1)) if min_match else 5
        return snooze_reminder, {"reminder_id_or_title": q, "minutes": snooze_mins}

    if "dismiss" in q or "stop alarm" in q or "silence alarm" in q or "turn off alarm" in q:
        return dismiss_alarm, {"event_id": ""}

    if "cancel reminder" in q or "delete reminder" in q:
        clean_title = q.replace("cancel reminder", "").replace("delete reminder", "").replace("for", "").strip()
        return cancel_reminder, {"reminder_id_or_title": clean_title}

    if "reschedule reminder" in q or "change reminder" in q:
        # e.g. reschedule reminder study to 9 PM
        parts = q.split(" to ")
        if len(parts) > 1:
            title_part = parts[0].replace("reschedule reminder", "").strip()
            return reschedule_reminder, {"reminder_id_or_title": title_part, "new_due_at": parts[1].strip()}

    if "list reminders" in q or "show reminders" in q or "pending reminders" in q or "my reminders" in q or "show my reminders" in q:
        return list_reminders, {"status": "pending"}

    if "remind me" in q or "set a reminder" in q or "create reminder" in q:
        # e.g. "remind me in 20 minutes to take a break" or "remind me tomorrow at 8 AM to attend my meeting"
        import re
        q_clean = q.replace("remind me", "").replace("set a reminder", "").replace("create reminder", "").strip()
        # Look for "to <task>"
        if " to " in q_clean:
            time_part, task_part = q_clean.split(" to ", 1)
            return create_reminder, {"title": task_part.strip(), "due_at": time_part.strip()}
        else:
            return create_reminder, {"title": q_clean, "due_at": "in 15 minutes"}

    if "alarm" in q:
        import re
        match = re.search(r'(\d{1,2}:\d{2})', q)
        time_at = match.group(1) if match else "08:00"
        return set_alarm, {"time_at": time_at, "task": q}

    
    # Security Intents
    if "wifi deauth" in q: return wifi_deauth_attack, {"target_bssid": q.split()[-1]}
    if "arp poison" in q: return arp_poison_router_attack, {}
    if "dns spoof" in q: return dns_spoofing_attack, {"domain": "example.com", "fake_ip": "192.168.1.100"}
    if "eternalblue" in q or "smb scan" in q: return smb_eternalblue_scan, {"target_ip": q.split()[-1]}
    if "rdp brute" in q: return rdp_brute_force_attack, {"target_ip": q.split()[-1]}
    if "record microphone" in q or "spy mic" in q: return stealth_microphone_record, {"duration": 10}
    if "browser passwords" in q: return extract_browser_passwords, {}
    if "rootkit scan" in q: return system_rootkit_scan, {}
        
    # Movie Strategic Intents
    if "house party" in q: return house_party_protocol, {}
    if "status" in q or "diagnostics" in q or "suit integrity" in q: return suit_integrity_diagnostics, {}
    if "threat assessment" in q or "tactical scan" in q: return holographic_threat_assessment, {"target": "Local Area"}
    if "stealth mode" in q: return activate_stealth_mode, {}
    
    if "publish" in q: return publish_to_sandbox, {}
    
    # Gaming Intents
    if "play" in q and ("game" in q or "minecraft" in q or "free fire" in q or "freefire" in q):
        game = "PC Game"
        if "minecraft" in q: game = "Minecraft"
        if "free fire" in q or "freefire" in q: game = "Free Fire"
        
        # Determine platform
        if "phone" in q or "mobile" in q or "android" in q:
            return play_full_game, {"game_name": game, "duration_minutes": 15}
        else:
            return play_game_pc, {"game_name": game, "duration_minutes": 15}

    if "wireless debugging" in q or "connect adb" in q:
        import re
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', q)
        ip = ip_match.group(1) if ip_match else "192.168.1.1" # Default placeholder
        return wireless_adb_connect, {"ip": ip}

    if "24/7 phone" in q or "keep phone connected" in q or "link phone" in q:
        import re
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', q)
        ip = ip_match.group(1) if ip_match else None
        if ip:
            # We should save this IP for the worker
            return maintain_247_phone_link, {"ip": ip}
        return maintain_247_phone_link, {}

    if "track phone" in q or "locate number" in q or "phone tracker" in q:
        import re
        phone_match = re.search(r'(\+?\d{10,15})', q)
        phone = phone_match.group(1) if phone_match else None
        if phone:
            return generate_phone_location_map, {"phone_number": phone}

    if "pair" in q and ("qr" in q or "code" in q):
        return generate_adb_pairing_qr, {}

    if "antigravity" in q or "open link" in q or "neural link" in q or "talk to creator" in q:
        return access_antigravity_neural_link, {"objective": q}

    return None, None

# ==============================
# ULTRON UNIFIED ASSISTANT ENGINE
# ==============================
class Assistant:
    def __init__(self):
        self.brain = AntiGravityEngine(self, tools=ALL_TOOLS)

    async def on_user_message(self, context: RunContext, message: str) -> str:
        # 🔹 INSTANT BARGE-IN: Stop any ongoing speech playback immediately
        try:
            import friday_tools.tts_engine as tts_engine
            tts_engine.stop_speech()
        except Exception:
            pass

        # 🔹 NOTIFY PROACTIVE VISION OF USER INTERACTION
        try:
            from friday_tools.proactive_screen_vision import notify_interaction
            notify_interaction()
        except Exception:
            pass

        # 🔹 ANTI-GRAVITY REASONING LAYER
        try:
            await self.brain.get_environment_awareness()
        except Exception:
            pass

        # 🔹 7-TIER AUTONOMOUS MEMORY RETRIEVAL & CONTEXT BUILDER
        memory_context = ""
        try:
            from tools.ultron_memory_engine import MEMORY_ENGINE
            memory_context = MEMORY_ENGINE.build_injected_context(message)
        except Exception:
            try:
                from friday_tools.ultron_memory_engine import MEMORY_ENGINE
                memory_context = MEMORY_ENGINE.build_injected_context(message)
            except Exception:
                pass

        # 🔹 MISSION RECOVERY SHORTCUT: "Continue the project"
        if any(p in message.lower() for p in ["continue the project", "continue project", "continue my project", "what was i doing", "resume work"]):
            try:
                unfin = MEMORY_ENGINE.working.get_unfinished_summary()
                if unfin:
                    message = f"{message} (Persistent working memory across restart: {unfin}. State the project and next step, and proceed.)"
            except Exception:
                pass

        # 🔹 SMART STORE MEMORY
        if message.lower().startswith("remember"):
            text = message.replace("remember", "", 1).strip()
            return remember(text)

        # 🔹 SMART AUTO-DETECT & STORE
        stored_items = auto_detect_and_store(message)
        if stored_items:
            print(f"🧠 Auto-stored to 7-Tier Memory: {stored_items}")

        # 🔹 AUTO-READ FILE PATHS
        import re
        if re.search(r'[a-zA-Z]:\\[\\\w\s.-]+', message) or ("/" in message and "." in message):
            path_match = re.search(r'([a-zA-Z]:\\[\\\w\s.-]+)', message)
            if path_match:
                file_path = path_match.group(1).strip()
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    return await read_file(context, file_path)

        # 🔹 INTENT ROUTING FOR 700+ OS TOOLS
        tool, args = route_intent(message)
        if tool:
            res = await tool(context, **args) if "context" in str(tool.__code__.co_varnames) else await tool(**args)
            try:
                MEMORY_ENGINE.record_interaction(message, str(res))
            except Exception:
                pass
            return str(res)

        # 🔹 UNIVERSAL GENERAL-PURPOSE AUTONOMOUS COMPUTER AGENT (Section 1 & 2)
        # Evaluates if the query is an explicit imperative computer action goal
        def is_autonomous_task(text: str) -> bool:
            msg = text.strip().lower()
            conversational_starters = (
                "what", "why", "how", "who", "when", "where", "which",
                "can you explain", "explain", "tell me", "describe", "define",
                "do you know", "is it", "are you", "can you tell", "what is",
                "what are", "why is", "why are", "who is", "who are",
                "hello", "hi", "hey", "jarvis", "ultron", "status", "who made you"
            )
            if any(msg.startswith(qs) for qs in conversational_starters) or msg.endswith("?"):
                explicit_overrides = [
                    "open control panel", "launch control panel", "navigate to", "subscribe to",
                    "organize my files", "organize files in", "create a game", "build a game"
                ]
                if not any(cmd in msg for cmd in explicit_overrides):
                    return False

            action_patterns = [
                r"^(?:please\s+)?(?:open|launch|access|show)\s+(?:the\s+)?control\s+panel",
                r"^(?:please\s+)?(?:open|launch|access|show)\s+(?:the\s+)?settings",
                r"^(?:please\s+)?(?:open|launch|start)\s+[a-zA-Z0-9_\-\.\s]{2,25}\.(?:exe|cpl|msc)",
                r"^(?:please\s+)?(?:go to|navigate to|browse to|open)\s+(?:https?://|www\.|youtube|google|github)",
                r"^(?:please\s+)?subscribe\s+to\s+",
                r"^(?:please\s+)?play\s+(?:video|song|track)\s+on\s+youtube",
                r"^(?:please\s+)?(?:organize|clean(?:\s+up)?|sort)\s+(?:the\s+)?(?:files|folder|desktop|downloads)",
                r"^(?:please\s+)?automate\s+",
                r"^(?:please\s+)?(?:create|build|write|develop)\s+(?:a\s+)?(?:game|script|program|app|application)\s+(?:called|named|in|using)",
                r"^(?:please\s+)?click\s+(?:on\s+)?(?:the\s+)?",
                r"^(?:please\s+)?type\s+['\"].*['\"]\s+into\s+",
                r"^execute\s+goal\s*:",
                r"^autonomous\s+task\s*:",
            ]
            return any(re.search(pat, msg) for pat in action_patterns)

        if is_autonomous_task(message):
            try:
                from tools.ultron_autonomous_agent import AUTONOMOUS_AGENT, TASK_COMPLETED, TASK_BLOCKED
                agent_res = await AUTONOMOUS_AGENT.execute_goal(message)
                status = agent_res.get("status")

                if status == TASK_COMPLETED:
                    report = f"Task completed and verified, Sir. Executed {agent_res.get('steps_completed')} steps."
                    try:
                        import friday_tools.tts_engine as tts_engine
                        tts_engine.speak_text_sync(report)
                    except Exception:
                        pass
                    return report
                elif status == TASK_BLOCKED:
                    blocker = agent_res.get("blocker_reason", "Action paused for authorization.")
                    try:
                        import friday_tools.tts_engine as tts_engine
                        tts_engine.speak_text_sync(blocker)
                    except Exception:
                        pass
                    return f"[TASK BLOCKED]: {blocker}"
            except Exception as e:
                print(f"[AUTONOMOUS AGENT NOTE]: {e}")

        # 🔹 UNIFIED BOUNDED STREAMING AI CLIENT (Groq / Gemini Failover)
        try:
            import friday_tools.ai_client as ai_client
        except ImportError:
            import tools.ai_client as ai_client

        clean_sys = f"{ai_client.ULTRON_PERSONA}\n\n{memory_context}" if memory_context else ai_client.ULTRON_PERSONA

        try:
            try:
                print("\n[ULTRON]: ", end="", flush=True)
            except Exception:
                pass

            def _safe_print_delta(d: str):
                try:
                    sys.stdout.write(d)
                    sys.stdout.flush()
                except Exception:
                    try:
                        print(d.encode("ascii", errors="replace").decode("ascii"), end="", flush=True)
                    except Exception:
                        pass

            reply = await ai_client.generate_ai_response_stream(
                prompt=message,
                system_instruction=clean_sys,
                on_delta=_safe_print_delta
            )
            try:
                print("\n")
            except Exception:
                pass
            try:
                MEMORY_ENGINE.record_interaction(message, reply)
            except Exception:
                pass
            return reply
        except Exception:
            try:
                reply = ai_client.generate_ai_response(message)
                MEMORY_ENGINE.record_interaction(message, reply)
                return reply
            except Exception:
                return "All systems operational, Sir. How may I assist you?"


# ==============================
# RUNNER & INTERACTIVE LOOP
# ==============================
async def main_async():
    print("🚀 Initializing JARVIS Tactical AI System...")

    # 🔹 LOG RUNTIME IDENTITY TO PREVENT GHOST PROCESS DESYNC
    try:
        from friday_tools.runtime_diagnostics import log_runtime_identity
        log_runtime_identity("JARVIS_Main")
    except Exception:
        pass
    
    # 🔹 START BACKGROUND WORKERS
    asyncio.create_task(reminder_worker())
    asyncio.create_task(phone_link_worker())

    # 🔹 START PERSISTENT BACKGROUND SCHEDULER DAEMON (Runs even when window closes)
    try:
        from friday_tools.jarvis_reminder_daemon import start_daemon_detached
        start_daemon_detached()
    except Exception as e:
        print(f"⚠️ Scheduler Daemon note: {e}")

    # 🔹 START ULTRON Ω PROACTIVE COMPANION & SCREEN SENTINEL
    try:
        from friday_tools.ultron_companion_bridge import _COMPANION
        _COMPANION.start()
    except Exception as e:
        print(f"⚠️ Proactive Companion note: {e}")

    assistant = Assistant()
    context = RunContext()

    # 🔹 RESTORE UNFINISHED MISSION TASKS ACROSS PC RESTARTS
    try:
        from tools.ultron_memory_engine import MEMORY_ENGINE
        unfin = MEMORY_ENGINE.working.get_unfinished_summary()
        if unfin:
            print(f"🔄 [ULTRON PERSISTENT RECOVERY]: Restored mission state across restart -> {unfin}")
    except Exception:
        try:
            from friday_tools.ultron_memory_engine import MEMORY_ENGINE
            unfin = MEMORY_ENGINE.working.get_unfinished_summary()
            if unfin:
                print(f"🔄 [ULTRON PERSISTENT RECOVERY]: Restored mission state across restart -> {unfin}")
        except Exception:
            pass

    # 🔹 STARTUP GREETING
    try:
        import friday_tools.tts_engine as tts_engine
        greeting = "JARVIS tactical neural systems online. All protocols operational and at your command, Sir."
        print(f"🤖 JARVIS: {greeting}")
        tts_engine.speak_text_sync(greeting)
    except Exception as e:
        print(f"⚠️ Greeting notice: {e}")

    print("\n✅ Ready for chat and voice commands (Type 'exit' to quit)\n" + "═"*60)

    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Shivansh ➤ ")
            user_input = user_input.strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "shutdown"]:
                print("👋 Powering down ULTRON...")
                break

            await assistant.on_user_message(context, user_input)

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as err:
            print(f"❌ Error: {err}")


def run():
    import os
    import sys
    from .config import validate_env

    if not os.path.exists(".env"):
        from .installer import setup as installer_setup
        installer_setup()

    try:
        validate_env()
    except RuntimeError as e:
        print(f"⚠️ Configuration Error: {e}")
        return

    print("\n" + "="*30)
    print("      ULTRON NEURAL OS")
    print("      UNIFIED SINGLE-BRAIN ENGINE")
    print("="*30 + "\n")

    print("✅ ACCESS GRANTED. Welcome back, Sir.")
    asyncio.run(main_async())


def main():
    run()


if __name__ == "__main__":
    main()
