# Friday / JARVIS Neural OS ⚡

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Status: Operational](https://img.shields.io/badge/Status-Operational-brightgreen.svg)]()
[![Tools: 800+](https://img.shields.io/badge/Active%20Tools-800+-orange.svg)]()

> **Friday / JARVIS Neural OS** is an advanced, autonomous AI desktop assistant and neural operating system equipped with 800+ deterministic tools, multimodal ambient vision, real-time tactical radar, aerospace flight tracking, and autonomous OS-level orchestration.

---

## 🌟 Key Features & Architecture

### 1. 🔮 Quantum Holographic Orb & Tactical HUD
- **Center Holographic Core**: Fluid particle core, nested rotating latitude rings, and multi-layered glow shaders.
- **Multi-Mode Tactical Console**:
  - `🔮 Quantum Orb`: Ambient neural standby state.
  - `🗺️ 2D Live Map`: Tactical live radar map visualizing real global air traffic and orbital passes.
  - `🌍 3D Tactical Globe`: Global projection with interactive camera controls.
  - `🔴 Live Planetary View`: Live optical video telemetry direct from the International Space Station (ISS).
- **HUD Telemetry**: Instant feedback on fleet count, active flight cards, and system status.

### 2. ✈️ Aerospace Flight Radar & Air Traffic Intelligence
- **Global Flight Tracking**: Real-time telemetry monitoring over 11,500+ commercial and transport aircraft worldwide.
- **Dynamic Arrival Estimation**:
  - Geodesic distance and ground-speed transit calculations.
  - Air traffic congestion analysis based on peak inbound sequencing at major international hubs (Delhi, Mumbai, Dubai, London Heathrow, Frankfurt, New York JFK, and more).
  - Accurate runway touchdown estimation down to the minute.
- **Live Space Station Telemetry**: Real-time geodesic tracking of the International Space Station (ISS) with orbital velocity, altitude, and upcoming regional pass predictions.

### 3. 👁️ Ambient Vision & Visual Cortex
- **Proactive Screen Sentinel**: Continuous low-overhead visual perception analyzing active desktop context.
- **Autonomous Computer Use**: Coordinate extraction, UI navigation, automated form interaction, and element clicking.
- **Multimodal Homework & Technical Solver**: Instant step-by-step solutions for complex math equations, engineering problems, and scientific queries via Gemini Vision.

### 4. 🛠️ 800+ Autonomous Tool Subsystem
- **Communication & Social Autopilot**: Full headless WhatsApp engine, intelligent email management (IMAP/SMTP copilot, phishing detection, OTP extraction).
- **System & Security Suite**: Hardware power management, audio/volume matrix, process watchdog, network discovery, and diagnostics.
- **Autonomous Subagents**: Parallel background worker spawning for multi-threaded intelligence tasks, web scraping, and deep research.
- **Productivity & Memory**: Persistent semantic memory with local JSON stores, deterministic alarms, reminders, and background scheduler daemon.

---

## 🚀 Getting Started

### Prerequisites
- **Operating System**: Windows 10 / 11 (x64)
- **Python**: Version 3.11 or higher
- **Hardware Acceleration**: Recommended (for Three.js / WebGL rendering)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Coderbhai777/friday-neural-os.git
   cd friday-neural-os
   ```

2. **Set Up Python Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GMAIL_USER=your_email@gmail.com
   GMAIL_APP_PASSWORD=your_app_password
   ```

4. **Launch Friday / JARVIS**:
   ```bash
   python main.py
   ```

---

## 📁 Repository Structure

```text
friday-neural-os/
├── assets/                  # UI assets and Quantum Orb interface (jarvis_orb.html)
├── friday/                  # Core assistant modules, neural brain, prompts
│   ├── agent.py             # Voice and LiveKit agent orchestration
│   ├── brain.py             # Gemini reasoning engine
│   └── tools/               # 800+ tool modules
│       ├── flight_radar.py  # Aerospace telemetry, arrival estimator, ISS tracking
│       ├── computer_use.py  # Autonomous UI control & coordinate extraction
│       ├── email_copilot.py # IMAP/SMTP automation & phishing guard
│       └── ...
├── tools/                   # Synced tools directory
├── main.py                  # Primary runtime launcher
├── setup.py                 # Package setup and build configuration
└── requirements.txt         # Core dependencies
```

---

## 🔒 Security & Privacy

- All API credentials, tokens, and personal communication data are strictly excluded from git tracking via `.gitignore`.
- Local memory files and application logs remain exclusively on your local device.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
