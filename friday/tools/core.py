import os
import json
import subprocess
import logging
import time
import platform
import requests
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
import psutil

# ==============================
# DATA FILES
# ==============================
DATA_DIR = os.path.expanduser(os.path.join("~", "Documents", "ULTRON_Data"))
os.makedirs(DATA_DIR, exist_ok=True)
APP_LOG_FILE = os.path.join(DATA_DIR, "app_usage_log.json")
MEMORY_FILE = os.path.join(DATA_DIR, "ultron_memory.json")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")

# ==============================
# APP TRACKING
# ==============================
def _load_app_log():
    if os.path.exists(APP_LOG_FILE):
        with open(APP_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_app_log(data):
    os.makedirs(os.path.dirname(APP_LOG_FILE), exist_ok=True)
    with open(APP_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

async def track_active_application() -> str:
    import win32gui
    import win32process
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        app = psutil.Process(pid).name()

        log = _load_app_log()
        today = datetime.today().date().isoformat()
        log.setdefault(today, {})
        log[today][app] = log[today].get(app, 0) + 1
        _save_app_log(log)
        return f"Tracked usage for {app}"
    except Exception as e:
        return f"Tracking failed: {e}"

async def weekly_app_usage_report() -> str:
    log = _load_app_log()
    cutoff = datetime.today().date() - timedelta(days=7)
    summary = defaultdict(int)

    for day, apps in log.items():
        if datetime.fromisoformat(day).date() >= cutoff:
            for app, mins in apps.items():
                summary[app] += mins

    if not summary:
        return "No usage data available."

    report = ["📊 Weekly Application Usage:"]
    for app, mins in sorted(summary.items(), key=lambda x: -x[1]):
        report.append(f"{app}: {mins} min")
    return "\n".join(report)

# ==============================
# MEMORY (ultron_memory.json = ULTRON's Brain)
# ==============================
import friday_tools.ultron_memory as _um

def load_memory():
    return _um._load_memory_json()

def save_memory(data):
    _um._save_memory_json(data)
    _um._update_memory_md(data)

# --- TOOL: Remember (save a fact or note) ---
async def remember(key: str = "", value: str = "", text: str = "", content: str = "") -> str:
    """Saves a fact, note, or memory to ULTRON's brain (ultron_memory.json & Ultron_Memory.md)."""
    if key and value:
        return _um.save_fact(key, value)
    msg = text or content or key or value or ""
    return _um.remember(msg)

# --- TOOL: Recall (retrieve a fact) ---
async def recall(key: str = "", query: str = "") -> str:
    """Recalls a specific piece of knowledge or searches memories in ultron_memory.json."""
    q = query or key or ""
    return _um.recall(q)

# --- TOOL: Forget (delete a specific memory) ---
async def forget(key: str = "") -> str:
    """Removes a specific fact from ULTRON's memory across all storage files."""
    return _um.forget(key)

# --- TOOL: Update memory (modify existing) ---
async def update_memory(key: str, new_value: str = "", value: str = "") -> str:
    """Updates an existing memory in ultron_memory.json. If it doesn't exist, creates it."""
    val = new_value or value or ""
    return _um.update_memory(key, val)

# --- TOOL: View full brain ---
async def view_brain() -> str:
    """Shows all of ULTRON's memories from ultron_memory.json (both facts and event logs)."""
    mem = load_memory()
    result = ["🧠 ULTRON BRAIN DUMP (ultron_memory.json)\n"]
    
    # Facts
    facts = mem.get("facts", {})
    if facts:
        result.append(f"📌 FACTS ({len(facts)} stored):")
        for k, v in facts.items():
            result.append(f"  • {k}: {v}")
    else:
        result.append("📌 FACTS: (empty)")
    
    # Logs
    logs = mem.get("logs", [])
    if logs:
        result.append(f"\n📝 EVENT LOGS ({len(logs)} entries, showing last 15):")
        for entry in logs[-15:]:
            ts = entry.get("timestamp", "?")[:16]
            content = entry.get("content", "")
            result.append(f"  [{ts}] {content}")
    else:
        result.append("\n📝 EVENT LOGS: (empty)")
    
    return "\n".join(result)

# --- TOOL: Delete a log entry ---
async def delete_log(search_text: str) -> str:
    """Removes a specific log entry from ultron_memory.json by matching its content."""
    mem = load_memory()
    original_count = len(mem.get("logs", []))
    mem["logs"] = [e for e in mem.get("logs", []) if search_text.lower() not in e.get("content", "").lower()]
    removed = original_count - len(mem["logs"])
    save_memory(mem)
    if removed > 0:
        return f"✅ Removed {removed} log(s) matching '{search_text}'."
    return f"❌ No logs found matching '{search_text}'."

# --- TOOL: Delete an upcoming event ---
async def delete_upcoming_event(event_name: str) -> str:
    """Permanently deletes an upcoming event or competition from all schedules and memory."""
    try:
        from friday_tools.briefing import delete_upcoming_event as b_delete
        return await b_delete(event_name)
    except Exception as e:
        return f"❌ Failed to delete event: {e}"

async def delete_event(event_name: str) -> str:
    """Permanently deletes an upcoming event or competition."""
    return await delete_upcoming_event(event_name)


# --- TOOL: Clear old logs ---
async def clear_old_logs(days_old: int = 30) -> str:
    """Removes log entries older than the specified number of days from ultron_memory.json."""
    mem = load_memory()
    cutoff = (datetime.now() - timedelta(days=days_old)).isoformat()
    original_count = len(mem.get("logs", []))
    mem["logs"] = [e for e in mem.get("logs", []) if e.get("timestamp", "") >= cutoff]
    removed = original_count - len(mem["logs"])
    save_memory(mem)
    return f"🧹 Cleaned up {removed} log(s) older than {days_old} days. {len(mem['logs'])} remaining."

# --- Internal: Add to logs ---
async def add_to_logs(content: str = "", text: str = "") -> str:
    """Appends a timestamped memory to the logs in ultron_memory.json."""
    c = content or text or ""
    if not c:
        return "[OK] No content to log."
    mem = load_memory()
    mem.setdefault("logs", []).append({
        "content": c,
        "timestamp": datetime.now().isoformat()
    })
    save_memory(mem)
    return f"[OK] Logged: {c}"

# --- Internal: Search memory ---
async def search_memory(query: str, limit: int = 5) -> str:
    """Searches both KV and logs for relevant information."""
    mem = load_memory()
    results = []
    q = query.lower()
    
    for k, v in mem.get("kv", {}).items():
        if q in k or q in str(v).lower():
            results.append(f"{k}: {v}")
            
    for entry in reversed(mem.get("logs", [])):
        if q in entry.get("content", "").lower():
            results.append(entry.get("content", ""))
        if len(results) >= limit:
            break
    return "\n".join(results) if results else f"No memories found matching '{query}'."

# --- Internal: Smart auto-detect what to remember ---
# These keywords trigger automatic memory storage from user messages
AUTO_REMEMBER_KEYWORDS = {
    # Events - stored as [EVENT] logs
    "events": [
        "meeting", "interview", "appointment", "event", "tomorrow", "next week",
        "next month", "schedule", "going to", "have to", "will be",
        "presentation", "exam", "test", "trip", "travel", "flight", "doctor",
        "dentist", "party", "celebration", "birthday", "anniversary", "deadline",
        "competition", "hackathon", "fest", "conference", "workshop"
    ],
    # Personal facts - stored as kv pairs 
    "facts": [
        "my name is", "i am", "i'm", "my age is", "i live in", "i work at",
        "my favorite", "i like", "i love", "i hate", "i prefer",
        "my phone", "my email", "my address", "my school", "my college",
        "my brother", "my sister", "my friend", "my mom", "my dad",
        "my password is", "my username is", "my id is"
    ],
    # Skills/interests - stored as kv
    "interests": [
        "i play", "i study", "i code in", "i know", "i speak",
        "my hobby", "i enjoy", "i practice"
    ]
}

def auto_detect_and_store(message: str):
    """Automatically detects important info in user messages and stores it in ultron_memory.json."""
    msg_lower = message.lower()
    stored = []
    
    # Check for events
    if any(kw in msg_lower for kw in AUTO_REMEMBER_KEYWORDS["events"]):
        add_to_logs(f"[EVENT] {message}")
        stored.append("event")
    
    # Check for personal facts
    for pattern in AUTO_REMEMBER_KEYWORDS["facts"]:
        if pattern in msg_lower:
            # Extract and store as kv
            # e.g., "my name is Shivansh" → kv["user_name"] = "Shivansh"
            idx = msg_lower.index(pattern)
            value = message[idx + len(pattern):].strip().rstrip(".!?,")
            if value and len(value) < 200:
                key = pattern.replace("my ", "user_").replace("i am", "user_identity").replace("i'm", "user_identity").replace("i ", "user_").replace(" is", "").replace(" ", "_").strip("_")
                mem = load_memory()
                mem["kv"][key] = value
                save_memory(mem)
                stored.append(f"fact:{key}")
            break
    
    # Check for interests
    for pattern in AUTO_REMEMBER_KEYWORDS["interests"]:
        if pattern in msg_lower:
            idx = msg_lower.index(pattern)
            value = message[idx + len(pattern):].strip().rstrip(".!?,")
            if value and len(value) < 200:
                key = pattern.replace("i ", "user_").replace(" ", "_").strip("_")
                mem = load_memory()
                mem["kv"][key] = value
                save_memory(mem)
                stored.append(f"interest:{key}")
            break
    
    return stored


# ==============================
# CONTACTS
# ==============================
def _load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_contacts(contacts):
    os.makedirs(os.path.dirname(CONTACTS_FILE), exist_ok=True)
    with open(CONTACTS_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

async def save_contact(name: str, phone: str, notes: str = "") -> str:
    """Saves a contact with their phone number."""
    try:
        contacts = _load_contacts()
        name_key = name.lower().strip()
        phone_clean = phone.strip().replace("+", "").replace("-", "").replace(" ", "")
        if not phone_clean.isdigit():
            return f"❌ Invalid phone number format. Use digits only (e.g., 919876543210)"
        
        if name_key in contacts:
            old_phone = contacts[name_key]["phone"]
            contacts[name_key] = {
                "name": name, "phone": phone_clean, "notes": notes, 
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            _save_contacts(contacts)
            return f"✅ Updated contact '{name}'\n📱 Old: {old_phone}\n📱 New: {phone_clean}"
        else:
            contacts[name_key] = {
                "name": name, "phone": phone_clean, "notes": notes, 
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            _save_contacts(contacts)
            return f"✅ Saved contact '{name}'\n📱 Phone: {phone_clean}"
    except Exception as e:
        return f"❌ Failed to save contact: {e}"

async def get_contact_phone(name: str) -> str:
    """Retrieves a phone number for a contact by name."""
    try:
        contacts = _load_contacts()
        name_lower = name.lower().strip()
        
        if name_lower in contacts:
            return contacts[name_lower]["phone"]
        
        matches = [c for k, c in contacts.items() if name_lower in k or name_lower in c["name"].lower()]
        
        if len(matches) == 1:
            return matches[0]["phone"]
        elif len(matches) > 1:
            return "Found potential matches:\n" + "\n".join([f"{c['name']}: {c['phone']}" for c in matches])
        else:
            return f"❌ No contact found for '{name}'"
    except Exception as e:
        return f"❌ Failed to retrieve contact: {e}"

async def list_all_contacts() -> str:
    """Lists all saved contacts."""
    try:
        contacts = _load_contacts()
        if not contacts: return "📱 No contacts saved yet."
        
        sorted_contacts = sorted(contacts.values(), key=lambda x: x["name"].lower())
        result = [f"📱 Saved Contacts ({len(contacts)} total):"]
        for i, c in enumerate(sorted_contacts, 1):
            notes_str = f" ({c['notes']})" if c.get("notes") else ""
            result.append(f"{i}. {c['name']}: {c['phone']}{notes_str}")
        return "\n".join(result)
    except Exception as e:
        return f"❌ Failed to list contacts: {e}"

async def delete_contact(name: str) -> str:
    """Deletes a contact."""
    try:
        contacts = _load_contacts()
        name_lower = name.lower().strip()
        if name_lower in contacts:
            del contacts[name_lower]
            _save_contacts(contacts)
            return f"✅ Deleted contact '{name}'"
        return f"❌ Contact '{name}' not found"
    except Exception as e:
        return f"❌ Failed to delete: {e}"

async def search_contacts(query: str) -> str:
    """Searches contacts."""
    try:
        contacts = _load_contacts()
        q = query.lower().strip()
        matches = [c for c in contacts.values() if q in c["name"].lower() or q in c["phone"] or q in c.get("notes", "").lower()]
        if not matches: return f"❌ No matches for '{query}'"
        return "🔍 Matches:\n" + "\n".join([f"{c['name']}: {c['phone']}" for c in matches])
    except Exception as e:
        return f"❌ Search failed: {e}"

# ==============================
# SYSTEM & WEATHER
# ==============================
async def get_weather(city: str) -> str:
    try:
        return requests.get(f"https://wttr.in/{city}?format=3", timeout=5).text
    except:
        return "Weather unavailable"

async def search_web(query: str, max_results: int = 5) -> str:
    """Performs a live real-time web search for any question, topic, flight, price, news, or fact."""
    # Tier 1: Google Real-Time Grounded Search via Gemini
    key = os.getenv("GEMINI_API_KEY")
    if key:
        try:
            for model_name in ["gemini-2.5-flash", "gemini-2.0-flash"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"Search the live web and provide an accurate, clear, up-to-date answer for: '{query}'. Include specific real-world details (like timings, prices, schedule, sources) if applicable."
                        }]
                    }],
                    "tools": [{"googleSearch": {}}]
                }
                r = requests.post(url, json=payload, timeout=12)
                if r.status_code == 200:
                    data = r.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if text:
                            chunks = candidates[0].get("groundingMetadata", {}).get("groundingChunks", [])
                            sources = []
                            for c in chunks[:4]:
                                web = c.get("web", {})
                                if web.get("uri") and web.get("title"):
                                    sources.append(f"• [{web['title']}]({web['uri']})")
                            src_text = ("\n\n**Sources:**\n" + "\n".join(sources)) if sources else ""
                            return f"{text.strip()}{src_text}"
        except Exception:
            pass

    # Tier 2: Bing Scraper Fallback
    try:
        import urllib.parse
        from bs4 import BeautifulSoup
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        b_url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(query)}"
        r = requests.get(b_url, headers=headers, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for li in soup.find_all("li", class_="b_algo")[:max_results]:
                h2 = li.find("h2")
                p = li.find("p") or li.find("div", class_="b_caption")
                a = h2.find("a") if h2 else None
                if h2 and p and a:
                    title = h2.get_text(strip=True)
                    link = a.get("href", "")
                    snippet = p.get_text(strip=True)
                    results.append(f"• **{title}**\n  URL: {link}\n  {snippet}")
            if results:
                return f"🌐 [Live Web Results for '{query}']:\n\n" + "\n\n".join(results)
    except Exception:
        pass

    return f"No live search results found for '{query}'."

async def current_time() -> str:
    return datetime.now().strftime("%H:%M:%S")

async def system_status() -> str:
    return platform.platform()

async def system_uptime() -> str:
    return str(timedelta(seconds=int(time.time() - psutil.boot_time())))

async def battery_status() -> str:
    b = psutil.sensors_battery()
    return f"{b.percent}% {'Charging' if b.power_plugged else 'Not Charging'}"

async def check_internet() -> str:
    import socket
    import http.client as httplib
    
    # Method 1: DNS
    targets = [("8.8.8.8", 53), ("1.1.1.1", 53)]
    for host, port in targets:
        try:
            socket.create_connection((host, port), timeout=2)
            return "✅ Internet Connection: Active (DNS verifying)."
        except: pass
            
    # Method 2: HTTP
    try:
        conn = httplib.HTTPSConnection("www.google.com", timeout=3)
        conn.request("HEAD", "/")
        conn.close()
        return "✅ Internet Connection: Active (HTTP verifying)."
    except: pass
    
    return "⚠️ Limited Connectivity Detected."

async def system_health_report() -> str:
    return f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%"

async def publish_to_sandbox() -> str:
    """Publishes the current application state to the LiveKit sandbox friday-ak3nk6."""
    try:
        # User specified: lk app create \ --sandbox friday-ak3nk6
        cmd = "lk app create --sandbox friday-ak3nk6"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=60)
        
        if process.returncode == 0:
            return f"🚀 Successfully published to sandbox 'friday-ak3nk6'.\nOutput: {stdout.strip()}"
        else:
            return f"❌ Publishing failed.\nError: {stderr.strip()}"
    except Exception as e:
        return f"❌ Sandbox error: {e}"

async def google_custom_search(query: str) -> str:
    """Performs a real-time live Google/Web search."""
    return await search_web(query)

