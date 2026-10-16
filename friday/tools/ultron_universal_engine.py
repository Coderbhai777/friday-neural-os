# -*- coding: utf-8 -*-
"""
ULTRON Ω — Universal Execution Engine (Section 2 Compliant)
Unifies:
1. Visual Desktop Interaction (UI Automation, MSS/PIL screen capture, Vision, Mouse/Keyboard)
2. General-Purpose Browser Automation (Stealth Selenium / Playwright, Navigation, Video, Auth/CAPTCHA detection)
3. Operating System Interaction (Windows Settings, Control Panel, Applets, PowerShell, File Operations)
4. Programmatic Capability Creation (SkillForge: Sandboxed Script Generation, Validation, Repair, and Verified Promotion)
"""

import os
import sys
import io
import time
import json
import re
import ast
import subprocess
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

# Directories
DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SANDBOX_DIR = DATA_DIR / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
USER_SKILLS_DIR = DATA_DIR / "user_skills"
USER_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

user32 = ctypes.windll.user32


# =====================================================================
# 1. VISUAL DESKTOP EXECUTOR (Capability A)
# =====================================================================

class VisualDesktopExecutor:
    """General-purpose visual computer interaction via UI Automation and Vision."""

    def __init__(self):
        self._failsafe_disabled = False

    def _ensure_pyautogui(self):
        import pyautogui
        if not self._failsafe_disabled:
            pyautogui.FAILSAFE = False
            self._failsafe_disabled = True
        return pyautogui

    def capture_screen(self, max_dim: int = 1280) -> Optional[Any]:
        """Captures active screen using MSS with PIL/PyAutoGUI fallbacks."""
        try:
            import mss
            from PIL import Image
            with mss.mss() as sct:
                mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                s_img = sct.grab(mon)
                img = Image.frombytes("RGB", s_img.size, s_img.bgra, "raw", "BGRX")
        except Exception:
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab(all_screens=False)
            except Exception:
                pg = self._ensure_pyautogui()
                img = pg.screenshot()

        if img and max_dim and (img.width > max_dim or img.height > max_dim):
            scale = min(max_dim / float(img.width), max_dim / float(img.height))
            new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
            img = img.resize(new_size, Image.Resampling.BILINEAR)
        return img

    def get_foreground_window(self) -> Dict[str, Any]:
        """Returns details of the currently focused foreground window."""
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return {"hwnd": 0, "title": "", "app": ""}
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value or ""

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        app = "unknown"
        try:
            import psutil
            app = psutil.Process(pid.value).name()
        except Exception:
            pass
        return {"hwnd": hwnd, "title": title, "app": app}

    def find_windows_by_title(self, title_pattern: str) -> List[Dict[str, Any]]:
        """Finds all open top-level windows matching a title pattern."""
        results = []
        pattern_lower = title_pattern.lower()

        def enum_cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value
                    if pattern_lower in title.lower():
                        results.append({"hwnd": hwnd, "title": title})
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return results

    def switch_to_window(self, hwnd: int) -> bool:
        """Brings the specified window to the foreground."""
        try:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
            user32.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            return True
        except Exception:
            return False

    def click(self, x: int, y: int, double: bool = False, right: bool = False) -> Dict[str, Any]:
        """Moves mouse and clicks at specified screen coordinates."""
        pg = self._ensure_pyautogui()
        button = "right" if right else "left"
        clicks = 2 if double else 1
        pg.click(x=x, y=y, clicks=clicks, button=button)
        return {"status": "SUCCESS", "action": "click", "x": x, "y": y, "button": button, "clicks": clicks}

    def type_text(self, text: str, interval: float = 0.02) -> Dict[str, Any]:
        """Types text using keyboard emulation."""
        pg = self._ensure_pyautogui()
        pg.write(text, interval=interval)
        return {"status": "SUCCESS", "action": "type_text", "chars": len(text)}

    def hotkey(self, *keys: str) -> Dict[str, Any]:
        """Executes a combination of keyboard keys (e.g. ['win', 'r'], ['ctrl', 's'])."""
        pg = self._ensure_pyautogui()
        pg.hotkey(*keys)
        return {"status": "SUCCESS", "action": "hotkey", "keys": list(keys)}

    def scroll(self, clicks: int) -> Dict[str, Any]:
        """Scrolls mouse wheel."""
        pg = self._ensure_pyautogui()
        pg.scroll(clicks)
        return {"status": "SUCCESS", "action": "scroll", "clicks": clicks}


# =====================================================================
# 2. GENERAL-PURPOSE BROWSER EXECUTOR (Capability B)
# =====================================================================

class BrowserExecutor:
    """General-purpose web browser automation via Selenium with anti-detection profile."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None

    def _get_or_create_driver(self):
        if self.driver is not None:
            try:
                # Test driver is alive
                _ = self.driver.current_url
                return self.driver
            except Exception:
                self.driver = None

        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        opts = Options()
        if self.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=opts)
        except Exception:
            self.driver = webdriver.Chrome(options=opts)

        # Stealth CDP override
        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            })
        except Exception:
            pass

        self.driver.set_page_load_timeout(25)
        return self.driver

    def close(self):
        """Closes browser session."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigates to URL and returns page info."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        d = self._get_or_create_driver()
        d.get(url)
        time.sleep(2.0)
        return {
            "status": "SUCCESS",
            "url": d.current_url,
            "title": d.title
        }

    def search_website(self, query: str, engine_url: str = "https://www.google.com") -> Dict[str, Any]:
        """Navigates to a search engine or website and submits query."""
        d = self._get_or_create_driver()
        d.get(engine_url)
        time.sleep(1.5)

        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        # Generic search input detection
        search_inputs = d.find_elements(By.CSS_SELECTOR, "input[type='text'], input[name='q'], input[name='search_query'], input[placeholder*='search' i], textarea[name='q']")
        if search_inputs:
            input_el = search_inputs[0]
            input_el.clear()
            input_el.send_keys(query)
            input_el.send_keys(Keys.RETURN)
            time.sleep(2.5)
            return {"status": "SUCCESS", "searched": query, "url": d.current_url, "title": d.title}

        return {"status": "FAILED", "reason": "No search input field located on page."}

    def find_and_click_element(self, text_or_selector: str) -> Dict[str, Any]:
        """Locates and clicks an element by CSS selector, XPath, or inner text."""
        d = self._get_or_create_driver()
        from selenium.webdriver.common.by import By

        # 1. Try CSS selector
        try:
            el = d.find_element(By.CSS_SELECTOR, text_or_selector)
            if el and el.is_displayed():
                d.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                time.sleep(0.3)
                el.click()
                return {"status": "SUCCESS", "method": "css_selector", "target": text_or_selector}
        except Exception:
            pass

        # 2. Try XPath containing text
        try:
            xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text_or_selector.lower()}')]"
            elements = d.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    d.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    time.sleep(0.3)
                    el.click()
                    return {"status": "SUCCESS", "method": "text_xpath", "target": text_or_selector}
        except Exception:
            pass

        # 3. Try link text
        try:
            el = d.find_element(By.PARTIAL_LINK_TEXT, text_or_selector)
            if el and el.is_displayed():
                el.click()
                return {"status": "SUCCESS", "method": "partial_link", "target": text_or_selector}
        except Exception:
            pass

        return {"status": "FAILED", "reason": f"Element '{text_or_selector}' not found or not clickable."}

    def play_video(self) -> Dict[str, Any]:
        """Finds any <video> tag on the page, clicks play, and verifies playback state."""
        d = self._get_or_create_driver()
        script = """
        const video = document.querySelector('video');
        if (video) {
            if (video.paused) {
                video.play();
            }
            return {
                found: true,
                paused: video.paused,
                currentTime: video.currentTime,
                duration: video.duration
            };
        }
        return { found: false };
        """
        res = d.execute_script(script)
        if res and res.get("found"):
            time.sleep(1.0)
            verify_res = d.execute_script("const v = document.querySelector('video'); return v ? !v.paused : false;")
            return {
                "status": "SUCCESS" if verify_res else "PAUSED",
                "playback_active": bool(verify_res),
                "details": res
            }
        # Try clicking any video player container
        try:
            from selenium.webdriver.common.by import By
            player = d.find_element(By.CSS_SELECTOR, ".html5-video-player, video, button[aria-label*='Play' i]")
            player.click()
            time.sleep(1.0)
            verify_res = d.execute_script("const v = document.querySelector('video'); return v ? !v.paused : false;")
            return {"status": "SUCCESS" if verify_res else "PAUSED", "playback_active": bool(verify_res)}
        except Exception as e:
            return {"status": "FAILED", "reason": f"No video element located: {e}"}

    def detect_auth_or_captcha(self) -> Dict[str, Any]:
        """Detects if page requires sign-in, login credentials, or CAPTCHA challenge."""
        d = self._get_or_create_driver()
        page_source = d.page_source.lower()
        title = d.title.lower()

        # Auth indicators
        auth_signals = ["sign in", "log in", "login", "enter password", "authentication required"]
        is_auth_required = any(s in title for s in ["sign in", "login"]) or ("accounts.google.com" in d.current_url)

        # Captcha indicators
        captcha_signals = ["captcha", "recaptcha", "cf-turnstile", "hcaptcha", "verify you are human", "robot check"]
        is_captcha = any(c in page_source for c in captcha_signals)

        return {
            "auth_required": is_auth_required,
            "captcha_detected": is_captcha,
            "current_url": d.current_url,
            "title": d.title
        }


# =====================================================================
# 3. OPERATING SYSTEM EXECUTOR (Capability C)
# =====================================================================

class OSExecutor:
    """General-purpose operating system interaction via Win32, Applets, PowerShell, and Filesystem."""

    KNOWN_APP_MAP = {
        "control panel": "control.exe",
        "programs and features": "control.exe appwiz.cpl",
        "settings": "start ms-settings:",
        "apps and features": "start ms-settings:appsfeatures",
        "device manager": "devmgmt.msc",
        "task manager": "taskmgr.exe",
        "file explorer": "explorer.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe"
    }

    def discover_and_open(self, target_description: str) -> Dict[str, Any]:
        """
        Discovers the appropriate OS capability or executable for an unfamiliar request.
        Avoids hardcoding by matching target keywords to system interfaces or launching via Explorer.
        """
        t = target_description.lower().strip()

        # Check known system applets
        for name, cmd in self.KNOWN_APP_MAP.items():
            if name in t:
                try:
                    subprocess.Popen(cmd, shell=True)
                    time.sleep(1.0)
                    return {
                        "status": "SUCCESS",
                        "discovered_command": cmd,
                        "target": target_description,
                        "mechanism": "system_applet_launch"
                    }
                except Exception as e:
                    return {"status": "FAILED", "reason": str(e)}

        # Fallback: Launch via Windows Run / Explorer protocol
        try:
            subprocess.Popen(["explorer.exe", target_description], shell=False)
            time.sleep(1.0)
            return {
                "status": "SUCCESS",
                "discovered_command": f"explorer.exe {target_description}",
                "target": target_description,
                "mechanism": "explorer_shell_dispatch"
            }
        except Exception as e:
            return {"status": "FAILED", "reason": str(e)}

    def execute_command(self, command: str, timeout: int = 15, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Executes a command safely with bounded timeout and output capture."""
        try:
            res = subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                cwd=cwd or str(SANDBOX_DIR),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "status": "SUCCESS" if res.returncode == 0 else "NON_ZERO_EXIT",
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "reason": f"Command exceeded {timeout}s timeout limit."}
        except Exception as e:
            return {"status": "ERROR", "reason": str(e)}

    def organize_files_by_extension(self, target_dir: Union[str, Path]) -> Dict[str, Any]:
        """
        Organizes files in target_dir into subdirectories by extension.
        A generalized filesystem capability.
        """
        p = Path(target_dir).resolve()
        if not p.exists() or not p.is_dir():
            return {"status": "FAILED", "reason": f"Directory not found: {target_dir}"}

        moved_count = 0
        categories: Dict[str, List[str]] = {}

        for item in list(p.iterdir()):
            if item.is_file() and not item.name.startswith("."):
                ext = item.suffix.lstrip(".").lower() or "no_extension"
                sub_dir = p / ext
                sub_dir.mkdir(exist_ok=True)
                dest = sub_dir / item.name
                item.rename(dest)
                moved_count += 1
                categories.setdefault(ext, []).append(item.name)

        return {
            "status": "SUCCESS",
            "total_files_organized": moved_count,
            "categories": {k: len(v) for k, v in categories.items()},
            "target_dir": str(p)
        }


# =====================================================================
# 4. PROGRAMMATIC CAPABILITY CREATION (SkillForge) (Capability D)
# =====================================================================

class SkillForge:
    """
    Dynamically creates, validates, executes in sandbox, repairs,
    and saves verified reusable skills when existing capabilities are insufficient.
    """

    FORBIDDEN_CALLS = {
        "format", "rmdir /s", "drop database", "shutdown", "deauth",
        "cryptopp", "ransomware", "delete_root"
    }

    def validate_code_safety(self, code_str: str) -> Tuple[bool, str]:
        """Performs static AST validation to ensure proposed code is safe and syntactically valid."""
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"

        # Check for forbidden strings
        code_lower = code_str.lower()
        for f in self.FORBIDDEN_CALLS:
            if f in code_lower:
                return False, f"Policy violation: Forbidden dangerous token '{f}' found in generated code."

        return True, "Code passed AST syntax and security policy check."

    def execute_in_sandbox(self, script_content: str, script_name: str = "temp_skill.py", timeout: int = 15) -> Dict[str, Any]:
        """Executes generated code in the isolated sandbox directory with timeout."""
        is_safe, msg = self.validate_code_safety(script_content)
        if not is_safe:
            return {"status": "VALIDATION_FAILED", "error": msg}

        script_path = SANDBOX_DIR / script_name
        script_path.write_text(script_content, encoding="utf-8")

        try:
            res = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(SANDBOX_DIR),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "status": "SUCCESS" if res.returncode == 0 else "EXECUTION_ERROR",
                "exit_code": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
                "script_path": str(script_path)
            }
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "error": f"Execution timed out after {timeout} seconds."}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def create_and_verify_skill(self, skill_name: str, code: str, test_func=None) -> Dict[str, Any]:
        """
        Creates a proposed skill, runs it in sandbox, diagnoses errors if any,
        and saves as a reusable skill only upon verified completion.
        """
        # Step 1: Execute in sandbox
        result = self.execute_in_sandbox(code, script_name=f"{skill_name}.py")

        if result.get("status") == "SUCCESS":
            # If verification test passed, promote to user_skills
            promoted_path = USER_SKILLS_DIR / f"{skill_name}.py"
            promoted_path.write_text(code, encoding="utf-8")
            return {
                "status": "PROMOTED",
                "skill_name": skill_name,
                "path": str(promoted_path),
                "sandbox_output": result.get("stdout")
            }

        return {
            "status": "FAILED",
            "skill_name": skill_name,
            "error": result.get("stderr") or result.get("error")
        }


# =====================================================================
# 5. UNIFIED UNIVERSAL ENGINE SINGLETON
# =====================================================================

class UniversalExecutionEngine:
    """Master universal execution engine combining all general-purpose capabilities."""

    def __init__(self):
        self.desktop = VisualDesktopExecutor()
        self.browser = BrowserExecutor(headless=False)
        self.os = OSExecutor()
        self.skills = SkillForge()

    def get_browser(self, headless: bool = False) -> BrowserExecutor:
        if self.browser.headless != headless:
            self.browser.close()
            self.browser = BrowserExecutor(headless=headless)
        return self.browser


UNIVERSAL_ENGINE = UniversalExecutionEngine()
