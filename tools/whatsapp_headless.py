# -*- coding: utf-8 -*-
"""
SIMRAN / JARVIS Headless WhatsApp Automation Tool Module
Precision DOM automation with Playwright.
Silent background messaging without opening any browser or app window.
"""

import asyncio
import os
import sys
from pathlib import Path

CHROME_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

# Standard profile directory
DEFAULT_PROFILE_DIR = os.path.expanduser("~/Documents/JARVIS/.jarvis_whatsapp_profile")
DEBUG_DIR = os.path.expanduser("~/Documents/JARVIS/wa_debug")

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.navigator.chrome = { runtime: {} };
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'hi', 'pa'] });
"""

async def check_whatsapp_headless_status() -> str:
    """Checks whether an active logged-in WhatsApp session exists in the headless profile."""
    from playwright.async_api import async_playwright
    prof = DEFAULT_PROFILE_DIR
    if not os.path.exists(prof):
        return "⚠️ Headless WhatsApp session is NOT linked. Please run 'whatsapp_headless_link' to scan the QR code once."

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=prof,
                headless=True,
                user_agent=CHROME_USER_AGENT,
                viewport={"width": 1366, "height": 768},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--disable-dev-shm-usage",
                ],
            )
            try:
                page = browser.pages[0] if browser.pages else await browser.new_page()
                await page.add_init_script(STEALTH_JS)
                await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(2.0)

                for _ in range(15):
                    logged_in = await page.evaluate("""() => {
                        return !!(document.querySelector('#side') ||
                                  document.querySelector('input[data-tab="3"]') ||
                                  document.querySelector('#pane-side'));
                    }""")
                    if logged_in:
                        return "✅ WhatsApp headless session is ACTIVE and linked. Ready to send messages silently in background!"
                    await asyncio.sleep(1.0)

                return "⚠️ WhatsApp Web is not authenticated. Please scan QR code using 'whatsapp_headless_link'."
            finally:
                await browser.close()
    except Exception as e:
        return f"Error checking WhatsApp session: {e}"

async def send_whatsapp_headless(contact_name: str, message: str) -> str:
    """
    Sends a WhatsApp message silently in the background (headless mode) without opening any UI window.
    """
    from playwright.async_api import async_playwright
    if not contact_name.strip():
        return "❌ Error: Please specify a recipient contact name."
    if not message.strip():
        return "❌ Error: Message content cannot be empty."

    prof = DEFAULT_PROFILE_DIR
    os.makedirs(prof, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=prof,
                headless=True,
                user_agent=CHROME_USER_AGENT,
                viewport={"width": 1366, "height": 768},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--disable-dev-shm-usage",
                ],
            )
            try:
                page = browser.pages[0] if browser.pages else await browser.new_page()
                try:
                    await page.add_init_script(STEALTH_JS)
                except Exception:
                    pass

                await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(2.5)

                logged_in = False
                for _ in range(25):
                    logged_in = await page.evaluate("""() => {
                        return !!(document.querySelector('#side') ||
                                  document.querySelector('input[data-tab="3"]') ||
                                  document.querySelector('#pane-side'));
                    }""")
                    if logged_in:
                        break
                    await asyncio.sleep(1.0)

                if not logged_in:
                    return "⚠️ WhatsApp Web is not linked. Please run 'whatsapp_headless_link' to scan the QR code first."

                await asyncio.sleep(1.0)

                # Type contact name in search box
                search_typed = await page.evaluate("""(contactName) => {
                    const input = document.querySelector('input[data-tab="3"]') ||
                                  document.querySelector('input[role="textbox"]') ||
                                  document.querySelector('input[aria-label="Search or start a new chat"]') ||
                                  document.querySelector('#side input[type="text"]');
                    if (!input) return 'no_input';
                    input.focus();
                    input.click();
                    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeSetter.call(input, contactName);
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    return 'ok';
                }""", contact_name)

                if search_typed != "ok":
                    return f"❌ Could not access WhatsApp search box ({search_typed})."

                await asyncio.sleep(2.5)

                matches = await page.evaluate("""(contactName) => {
                    const lowerName = contactName.toLowerCase();
                    const found = [];
                    const seen = new Set();
                    const filterLabels = new Set(['all', 'unread', 'groups', 'chats', 'messages']);
                    const spans = document.querySelectorAll('#pane-side span[title], #side span[title]');
                    for (const span of spans) {
                        const title = span.title.trim();
                        const lowerTitle = title.toLowerCase();
                        if (title && !filterLabels.has(lowerTitle) && lowerTitle.includes(lowerName)) {
                            if (!seen.has(lowerTitle)) {
                                seen.add(lowerTitle);
                                found.push(title);
                            }
                        }
                    }
                    return found;
                }""", contact_name)

                if not matches:
                    return f"❌ No WhatsApp contact found matching '{contact_name}'. Please verify the name."

                exact_matches = [m for m in matches if m.lower() == contact_name.lower().strip()]
                if len(exact_matches) == 1:
                    target_name = exact_matches[0]
                elif len(matches) > 1:
                    return f"⚠️ Multiple contacts found matching '{contact_name}': {', '.join(matches)}. Please be more specific."
                else:
                    target_name = matches[0]

                target_span = page.locator(f'#side span[title="{target_name}"], span[title="{target_name}"]').first
                box = await target_span.bounding_box()
                if not box:
                    await page.evaluate("""(name) => {
                        const spans = document.querySelectorAll('span[title]');
                        for (const s of spans) {
                            if (s.title.trim().toLowerCase() === name.toLowerCase()) {
                                s.closest('div[role="listitem"]')?.click() || s.click();
                                return true;
                            }
                        }
                    }""", target_name)
                else:
                    await page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)

                await asyncio.sleep(2.0)

                footer_ready = False
                for _ in range(16):
                    footer_ready = await page.evaluate("""() => {
                        return !!(document.querySelector('footer div[contenteditable="true"]') ||
                                  document.querySelector('#main footer'));
                    }""")
                    if footer_ready:
                        break
                    await asyncio.sleep(0.5)

                if not footer_ready:
                    return f"❌ Could not open chat conversation for '{target_name}'."

                msg_input = page.locator('footer div[contenteditable="true"]').first
                await msg_input.click()
                await asyncio.sleep(0.3)
                await page.keyboard.type(message, delay=12)
                await asyncio.sleep(0.5)

                send_btn = page.locator('button[aria-label="Send"]').first
                send_box = await send_btn.bounding_box()
                if send_box:
                    await page.mouse.click(send_box['x'] + send_box['width'] / 2, send_box['y'] + send_box['height'] / 2)
                else:
                    await page.keyboard.press("Enter")

                await asyncio.sleep(2.0)
                return f"✅ [Headless WhatsApp] Message successfully sent to '{target_name}': \"{message}\""

            finally:
                await browser.close()
    except Exception as e:
        return f"❌ Error sending headless WhatsApp message: {e}"

async def setup_whatsapp_headless() -> str:
    """Opens a visible browser window so user can scan QR code to link device."""
    from playwright.async_api import async_playwright
    prof = DEFAULT_PROFILE_DIR
    os.makedirs(prof, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=prof,
                headless=False,
                user_agent=CHROME_USER_AGENT,
                viewport={"width": 1280, "height": 850},
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            try:
                page = browser.pages[0] if browser.pages else await browser.new_page()
                try:
                    await page.add_init_script(STEALTH_JS)
                except Exception:
                    pass

                await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=60000)

                for _ in range(80):
                    logged_in = await page.evaluate("""() => {
                        return !!(document.querySelector('#side') ||
                                  document.querySelector('#pane-side') ||
                                  document.querySelector('input[data-tab="3"]'));
                    }""")
                    if logged_in:
                        await asyncio.sleep(5.0)
                        return "✅ WhatsApp Web linked successfully! Session is permanently saved for headless messaging."
                    await asyncio.sleep(1.5)

                return "⚠️ QR scan timed out after 120 seconds. Please try again."
            finally:
                await browser.close()
    except Exception as e:
        return f"❌ Error during WhatsApp setup: {e}"
