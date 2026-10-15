"""
ULTRON Advanced Stealth Browser & Anti-Detection Automation Engine
Configures Chrome with realistic user agent headers, disabled automation flags,
humanized typing cadence, and session profile persistence to navigate modern web interfaces smoothly.
"""

import os
import time
import json
import asyncio
from typing import Optional, Dict, Any

async def stealth_web_browse(url: str, wait_seconds: int = 4, capture_screenshot: bool = True) -> str:
    """
    Opens a URL in a stealth-configured Chrome browser, bypassing common basic webdriver bot-detection fingerprints.
    """
    def _run_browser():
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)

        try:
            # Overwrite navigator.webdriver flag in javascript
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })

            driver.get(url)
            time.sleep(wait_seconds)

            title = driver.title
            page_src_len = len(driver.page_source)

            screenshot_path = ""
            if capture_screenshot:
                out_dir = os.path.expanduser(r"~\Documents\ULTRON_Data\screenshots")
                os.makedirs(out_dir, exist_ok=True)
                screenshot_path = os.path.join(out_dir, f"stealth_{int(time.time())}.png")
                driver.save_screenshot(screenshot_path)

            return f"[STEALTH BROWSER] Successfully loaded: '{title}' ({url})\nPage content size: {page_src_len} chars.\nScreenshot: {screenshot_path or 'None'}"
        finally:
            driver.quit()

    return await asyncio.to_thread(_run_browser)
