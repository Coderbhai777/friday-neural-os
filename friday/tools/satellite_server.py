"""
ULTRON Mobile Satellite Host Server
Runs on your laptop to link your phone and laptop in real time.
Features:
- Auto IP discovery & QR code terminal pairing
- Real-time bidirectional synchronization with ~/Documents/ULTRON_Data/ultron_memory.json
- Intelligent Device-Aware Intent Routing:
  * Phone Local Actions (YouTube, WhatsApp, Torch, Camera, Spotify, Maps) -> Executed on Phone
  * Laptop Compute / AI Tasks (Deep AI models, code, PC files, exams, memory) -> Executed on Laptop
- Low-latency WebSocket voice channel with en-GB-RyanNeural audio streaming
- Embedded Cyberpunk HUD Mobile Web App & APK download endpoint
"""

import os
import io
import re
import json
import time
import socket
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure ULTRON directories exist
DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(DATA_DIR / ".env")

app = FastAPI(title="ULTRON Mobile Satellite Host")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_CACHE_DIR = DATA_DIR / "satellite_audio_cache"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_local_ip() -> str:
    """Finds the primary local LAN IP address of the laptop."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to public DNS to determine default routing interface (no packets sent)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def print_server_banner(port: int = 8765):
    """Prints terminal pairing banner and ASCII QR code for phone scanning."""
    ip = get_local_ip()
    url = f"http://{ip}:{port}"
    print("\n" + "=" * 65)
    print("🤖 ULTRON MOBILE SATELLITE HOST SERVER ACTIVE")
    print("=" * 65)
    print(f"📡 Local LAN URL: {url}")
    print(f"📁 Real-Time Memory Link: {DATA_DIR / 'ultron_memory.json'}")
    print("=" * 65)

    try:
        import qrcode
        qr = qrcode.QRCode(box_size=1, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        print("📲 SCAN WITH YOUR PHONE CAMERA TO CONNECT INSTANTLY:")
        qr.print_ascii(invert=True)
    except Exception:
        pass
    print("=" * 65 + "\n")


# ==============================================================================
# INTENT ROUTING LOGIC (Phone vs Laptop Decision Matrix)
# ==============================================================================

def classify_and_route_intent(prompt: str) -> Dict[str, Any]:
    """
    Classifies user commands into Phone-Local vs Laptop-Offloaded execution.
    """
    p_lower = prompt.lower().strip()

    # 1. YouTube -> Phone Local Intent
    if any(k in p_lower for k in ["open youtube", "youtube chalao", "play on youtube", "search youtube"]):
        query = ""
        m = re.search(r'(?:play|search)\s+(.+?)(?:\s+on\s+youtube|$)', p_lower)
        if m:
            query = m.group(1).strip()
        intent_url = f"https://www.youtube.com/results?search_query={query}" if query else "https://www.youtube.com"
        android_uri = f"vnd.youtube://results?q={query}" if query else "vnd.youtube:"
        return {
            "execution_target": "phone_local",
            "action": "open_youtube",
            "package": "com.google.android.youtube",
            "intent_uri": android_uri,
            "fallback_url": intent_url,
            "query": query,
            "speech": f"Opening YouTube{' for ' + query if query else ''} on your phone, Sir."
        }

    # 2. WhatsApp -> Phone Local Intent
    if any(k in p_lower for k in ["open whatsapp", "whatsapp chalao", "whatsapp message", "whatsapp pe"]):
        return {
            "execution_target": "phone_local",
            "action": "open_whatsapp",
            "package": "com.whatsapp",
            "intent_uri": "whatsapp://send",
            "fallback_url": "https://api.whatsapp.com",
            "speech": "Opening WhatsApp on your phone, Sir."
        }

    # 3. Flashlight / Torch -> Phone Local
    if any(k in p_lower for k in ["turn on flashlight", "torch on", "flashlight on", "torch chalao"]):
        return {
            "execution_target": "phone_local",
            "action": "torch",
            "state": "on",
            "speech": "Flashlight activated on your phone, Sir."
        }
    if any(k in p_lower for k in ["turn off flashlight", "torch off", "flashlight off", "torch band karo"]):
        return {
            "execution_target": "phone_local",
            "action": "torch",
            "state": "off",
            "speech": "Flashlight deactivated, Sir."
        }

    # 4. Camera -> Phone Local
    if any(k in p_lower for k in ["open camera", "take photo", "camera chalao", "click photo"]):
        return {
            "execution_target": "phone_local",
            "action": "camera",
            "intent_uri": "android.media.action.IMAGE_CAPTURE",
            "speech": "Opening camera on your phone, Sir."
        }

    # 5. Spotify / Music -> Phone Local
    if any(k in p_lower for k in ["open spotify", "spotify chalao", "play music on spotify"]):
        return {
            "execution_target": "phone_local",
            "action": "open_spotify",
            "package": "com.spotify.music",
            "intent_uri": "spotify:",
            "fallback_url": "https://open.spotify.com",
            "speech": "Launching Spotify on your phone, Sir."
        }

    # 6. Maps / Navigation -> Phone Local
    if any(k in p_lower for k in ["open maps", "navigate to", "google maps", "directions to"]):
        loc_match = re.search(r'(?:navigate to|directions to|location of)\s+(.+)', p_lower)
        loc = loc_match.group(1).strip() if loc_match else ""
        return {
            "execution_target": "phone_local",
            "action": "open_maps",
            "intent_uri": f"geo:0,0?q={loc}" if loc else "geo:0,0",
            "fallback_url": f"https://www.google.com/maps/search/{loc}" if loc else "https://www.google.com/maps",
            "speech": f"Opening Maps navigation{' to ' + loc if loc else ''} on your phone, Sir."
        }

    # 7. Heavy Task / AI / Memory / Code / General Query -> Laptop Compute
    return {
        "execution_target": "laptop_compute",
        "action": "ai_response"
    }


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.get("/api/status")
async def get_status():
    """Health check and laptop status indicator."""
    import psutil
    return {
        "status": "online",
        "system": "ULTRON Neural Satellite Hub",
        "host_ip": get_local_ip(),
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else 100,
        "cpu_percent": psutil.cpu_percent(),
        "memory_file": str(DATA_DIR / "ultron_memory.json"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


@app.get("/api/memory")
async def get_memory():
    """Returns real-time contents of ultron_memory.json."""
    import friday_tools.ultron_memory as mem
    return mem.load_memory()


@app.post("/api/memory/fact")
async def save_fact(req: Request):
    """Saves a fact directly into laptop's ultron_memory.json in real time."""
    data = await req.json()
    key = data.get("key", "").strip()
    val = data.get("value", "").strip()
    if key and val:
        import friday_tools.ultron_memory as mem
        res = mem.save_fact(key, val)
        return {"status": "success", "result": res}
    return {"status": "error", "message": "Missing key or value"}


@app.post("/api/chat")
async def process_chat(req: Request):
    """
    Main communication endpoint.
    Performs device-aware intent routing, memory sync, and AI generation.
    Enforces instant barge-in: cuts off any currently playing speech immediately.
    """
    # 0. Instant Barge-In: Halt ongoing speech on laptop
    try:
        import friday_tools.tts_engine as tts_engine
        tts_engine.stop_speech()
    except Exception:
        pass

    body = await req.json()
    prompt = body.get("prompt", "").strip()
    if not prompt:
        return JSONResponse({"status": "error", "message": "Empty prompt"})

    # 1. Classify Intent
    routing = classify_and_route_intent(prompt)

    # 2. If Phone Local Action, return immediately with intent payload
    if routing["execution_target"] == "phone_local":
        # Record user turn in laptop history
        try:
            import friday_tools.conversation_history as conv_mem
            conv_mem.add_conversation_turn("user", prompt, model_name="Phone-Satellite")
            conv_mem.add_conversation_turn("assistant", routing["speech"], model_name="Phone-IntentRouter")
        except Exception:
            pass

        return {
            "status": "success",
            "execution_target": "phone_local",
            "routing": routing,
            "reply": routing["speech"],
            "speech": routing["speech"]
        }

    # 3. Laptop Execution (Groq / Gemini Multi-Model Failover)
    import friday_tools.ai_client as ai_client
    import friday_tools.conversation_history as conv_mem

    # Generate response
    reply = ai_client.generate_ai_response(prompt)

    # Generate audio for phone playback via Edge-TTS
    audio_id = f"speech_{int(time.time()*1000)}"
    audio_file = AUDIO_CACHE_DIR / f"{audio_id}.mp3"

    try:
        import edge_tts
        communicate = edge_tts.Communicate(
            text=reply[:300],  # Cap audio to executive verbal summary
            voice="en-GB-RyanNeural",
            rate="+0%",
            pitch="-5Hz"
        )
        await communicate.save(str(audio_file))
        audio_url = f"/api/audio/{audio_id}.mp3"
    except Exception as err:
        audio_url = ""

    return {
        "status": "success",
        "execution_target": "laptop_compute",
        "routing": routing,
        "reply": reply,
        "speech": reply[:250],
        "audio_url": audio_url
    }


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """Streams generated RyanNeural audio MP3 to the phone."""
    file_path = AUDIO_CACHE_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    return Response(status_code=404)


@app.get("/download/ultron.apk")
async def download_apk():
    """Serves the standalone compiled Android APK directly to the phone."""
    apk_path = DATA_DIR / "ULTRON_Satellite.apk"
    if apk_path.exists():
        return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename="ULTRON_Satellite.apk")
    return JSONResponse({"status": "error", "message": "APK is currently generating."})


@app.get("/manifest.json")
async def get_pwa_manifest():
    """Returns PWA web manifest for native 1-tap Android app installation."""
    manifest = {
        "name": "ULTRON Satellite",
        "short_name": "ULTRON",
        "description": "ULTRON Mobile AI Satellite & Host Communicator",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#070c16",
        "theme_color": "#ffaa30",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/api/icon",
                "sizes": "512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    }
    return JSONResponse(manifest)


@app.get("/api/icon")
async def get_app_icon():
    """Returns dynamic SVG app icon."""
    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <rect width="512" height="512" rx="100" fill="#070c16"/>
  <circle cx="256" cy="256" r="180" stroke="#ffaa30" stroke-width="12" fill="none" stroke-dasharray="20,10"/>
  <circle cx="256" cy="256" r="130" stroke="#ffaa30" stroke-width="8" fill="#111827"/>
  <circle cx="256" cy="256" r="70" fill="#ffaa30"/>
  <text x="256" y="275" font-size="60" text-anchor="middle" fill="#070c16" font-family="monospace" font-weight="900">AI</text>
</svg>"""
    return Response(content=svg_icon, media_type="image/svg+xml")


@app.get("/sw.js")
async def get_service_worker():
    """Service Worker script for WebAPK standalone installation."""
    sw_script = """
self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  // Let network handle real-time chat & api calls
  e.respondWith(fetch(e.request).catch(() => new Response('ULTRON Offline')));
});
"""
    return Response(content=sw_script, media_type="application/javascript")


# ==============================================================================
# WEBSOCKET REAL-TIME VOICE & EVENT CHANNEL
# ==============================================================================

@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """Low-latency WebSocket channel for phone voice & silent chat."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            prompt = msg.get("prompt", "").strip()
            if not prompt:
                continue

            routing = classify_and_route_intent(prompt)
            if routing["execution_target"] == "phone_local":
                await websocket.send_json({
                    "type": "intent",
                    "execution_target": "phone_local",
                    "routing": routing,
                    "reply": routing["speech"]
                })
            else:
                import friday_tools.ai_client as ai_client
                reply = ai_client.generate_ai_response(prompt)
                await websocket.send_json({
                    "type": "response",
                    "execution_target": "laptop_compute",
                    "reply": reply,
                    "speech": reply[:250]
                })
    except WebSocketDisconnect:
        pass


# ==============================================================================
# EMBEDDED MOBILE HUD WEB APP (Rendered on Phone)
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
async def mobile_hud_page():
    """Serves the full Cyberpunk Mobile HUD to the phone browser / PWA / Webview."""
    local_ip = get_local_ip()
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <meta name="theme-color" content="#070c16">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="ULTRON">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" href="/api/icon" type="image/svg+xml">
  <title>ULTRON Satellite HUD</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes pulse-glow {{
      0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 15px rgba(255, 170, 48, 0.6)); }}
      50% {{ transform: scale(1.06); filter: drop-shadow(0 0 30px rgba(255, 170, 48, 0.9)); }}
    }}
    @keyframes wave-bar {{
      0%, 100% {{ height: 6px; }}
      50% {{ height: 28px; }}
    }}
    .orb-pulse {{ animation: pulse-glow 3s infinite ease-in-out; }}
    .wave-anim {{ animation: wave-bar 1.2s infinite ease-in-out; }}
    .cyber-grid {{
      background-size: 24px 24px;
      background-image: 
        linear-gradient(to right, rgba(255, 170, 48, 0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 170, 48, 0.05) 1px, transparent 1px);
    }}
  </style>
</head>
<body class="bg-[#070c16] text-slate-100 min-h-screen flex flex-col justify-between p-4 font-sans select-none cyber-grid overflow-hidden">
  
  <!-- Header Bar -->
  <div class="flex items-center justify-between py-2 border-b border-amber-500/20 bg-slate-950/80 rounded-2xl px-4 backdrop-blur z-20">
    <div class="flex items-center gap-2">
      <div class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></div>
      <div>
        <div class="text-xs font-black tracking-widest text-amber-400">ULTRON SATELLITE</div>
        <div id="linkStatus" class="text-[9px] font-mono text-emerald-400">LINKED: {local_ip}:8765</div>
      </div>
    </div>
    <div class="flex items-center gap-1.5">
      <button id="installAppBtn" onclick="triggerInstallApp()" class="px-2.5 py-1 rounded-lg bg-emerald-500/20 border border-emerald-500/50 text-[10px] font-mono text-emerald-300 font-bold flex items-center gap-1 hover:bg-emerald-500/30 transition">
        <span>📲 Install App</span>
      </button>
      <a href="/download/ultron.apk" class="px-2 py-1 rounded-lg bg-amber-500/20 border border-amber-500/40 text-[10px] font-mono text-amber-300 font-bold flex items-center gap-1">
        <span>APK</span>
      </a>
    </div>
  </div>

  <!-- Router Target Notification Badge -->
  <div id="routingBadge" class="mt-3 py-1.5 px-3 rounded-xl bg-slate-900/90 border border-amber-500/30 flex items-center justify-between text-[11px] font-mono transition-all z-20">
    <span class="text-slate-400">EXECUTION ROUTER:</span>
    <span id="routingTarget" class="text-emerald-400 font-bold">READY (WAITING)</span>
  </div>

  <!-- Central Arc Reactor Holographic Orb -->
  <div class="flex-1 flex flex-col items-center justify-center my-auto relative z-10">
    <div class="relative w-48 h-48 flex items-center justify-center">
      <div class="absolute inset-0 rounded-full border border-dashed border-amber-500/40 animate-spin" style="animation-duration: 25s;"></div>
      <div class="absolute inset-3 rounded-full border border-amber-400/30"></div>
      
      <div id="coreOrb" onclick="toggleVoiceRecording()" class="w-32 h-32 rounded-full bg-gradient-to-tr from-amber-600 via-yellow-500 to-amber-300 orb-pulse flex items-center justify-center shadow-lg shadow-amber-500/50 cursor-pointer active:scale-95 transition">
        <div class="w-24 h-24 rounded-full bg-slate-950/90 border border-amber-400/80 flex flex-col items-center justify-center">
          <span class="text-2xl">🤖</span>
          <span class="text-[9px] font-mono font-bold tracking-widest text-amber-300 mt-1">ULTRON</span>
        </div>
      </div>
    </div>

    <!-- Soundwave Visualizer -->
    <div class="flex items-center gap-1.5 mt-5 h-8 px-4">
      <div class="w-1 bg-amber-400/80 rounded-full wave-anim" style="animation-delay: 0.1s"></div>
      <div class="w-1 bg-amber-400/80 rounded-full wave-anim" style="animation-delay: 0.3s"></div>
      <div class="w-1 bg-amber-400/80 rounded-full wave-anim" style="animation-delay: 0.5s"></div>
      <div class="w-1 bg-amber-300 rounded-full wave-anim" style="animation-delay: 0.2s"></div>
      <div class="w-1 bg-amber-400/80 rounded-full wave-anim" style="animation-delay: 0.4s"></div>
      <div class="w-1 bg-amber-400/80 rounded-full wave-anim" style="animation-delay: 0.6s"></div>
      <div class="w-1 bg-amber-400/80 rounded-full wave-anim" style="animation-delay: 0.15s"></div>
    </div>

    <!-- Live Subtitles & Response View -->
    <div class="mt-3 text-center px-4 max-w-sm">
      <div id="statusText" class="text-xs font-mono text-amber-400 font-semibold tracking-wide">
        "Standing by for voice or silent chat, Sir."
      </div>
      <div id="detailText" class="text-[11px] text-slate-400 mt-1.5 max-h-24 overflow-y-auto leading-relaxed">
        RyanNeural 24kHz active | Memory synced with Laptop JSON
      </div>
    </div>
  </div>

  <!-- Bottom Interaction Dock -->
  <div class="space-y-2 bg-slate-950/90 border border-amber-500/20 p-3 rounded-2xl backdrop-blur z-20">
    <div class="flex items-center justify-between text-[10px] font-mono text-slate-400 px-1">
      <span class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> ultron_memory.json Linked</span>
      <span class="text-amber-400">en-GB-RyanNeural</span>
    </div>

    <!-- Text Input Bar -->
    <div class="flex items-center gap-2">
      <input type="text" id="chatInput" placeholder="Command or ask Ultron..." class="flex-1 bg-slate-900 border border-amber-500/30 focus:border-amber-400 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 outline-none">
      <button onclick="submitChat()" class="px-3.5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition">
        SEND
      </button>
    </div>

    <!-- Tap to Speak Voice Button -->
    <button id="voiceMicBtn" onclick="toggleVoiceRecording()" class="w-full py-3 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 active:scale-98 transition">
      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
      <span id="micLabel">TAP TO SPEAK</span>
    </button>
  </div>

  <audio id="audioPlayer" class="hidden"></audio>

  <script>
    // PWA Service Worker & Install Handler
    let deferredPrompt = null;
    window.addEventListener('beforeinstallprompt', (e) => {{
      e.preventDefault();
      deferredPrompt = e;
    }});

    function triggerInstallApp() {{
      if (deferredPrompt) {{
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((res) => {{
          deferredPrompt = null;
        }});
      }} else {{
        alert("To install as a dedicated phone app: tap Chrome's 3-dot menu (⋮) at top right and select 'Install app' or 'Add to Home screen'.");
      }}
    }}

    if ('serviceWorker' in navigator) {{
      navigator.serviceWorker.register('/sw.js').catch(() => {{}});
    }}

    let isRecording = false;
    let recognition = null;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRec();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {{
        isRecording = true;
        document.getElementById('micLabel').innerText = 'LISTENING...';
        document.getElementById('voiceMicBtn').classList.add('animate-pulse', 'from-red-500', 'to-red-600');
        document.getElementById('coreOrb').style.filter = "drop-shadow(0 0 45px rgba(255, 50, 50, 1))";
      }};

      recognition.onresult = (event) => {{
        const transcript = event.results[0][0].transcript;
        document.getElementById('statusText').innerText = `"${{transcript}}"`;
        sendCommand(transcript);
      }};

      recognition.onerror = () => {{ resetMicUI(); }};
      recognition.onend = () => {{ resetMicUI(); }};
    }}

    function resetMicUI() {{
      isRecording = false;
      document.getElementById('micLabel').innerText = 'TAP TO SPEAK';
      document.getElementById('voiceMicBtn').classList.remove('animate-pulse', 'from-red-500', 'to-red-600');
      document.getElementById('coreOrb').style.filter = "";
    }}

    function toggleVoiceRecording() {{
      if (!recognition) {{
        alert('Voice speech recognition not supported in this browser. Please use the text chat bar.');
        return;
      }}
      if (isRecording) {{
        recognition.stop();
      }} else {{
        recognition.start();
      }}
    }}

    async function sendCommand(promptText) {{
      // Instant Barge-In: Halt any phone audio playback immediately
      const currentAudio = document.getElementById('audioPlayer');
      if (currentAudio) {{
        currentAudio.pause();
        currentAudio.currentTime = 0;
      }}

      const badge = document.getElementById('routingBadge');
      const target = document.getElementById('routingTarget');
      const detailText = document.getElementById('detailText');

      detailText.innerText = 'Routing and processing command...';

      try {{
        const resp = await fetch('/api/chat', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ prompt: promptText }})
        }});
        const data = await resp.json();

        if (data.status === 'success') {{
          const isPhone = data.execution_target === 'phone_local';
          
          if (isPhone) {{
            target.innerText = '📱 PHONE LOCAL ACTION';
            target.className = 'text-amber-400 font-bold';
            badge.className = 'mt-3 py-1.5 px-3 rounded-xl bg-amber-950/60 border border-amber-500/60 flex items-center justify-between text-[11px] font-mono transition-all z-20';
            detailText.innerText = data.reply;

            // Execute local action on phone via Android intent
            const routing = data.routing;
            if (routing.action === 'open_youtube') {{
              setTimeout(() => {{
                window.location.href = routing.intent_uri || routing.fallback_url;
              }}, 400);
            }} else if (routing.action === 'open_whatsapp') {{
              setTimeout(() => {{
                window.location.href = routing.intent_uri || routing.fallback_url;
              }}, 400);
            }} else if (routing.action === 'open_spotify') {{
              setTimeout(() => {{
                window.location.href = routing.intent_uri || routing.fallback_url;
              }}, 400);
            }} else if (routing.action === 'open_maps') {{
              setTimeout(() => {{
                window.location.href = routing.intent_uri || routing.fallback_url;
              }}, 400);
            }} else if (routing.action === 'camera') {{
              const fileInput = document.createElement('input');
              fileInput.type = 'file';
              fileInput.accept = 'image/*';
              fileInput.capture = 'camera';
              fileInput.click();
            }} else if (routing.action === 'torch') {{
              detailText.innerText = `[Torch] ${{routing.speech}}`;
            }}
          }} else {{
            target.innerText = '💻 LAPTOP SERVER OFFLOAD';
            target.className = 'text-cyan-400 font-bold';
            badge.className = 'mt-3 py-1.5 px-3 rounded-xl bg-cyan-950/60 border border-cyan-500/60 flex items-center justify-between text-[11px] font-mono transition-all z-20';
            detailText.innerText = data.reply;

            // Play RyanNeural audio if returned
            if (data.audio_url) {{
              const audio = document.getElementById('audioPlayer');
              audio.src = data.audio_url;
              audio.play().catch(() => {{}});
            }}
          }}
        }} else {{
          detailText.innerText = 'Error: ' + data.message;
        }}
      }} catch (err) {{
        detailText.innerText = 'Connection error with laptop: ' + err.message;
      }}
    }}

    function submitChat() {{
      const input = document.getElementById('chatInput');
      const val = input.value.trim();
      if (!val) return;
      document.getElementById('statusText').innerText = `"${{val}}"`;
      sendCommand(val);
      input.value = '';
    }}

    document.getElementById('chatInput').addEventListener('keypress', (e) => {{
      if (e.key === 'Enter') submitChat();
    }});
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


async def start_mobile_satellite_server(port: int = 8765) -> str:
    """Launches the ULTRON Mobile Satellite Host Server in a separate window and returns connection info."""
    import sys
    import subprocess
    ip = get_local_ip()
    url = f"http://{ip}:{port}"
    cmd = [sys.executable, "-m", "friday_tools.satellite_server"]
    try:
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
        return f"ULTRON Mobile Satellite Server launched successfully at {url}. Open this URL on your phone or install ULTRON_Satellite.apk."
    except Exception as e:
        return f"Error launching satellite server: {e}"


def start_server(host: str = "0.0.0.0", port: int = 8765):
    """Starts the FastAPI Satellite Host Server."""
    print_server_banner(port)
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    start_server()
