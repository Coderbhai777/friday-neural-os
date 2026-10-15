import os
import subprocess
import time
import socket
import random
import webbrowser

def adb_cmd(cmd_list, device=None, timeout=15):
    import shutil
    adb_path = shutil.which("adb")
    if not adb_path:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates = [
            os.path.join(base_path, "platform-tools", "adb.exe"),
            os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
            r"C:\platform-tools\adb.exe",
            r"C:\Program Files\Android\platform-tools\adb.exe"
        ]
        for c in candidates:
            if os.path.exists(c):
                adb_path = c
                break
        if not adb_path:
            adb_path = "adb"

    target = ["-s", device] if device else []
    full_cmd = [adb_path] + target + cmd_list
    try:
        return subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return subprocess.CompletedProcess(args=full_cmd, returncode=1, stdout="", stderr="[ERROR] ADB executable (adb.exe) not found on system PATH or platform-tools.")
    except Exception as e:
        return subprocess.CompletedProcess(args=full_cmd, returncode=1, stdout="", stderr=str(e))

async def wireless_adb_connect(ip: str, port: str = "5555") -> str:
    """Connects to a device via Wireless Debugging (ADB over TCP/IP)."""
    res = adb_cmd(["connect", f"{ip}:{port}"])
    if "connected to" in res.stdout:
        return f"✅ Linked to device at {ip}:{port} via Neural Wireless Link."
    return f"❌ Connection failed: {res.stdout or res.stderr}"

async def play_game_action(action: str, params: str = "") -> str:
    """
    Executes specific ADB actions for game automation.
    Actions: 
    - click x,y: Click at coordinates
    - swipe x1,y1,x2,y2,duration: Swipe from start to end
    - key keycode: Send a specific keycode (e.g. 66 for Enter)
    - text string: Type text
    - home: Go to home screen
    - back: Press back button
    """
    try:
        if action == "click":
            x, y = params.split(",")
            adb_cmd(["shell", "input", "tap", x.strip(), y.strip()])
        elif action == "swipe":
            x1, y1, x2, y2, d = params.split(",")
            adb_cmd(["shell", "input", "swipe", x1.strip(), y1.strip(), x2.strip(), y2.strip(), d.strip()])
        elif action == "key":
            adb_cmd(["shell", "input", "keyevent", params.strip()])
        elif action == "text":
            adb_cmd(["shell", "input", "text", params.strip()])
        elif action == "home":
            adb_cmd(["shell", "input", "keyevent", "3"])
        elif action == "back":
            adb_cmd(["shell", "input", "keyevent", "4"])
        else:
            return f"Unknown action: {action}"
        
        return f"Action {action} executed with params {params}"
    except Exception as e:
        return f"ADB Error: {e}"

async def play_game_scenario(game: str, scenario: str) -> str:
    """
    Executes advanced game-specific sequences.
    Games: 'minecraft', 'freefire'.
    Scenarios for Minecraft: 'mine_diamond', 'build_wall', 'survive_night'.
    Scenarios for Free Fire: 'auto_loot', 'combat_mode', 'evade'.
    """
    game = game.lower()
    scenario = scenario.lower()
    
    if game == "minecraft":
        if scenario == "mine_block":
            # Hold tap for 2 seconds to mine
            return adb_cmd(["shell", "input", "swipe", "500", "500", "500", "500", "2000"]).stdout or "Mining action sent."
        elif scenario == "move_forward":
            # Swipe up on left joystick area
            return adb_cmd(["shell", "input", "swipe", "200", "800", "200", "600", "500"]).stdout or "Moving forward."
        elif scenario == "jump":
            # Tap jump button area (typical bottom right)
            return adb_cmd(["shell", "input", "tap", "900", "800"]).stdout or "Jumping."
            
    elif game == "freefire":
        if scenario == "shoot":
            # Rapid fire on fire button
            for _ in range(5):
                adb_cmd(["shell", "input", "tap", "850", "750"])
                time.sleep(0.1)
            return "Firing sequence triggered."
        elif scenario == "reload":
            return adb_cmd(["shell", "input", "tap", "900", "150"]).stdout or "Reloading."
        elif scenario == "run":
            # Hold run button or swipe joystick deep
            return adb_cmd(["shell", "input", "swipe", "150", "850", "150", "500", "1000"]).stdout or "Sprinting."

    return f"Scenario {scenario} for {game} is not yet optimized in my neural pathways."

async def analyze_and_play(game_name: str, goal: str) -> str:
    """
    Vision-Assisted Gaming: EDITH captures the screen, analyzes the situation, and takes the best action.
    Example: 'EDITH, survive in Minecraft' or 'EDITH, find enemies in Free Fire'.
    """
    # 1. Capture screen via ADB
    img_path = "game_temp.png"
    adb_cmd(["shell", "screencap", "-p", "/sdcard/game.png"])
    adb_cmd(["pull", "/sdcard/game.png", img_path])
    
    if not os.path.exists(img_path):
        return "❌ Failed to capture game screen. Is the device connected?"
        
    try:
        from google import genai
        from PIL import Image
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        img = Image.open(img_path)
        
        # 2. Analyze Situation
        prompt = f"You are playing {game_name}. Goal: {goal}. Based on this screenshot, what is the SINGLE MOST IMPORTANT ADB action to take? Respond ONLY with one of: 'click x,y', 'swipe x1,y1,x2,y2,d', 'none'."
        response = client.models.generate_content(model='gemini-1.5-flash', contents=[prompt, img])
        action_text = response.text.strip().lower()
        
        # 3. Execute Action
        result = ""
        if "click" in action_text:
            coords = action_text.replace("click", "").strip()
            result = await play_game_action("click", coords)
        elif "swipe" in action_text:
            coords = action_text.replace("swipe", "").strip()
            result = await play_game_action("swipe", coords)
        else:
            result = "No clear action identified. Standing by."
            
        os.remove(img_path)
        return f"🎮 AI Decision for {game_name}: {action_text}\n⚡ Execution: {result}"
        
    except Exception as e:
        if os.path.exists(img_path): os.remove(img_path)
        return f"❌ Neural Gaming Error: {e}"

async def play_full_game(game_name: str, duration_minutes: int = 5) -> str:
    """
    Autonomous Full Game Play: EDITH takes complete control of the game for a specified duration.
    Uses continuous vision and decision updates to play autonomously.
    """
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    # Check for specific device if wireless debugging is active
    # (Usually the last connected device is the default)
    
    log = [f"🚀 Initializing Full Autonomous Play for {game_name}...", f"⏱️ Mission Duration: {duration_minutes} minutes"]
    
    try:
        from google import genai
        from PIL import Image
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        while time.time() < end_time:
            # 1. Capture screen
            img_path = f"game_play_temp.png"
            adb_cmd(["shell", "screencap", "-p", "/sdcard/game.png"])
            adb_cmd(["pull", "/sdcard/game.png", img_path])
            
            if not os.path.exists(img_path):
                log.append("❌ Screen capture interrupted. Aborting mission.")
                break
                
            img = Image.open(img_path)
            
            # 2. Analyze Situation
            prompt = (f"You are playing {game_name} autonomously. Analyze the screen and provide the NEXT action. "
                     "Return ONLY a command in this format: 'click x,y' or 'swipe x1,y1,x2,y2,d'. "
                     "If no action is needed, return 'none'.")
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=[prompt, img])
            action_text = response.text.strip().lower()
            
            # 3. Execute Action
            if "click" in action_text:
                coords = action_text.replace("click", "").strip()
                await play_game_action("click", coords)
                print(f"🎮 Autonomous Action: {action_text}")
            elif "swipe" in action_text:
                coords = action_text.replace("swipe", "").strip()
                await play_game_action("swipe", coords)
                print(f"🎮 Autonomous Action: {action_text}")
            
            os.remove(img_path)
            time.sleep(2) # Tactical pause between frames
            
        log.append("🏆 Mission complete. Relinquishing control to the user.")
        return "\n".join(log)
        
    except Exception as e:
        return f"❌ Autonomous Play Error: {e}"

async def maintain_247_phone_link(ip: str = None) -> str:
    """
    Ensures the phone stays connected 24/7 to EDITH.
    If IP is provided, it saves it and tries to re-establish wireless link.
    If no IP, it attempts to wake any existing USB/Wireless link.
    """
    logs = ["🔄 Initializing 24/7 Persistent Phone Link..."]
    
    # 1. Persistence: If IP provided, save it to .env
    if ip:
        logs.append(f"💾 Saving Phone IP {ip} to neural memory...")
        # Update .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
            
            written = False
            with open(env_path, "w") as f:
                for line in lines:
                    if line.startswith("PHONE_IP="):
                        f.write(f"PHONE_IP={ip}\n")
                        written = True
                    else:
                        f.write(line)
                if not written:
                    f.write(f"PHONE_IP={ip}\n")
            os.environ["PHONE_IP"] = ip
            
    current_ip = ip or os.getenv("PHONE_IP")
    
    # 2. Try to wake/connect
    res = adb_cmd(["devices"])
    if "device" in res.stdout.replace("List of devices attached", "").strip():
        logs.append("✅ Phone detected. Waking up background services...")
        adb_cmd(["shell", "input", "keyevent", "224"]) # Wake up
    elif current_ip:
        logs.append(f"📡 Device offline. Attempting Wireless Re-link to {current_ip}...")
        res_conn = adb_cmd(["connect", f"{current_ip}:5555"])
        if "connected" in res_conn.stdout:
            logs.append(f"✅ Re-established link to {current_ip}.")
        else:
            logs.append(f"❌ Re-link failed: {res_conn.stdout}")
    else:
        logs.append("⚠️ No device connected and no IP registered for wireless link.")

    return "\n".join(logs)

async def get_phone_battery_and_status() -> str:
    """Checks the current battery level and connection health of the phone."""
    battery = adb_cmd(["shell", "dumpsys", "battery", "|", "grep", "level"])
    status = adb_cmd(["get-state"])
    
    b_level = battery.stdout.strip() or "Unknown"
    s_state = status.stdout.strip() or "Disconnected"
    
    return f"📱 Phone Status: {s_state} | 🔋 Battery: {b_level}"

async def generate_adb_pairing_qr() -> str:
    """
    Generates a Neural Pairing QR Code for Wireless Debugging.
    The user scans this QR from the 'Pair with QR Code' screen in Android Developer Options.
    """
    # 1. Determine Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    # 2. Generate Random Pairing Code and Port
    pairing_code = str(random.randint(100000, 999999))
    
    # 3. Create QR Content (Android format)
    # Format: WIFI:T:ADB;S:EDITH_PAIR;P:123456;;
    qr_data = f"WIFI:T:ADB;S:EDITH_NS;P:{pairing_code};;"
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={qr_data}"

    # 4. Create HTML Dashboard
    html_path = os.path.abspath("adb_pairing_dashboard.html")
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EDITH | ADB Wireless Pairing</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: #00d4ff; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .card {{ background: #1a1a1a; padding: 40px; border-radius: 20px; border: 1px solid #00d4ff; box-shadow: 0 0 30px rgba(0, 212, 255, 0.2); text-align: center; }}
            h1 {{ margin-top: 0; letter-spacing: 2px; }}
            img {{ border: 10px solid white; border-radius: 10px; margin: 20px 0; }}
            .info {{ font-size: 1.1em; color: #fff; margin-bottom: 20px; }}
            .code {{ font-size: 2em; font-weight: bold; background: #00d4ff; color: #000; padding: 5px 20px; border-radius: 10px; }}
            .step {{ font-size: 0.9em; color: #888; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>NEURAL PAIRING LINK</h1>
            <p class="info">Scan the code below in <b>Wireless Debugging</b></p>
            <img src="{qr_api_url}" alt="ADB QR Code">
            <div class="code">{pairing_code}</div>
            <p class="step">1. Open Developer Options<br>2. Wireless Debugging -> Pair with QR Code<br>3. Scan this screen</p>
        </div>
        <script>
            // Periodic status check could go here
        </script>
    </body>
    </html>
    """
    
    with open(html_path, "w") as f:
        f.write(html_content)

    # 5. Open Web Browser
    webbrowser.open(f"file://{html_path}")

    return f"🚀 Neural Pairing Dashboard deployed. Sir, please scan the QR code on your screen using the 'Pair with QR Code' option on your phone.\n\nPairing Code: {pairing_code}\nLocal IP detected: {local_ip}"

async def get_screen_info_via_adb() -> str:
    """Gets screen resolution and current activity for context."""
    res = adb_cmd(["shell", "wm", "size"])
    activity = adb_cmd(["shell", "dumpsys", "window", "|", "grep", "mCurrentFocus"])
    return f"Screen: {res.stdout.strip()}, Activity: {activity.stdout.strip()}"
