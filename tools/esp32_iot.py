"""
ULTRON ESP32 & IoT Hardware Intelligence Engine
Provides comprehensive USB Serial, Wi-Fi HTTP, WebSocket, and MQTT integration for ESP32, NodeMCU, and Arduino.
Supports direct one-click firmware compiling & uploading, MicroPython script injection, GPIO control,
sensor telemetry, firmware flashing (esptool/arduino-cli), ESP32-CAM vision analysis, and AI firmware generation.
"""

import os
import sys
import time
import json
import asyncio
import tempfile
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List

ARDUINO_CLI_PATH = Path.home() / "Documents" / "ULTRON_Data" / "bin" / "arduino-cli.exe"


# ── Auto-Fix Missing #include Headers ──────────────────────────────────
# Maps type/function usage patterns to required headers.
_INCLUDE_FIX_MAP = [
    # (search_pattern, required_include, must_not_already_have)
    ("File ",           '#include <FS.h>',           "FS.h"),
    ("File ",           '#include <SPIFFS.h>',       "SPIFFS.h"),
    ("SPIFFS.",         '#include <SPIFFS.h>',       "SPIFFS.h"),
    ("SPIFFS.",         '#include <FS.h>',           "FS.h"),
    ("SD.",             '#include <SD.h>',           "SD.h"),
    ("SD.",             '#include <FS.h>',           "FS.h"),
    ("WiFi.",           '#include <WiFi.h>',         "WiFi.h"),
    ("WiFi.begin",      '#include <WiFi.h>',         "WiFi.h"),
    ("WebServer ",      '#include <WebServer.h>',    "WebServer.h"),
    ("HTTPClient",      '#include <HTTPClient.h>',   "HTTPClient.h"),
    ("http.",           '#include <HTTPClient.h>',   "HTTPClient.h"),
    ("esp_camera",      '#include "esp_camera.h"',   "esp_camera"),
    ("camera_config",   '#include "esp_camera.h"',   "esp_camera"),
    ("Preferences ",    '#include <Preferences.h>',  "Preferences.h"),
    ("EEPROM.",         '#include <EEPROM.h>',       "EEPROM.h"),
    ("MDNS.",           '#include <ESPmDNS.h>',      "ESPmDNS.h"),
    ("ArduinoOTA",      '#include <ArduinoOTA.h>',   "ArduinoOTA.h"),
    ("esp_wifi_",       '#include "esp_wifi.h"',     "esp_wifi"),
    ("WiFiClient ",     '#include <WiFi.h>',         "WiFi.h"),
    ("WiFiServer ",     '#include <WiFi.h>',         "WiFi.h"),
    ("WiFiUDP ",        '#include <WiFiUdp.h>',      "WiFiUdp.h"),
    ("AsyncWebServer",  '#include <ESPAsyncWebServer.h>', "ESPAsyncWebServer.h"),
    ("NTPClient",       '#include <NTPClient.h>',    "NTPClient.h"),
    ("Wire.",           '#include <Wire.h>',         "Wire.h"),
    ("SPI.",            '#include <SPI.h>',          "SPI.h"),
    ("Servo ",          '#include <ESP32Servo.h>',   "Servo"),
    ("Serial.",         None,                        None),  # always available, skip
    ("pcap",            '#include <FS.h>',           "FS.h"),
    ("pcap",            '#include <SPIFFS.h>',       "SPIFFS.h"),
]

def _auto_fix_includes(code: str) -> str:
    """Scans generated code for known types/functions and injects any missing #include headers."""
    if not code or "void setup" not in code:
        return code
    
    inject = []
    for pattern, header, check_key in _INCLUDE_FIX_MAP:
        if header is None or check_key is None:
            continue
        if pattern in code and check_key not in code.split("void setup")[0]:
            if header not in inject:
                inject.append(header)
    
    if not inject:
        return code
    
    # Insert missing includes right after the last existing #include line
    lines = code.splitlines()
    last_include_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("#include"):
            last_include_idx = i
    
    if last_include_idx >= 0:
        for j, hdr in enumerate(inject):
            lines.insert(last_include_idx + 1 + j, hdr)
    else:
        # No includes at all — prepend them
        lines = inject + [""] + lines
    
    return "\n".join(lines)

# ── Serial Port Scanning & Auto-Detection ─────────────────────────────
def _list_serial_ports() -> List[Dict[str, str]]:
    """Lists all available serial / COM ports with hardware descriptions."""
    ports_info = []
    try:
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            desc = p.description or ""
            is_esp = any(k in desc.lower() or k in (p.manufacturer or "").lower() 
                         for k in ["ch340", "cp210", "ftdi", "silicon labs", "esp", "usb-serial", "uart", "arduino"])
            ports_info.append({
                "port": p.device,
                "description": desc,
                "hwid": p.hwid or "",
                "is_esp_candidate": is_esp
            })
    except Exception as e:
        ports_info.append({"port": "N/A", "description": f"Error scanning ports: {e}", "is_esp_candidate": False})
    return ports_info


def _detect_best_port(port: str = "auto") -> Optional[str]:
    """Auto-detects the connected ESP32 / Arduino COM port if 'auto' is specified."""
    clean = port.strip().upper()
    if clean and clean != "AUTO":
        return clean if clean.startswith("COM") else f"COM{clean}"
    
    ports = _list_serial_ports()
    # 1. Look for ESP32 / UART candidate first
    for p in ports:
        if p["is_esp_candidate"] and p["port"] != "N/A":
            return p["port"]
    # 2. Look for any valid COM port
    for p in ports:
        if p["port"] != "N/A" and p["port"].startswith("COM"):
            return p["port"]
    return None


# ── Tool 1: Scan & Detect ESP32 / IoT Devices ─────────────────────────
async def esp32_scan_devices() -> str:
    """
    Scans for connected ESP32, NodeMCU, Arduino, and USB-to-UART microcontroller devices on COM ports.
    """
    try:
        ports = _list_serial_ports()
        if not ports or (len(ports) == 1 and ports[0]["port"] == "N/A"):
            return "[INFO] No USB serial COM ports detected. Check USB cable connection."

        lines = ["[ESP32 / IOT DEVICE SCANNER]", ""]
        esp_found = []
        other_found = []

        for p in ports:
            tag = "⭐ [ESP32 / Microcontroller Candidate]" if p["is_esp_candidate"] else "[Serial Port]"
            entry = f"• {p['port']}: {p['description']} ({tag})"
            if p["is_esp_candidate"]:
                esp_found.append(entry)
            else:
                other_found.append(entry)

        if esp_found:
            lines.append("Detected Microcontrollers:")
            lines.extend(esp_found)
        if other_found:
            lines.append("\nOther COM Devices:")
            lines.extend(other_found)

        return "\n".join(lines)
    except Exception as e:
        return f"[ERROR] Failed to scan ESP32 devices: {e}"


# ── Tool 2: Send Command / Data over Serial or HTTP ────────────────────
async def esp32_send_command(target: str, command: str, baudrate: int = 115200, timeout: float = 3.0) -> str:
    """
    Sends a command or payload to an ESP32 via USB Serial COM port (e.g. 'COM3') or local network IP (e.g. '192.168.1.100').
    """
    try:
        target = target.strip()
        cmd = command.strip()

        # Network HTTP Request (if IP or URL provided)
        if target.startswith("http://") or target.startswith("https://") or ("." in target and not target.upper().startswith("COM")):
            url = target if target.startswith("http") else f"http://{target}"
            if not url.endswith("/") and not any(k in url for k in ["?", "api", "cmd", "control"]):
                url = f"{url}/control?cmd={urllib.parse.quote(cmd)}"
            
            req = urllib.request.Request(url, headers={"User-Agent": "ULTRON-IoT-Engine/2.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                return f"[OK] HTTP Request to ESP32 [{target}] succeeded:\n{body[:400]}"

        # USB Serial Port Communication
        import serial
        port = _detect_best_port(target)
        if not port:
            return f"[ERROR] Target port '{target}' could not be resolved or no device is connected."
        
        with serial.Serial(port, baudrate=baudrate, timeout=timeout) as ser:
            time.sleep(0.1)
            ser.write((cmd + "\n").encode("utf-8"))
            time.sleep(0.2)
            
            response_bytes = ser.read_all()
            reply = response_bytes.decode("utf-8", errors="replace").strip()
            return f"[OK] Serial Command sent to [{port}] @ {baudrate} baud.\nResponse from ESP32:\n{reply or '(No echo received)'}"
    except Exception as e:
        return f"[ERROR] Failed to send command to ESP32 [{target}]: {e}"


# ── Tool 3: Control GPIO Pins (Relays, LEDs, Servos, Buzzers) ─────────
async def esp32_control_gpio(target: str, pin: int, state: str) -> str:
    """
    Controls an ESP32 GPIO pin (e.g. Pin 2 for builtin LED, Pin 4 for Relay, Pin 18 for Servo).
    'state': 'ON', 'OFF', 'HIGH', 'LOW', 'TOGGLE', or PWM integer value '0-255'.
    """
    try:
        clean_state = state.strip().upper()
        cmd = f"GPIO:{pin}:{clean_state}"
        return await esp32_send_command(target, cmd)
    except Exception as e:
        return f"[ERROR] Failed to control GPIO pin {pin}: {e}"


# ── Tool 4: Read Sensor Telemetry ─────────────────────────────────────
async def esp32_read_sensor_data(target: str, sensor_type: str = "all") -> str:
    """
    Queries an ESP32 for sensor readings (DHT11/DHT22 temp/humidity, ultrasonic distance, PIR motion, LDR light, MPU6050 gyro).
    """
    try:
        cmd = f"GET_SENSOR:{sensor_type.upper()}"
        return await esp32_send_command(target, cmd)
    except Exception as e:
        return f"[ERROR] Failed to read sensor data from [{target}]: {e}"


# ── Tool 5: Flash ESP32 Firmware Binary (.bin) via esptool ────────────
async def esp32_flash_firmware(port: str = "auto", binary_path: str = "", baudrate: int = 460800, chip: str = "esp32") -> str:
    """
    Flashes a compiled firmware binary (.bin file) to an ESP32 microcontroller using esptool.
    """
    try:
        if not binary_path or not os.path.exists(binary_path):
            return f"[ERROR] Firmware binary file not found at path: '{binary_path}'"

        target_port = _detect_best_port(port)
        if not target_port:
            return "[ERROR] No connected ESP32 COM port detected. Please specify port or plug in device."

        cmd = [
            "C:\\Users\\shiva\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
            "-m", "esptool",
            "--chip", chip.lower(),
            "--port", target_port,
            "--baud", str(baudrate),
            "write_flash", "-z", "0x10000", binary_path
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode == 0:
            return f"[OK] ESP32 Firmware successfully flashed to {target_port}!\n\nOutput:\n{proc.stdout[-400:]}"
        else:
            return f"[ERROR] esptool flashing failed (Code {proc.returncode}):\n{proc.stderr or proc.stdout}"
    except Exception as e:
        return f"[ERROR] Error executing firmware flash: {e}"


# ── Tool 6: DIRECT One-Click Firmware Upload (Code or Natural Language) ─
async def esp32_direct_upload(code_or_prompt: str, port: str = "auto", wifi_ssid: str = "", wifi_password: str = "", board_type: str = "esp32") -> str:
    """
    DIRECTLY compiles and uploads firmware/code to an ESP32 in one step.
    Accepts:
    1. A compiled .bin file path.
    2. Raw Arduino C++ code (void setup, void loop).
    3. Python / MicroPython code.
    4. A natural language prompt (e.g. 'Turn on relay on pin 4 when button on pin 5 is pressed and create a web server').
    """
    try:
        content = code_or_prompt.strip()
        target_port = _detect_best_port(port)

        # 1. If content is an existing .bin file, flash directly via esptool
        if content.lower().endswith(".bin") and os.path.exists(content):
            return await esp32_flash_firmware(port=target_port or "auto", binary_path=content)

        # 2. If content is MicroPython code
        if ("import machine" in content or "from machine import" in content or "import network" in content) and "void setup" not in content:
            return await esp32_upload_micropython(script_code=content, port=target_port or "auto", filename="main.py")

        # 3. If natural language description, generate production C++ code with AI first
        if "void setup" not in content and "#include" not in content and len(content.splitlines()) < 4:
            from friday_tools.homework_solver import _ai_text
            gen_prompt = (
                f"You are an expert embedded systems engineer for ESP32 and Arduino.\n"
                f"Write complete, production-ready Arduino C++ code that COMPILES WITHOUT ERRORS for:\n"
                f"Requirement: {content}\n"
                f"Wi-Fi SSID: {wifi_ssid or 'Home_WiFi'}\n"
                f"Wi-Fi Password: {wifi_password or '12345678'}\n\n"
                f"CRITICAL RULES:\n"
                f"1. Include ALL necessary #include headers at the top. Every type you use MUST have its header included.\n"
                f"2. Common headers you MUST include when using their features:\n"
                f"   - File type -> #include <FS.h> and #include <SPIFFS.h> or #include <SD.h>\n"
                f"   - WiFi -> #include <WiFi.h>\n"
                f"   - WebServer -> #include <WebServer.h>\n"
                f"   - HTTPClient -> #include <HTTPClient.h>\n"
                f"   - ArduinoJson -> #include <ArduinoJson.h>\n"
                f"   - ESP32 camera -> #include \"esp_camera.h\"\n"
                f"   - Preferences -> #include <Preferences.h>\n"
                f"   - EEPROM -> #include <EEPROM.h>\n"
                f"   - mDNS -> #include <ESPmDNS.h>\n"
                f"   - OTA -> #include <ArduinoOTA.h>\n"
                f"   - esp_wifi -> #include \"esp_wifi.h\"\n"
                f"3. The code MUST have void setup() and void loop().\n"
                f"4. Do NOT use libraries that require separate installation unless absolutely necessary.\n"
                f"   Prefer built-in ESP32 Arduino core libraries.\n"
                f"5. Return ONLY valid C++ code. No markdown, no explanations, no ```.\n"
            )
            raw_code = await _ai_text(gen_prompt)
            # Strip markdown code blocks
            lines = raw_code.splitlines()
            code_lines = [l for l in lines if not l.startswith("```")]
            content = "\n".join(code_lines).strip()

        # Auto-fix: inject missing #include headers based on types/functions used in code
        content = _auto_fix_includes(content)

        if not target_port:
            return (
                f"[CODE GENERATED — Ready for Upload]\n"
                f"No connected ESP32 port detected. Plug in your ESP32 over USB and re-run.\n\n"
                f"Generated Code:\n{content[:500]}..."
            )

        # 4. Compile and Upload using Arduino-CLI
        cli_exe = str(ARDUINO_CLI_PATH)
        if os.path.exists(cli_exe):
            sketch_dir = tempfile.mkdtemp(prefix="ultron_esp32_")
            sketch_name = os.path.basename(sketch_dir)
            sketch_file = os.path.join(sketch_dir, f"{sketch_name}.ino")
            
            with open(sketch_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Compile & Upload (High Speed Multi-Core Compile + 921600 Upload Baud)
            fqbn = "esp32:esp32:esp32" if "esp32" in board_type.lower() else "arduino:avr:uno"
            compile_cmd = [
                cli_exe, "compile",
                "--fqbn", fqbn,
                "-j", "0",
                "-e",
                sketch_dir
            ]
            upload_cmd = [
                cli_exe, "upload",
                "-p", target_port,
                "--fqbn", fqbn,
                "--upload-property", "upload.speed=921600",
                sketch_dir
            ]

            # Run compile with parallel worker threads
            c_proc = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=45)
            if c_proc.returncode == 0:
                # Run fast upload (typically 5-10 seconds at 921600 baud)
                u_proc = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=30)
                if u_proc.returncode == 0:
                    return f"[DIRECT UPLOAD SUCCESS] Firmware compiled and uploaded to ESP32 on {target_port} in seconds!\n\nBoard is now running your firmware."
                else:
                    # Fallback to standard upload if speed property is unsupported
                    fallback_upload = [cli_exe, "upload", "-p", target_port, "--fqbn", fqbn, sketch_dir]
                    u2_proc = subprocess.run(fallback_upload, capture_output=True, text=True, timeout=30)
                    if u2_proc.returncode == 0:
                        return f"[DIRECT UPLOAD SUCCESS] Firmware compiled and uploaded to ESP32 on {target_port}!\n\nBoard is now running your firmware."
                    return f"[COMPILE OK — UPLOAD FAILED on {target_port}]:\n{u_proc.stderr or u_proc.stdout}"
            else:
                return (
                    f"[COMPILATION ERROR]\n"
                    f"Target Port: {target_port}\n"
                    f"Errors:\n{c_proc.stderr or c_proc.stdout}\n\n"
                    f"Saved Sketch: {sketch_file}"
                )



        # Fallback if CLI not found
        return f"[FIRMWARE READY] Generated complete code for {target_port}:\n\n{content[:600]}..."
    except Exception as e:
        return f"[ERROR] Direct firmware upload failed: {e}"


# ── Tool 7: Direct MicroPython Upload via ampy ────────────────────────
async def esp32_upload_micropython(script_code: str, port: str = "auto", filename: str = "main.py") -> str:
    """
    Directly uploads a Python/MicroPython script to an ESP32 or Raspberry Pi Pico filesystem (e.g. main.py) via serial.
    """
    try:
        target_port = _detect_best_port(port)
        if not target_port:
            return "[ERROR] No connected ESP32 COM port detected. Please connect device."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp_f:
            temp_f.write(script_code)
            temp_path = temp_f.name

        try:
            # Use ampy to push file directly over serial (-b 115200 for reliable transfer)
            cmd = [
                "C:\\Users\\shiva\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
                "-m", "ampy.cli",
                "-p", target_port,
                "-b", "115200",
                "put", temp_path, filename
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if proc.returncode == 0:
                return f"[OK] MicroPython script '{filename}' directly uploaded to ESP32 on {target_port}!"
            else:
                return f"[NOTICE] ampy upload to {target_port} output: {proc.stderr or proc.stdout}"
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass
    except Exception as e:
        return f"[ERROR] Failed to upload MicroPython script: {e}"


# ── Tool 8: ESP32-CAM AI Vision Stream Inspection ─────────────────────
async def esp32_camera_analyze(camera_ip: str, question: str = "Describe what you see in front of the ESP32 camera.") -> str:
    """
    Captures a frame from an ESP32-CAM video stream (e.g. '192.168.1.150') and analyzes it using Gemini AI Vision.
    """
    try:
        url = camera_ip.strip()
        if not url.startswith("http"):
            url = f"http://{url}"
        
        snapshot_url = f"{url}/capture" if not url.endswith("/capture") and not url.endswith(".jpg") else url
        
        req = urllib.request.Request(snapshot_url, headers={"User-Agent": "ULTRON-Vision-Core"})
        with urllib.request.urlopen(req, timeout=5.0) as response:
            frame_bytes = response.read()

        if not frame_bytes or len(frame_bytes) < 100:
            return f"[ERROR] Empty or invalid image received from ESP32-CAM at {camera_ip}."

        from aria_modules.vision_core import analyze_image_fast
        prompt = f"You are analyzing a live frame from an ESP32-CAM microcontroller. {question}"
        analysis = analyze_image_fast(frame_bytes, prompt)
        return f"[ESP32-CAM Live Vision Analysis]\n{analysis}"
    except Exception as e:
        return f"[ERROR] Failed to capture and analyze ESP32-CAM stream: {e}"


# ── Tool 9: AI Firmware Code Generator ─────────────────────────────────
async def esp32_generate_firmware_code(project_description: str, wifi_ssid: str = "YOUR_WIFI_SSID", wifi_password: str = "YOUR_WIFI_PASSWORD") -> str:
    """
    Generates complete, production-ready Arduino C++ or MicroPython firmware code for ESP32 with WebServer, REST API endpoints, and GPIO handlers.
    """
    try:
        prompt = (
            f"You are an expert embedded systems engineer for ESP32 and Arduino.\n"
            f"Write complete, production-ready, compiling Arduino C++ code for the following project requirements:\n\n"
            f"Project: {project_description}\n"
            f"Wi-Fi SSID: {wifi_ssid}\n"
            f"Wi-Fi Password: {wifi_password}\n\n"
            f"Include:\n"
            f"1. Pin definitions and setup.\n"
            f"2. WiFi connection logic with status LED.\n"
            f"3. ESPAsyncWebServer or WebServer endpoints to handle REST API commands (/control, /sensor, /status).\n"
            f"4. Serial command parser at 115200 baud for USB communication.\n"
            f"5. Clear comments explaining how to upload via Arduino IDE / PlatformIO.\n"
            f"Return ONLY valid, complete C++ code ready to upload."
        )

        from friday_tools.homework_solver import _ai_text
        code = await _ai_text(prompt)
        return code
    except Exception as e:
        return f"[ERROR] Failed to generate firmware code: {e}"
