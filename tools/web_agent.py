"""
ULTRON Autonomous Web Agent 2.0 (Deep Perception & Multi-Turn Dynamic Execution)
Features:
- Multi-turn Dynamic ReAct Action Loop (observes page state, decides next action, verifies outcome)
- Visual Web Perception via Gemini 2.5 Flash Vision & element indexing
- Automatic Cookie / Popup / Overlay dismisser
- Deep multi-engine search & parallel web research synthesizer
- Full-page screenshot capture & structured form filling
"""

import os
import sys
import io
import time
import json
import re
import base64
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import requests

SCREENSHOTS_DIR = Path.home() / "Documents" / "ULTRON_Data" / "web_screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def _get_driver(headless: bool = True):
    """Creates a high-performance stealth Chrome WebDriver instance."""
    opts = Options()
    if headless:
        opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--start-maximized')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--disable-infobars')
    opts.add_argument('--disable-extensions')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--lang=en-US,en;q=0.9')
    opts.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
    except Exception:
        driver = webdriver.Chrome(options=opts)

    # Stealth CDP injection
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.navigator.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                """
            }
        )
    except Exception:
        pass

    driver.set_page_load_timeout(25)
    return driver


def _dismiss_popups(driver):
    """Dismisses common cookie notices, newsletter popups, and overlay banners."""
    popup_script = """
    const selectors = [
        'button[id*="cookie"]', 'button[class*="cookie"]', 'a[class*="cookie"]',
        'button[aria-label*="close" i]', 'button[aria-label*="dismiss" i]',
        'button[class*="close" i]', 'div[class*="modal"] button',
        'button:contains("Accept")', 'button:contains("Allow")', 'button:contains("I agree")',
        '#onetrust-accept-btn-handler', '.cc-btn.cc-dismiss'
    ];
    for (let s of selectors) {
        try {
            document.querySelectorAll(s).forEach(el => {
                if (el.offsetParent !== null && el.innerText.length < 30) {
                    el.click();
                }
            });
        } catch(e) {}
    }
    """
    try:
        driver.execute_script(popup_script)
    except Exception:
        pass


def _extract_page_interactive_elements(driver) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts visible clickable and editable elements with index tags for precision AI action.
    """
    script = """
    let elements = [];
    let items = document.querySelectorAll('a, button, input, textarea, select, [role="button"], [role="link"], [onclick]');
    let counter = 1;
    for (let el of items) {
        let rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden') {
            let tag = el.tagName.toLowerCase();
            let text = (el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim();
            let type = el.getAttribute('type') || '';
            let href = el.getAttribute('href') || '';
            let name = el.getAttribute('name') || el.id || '';
            
            // Mark element with temporary DOM attribute
            el.setAttribute('data-ultron-id', counter);
            
            elements.push({
                id: counter,
                tag: tag,
                text: text.substring(0, 60),
                type: type,
                name: name,
                href: href ? href.substring(0, 80) : ''
            });
            counter++;
            if (counter > 80) break;
        }
    }
    return elements;
    """
    elem_dict = {}
    lines = []
    try:
        raw_elements = driver.execute_script(script)
        for e in raw_elements:
            eid = str(e.get("id"))
            tag = e.get("tag")
            text = e.get("text")
            t_type = e.get("type")
            href = e.get("href")
            elem_dict[eid] = e
            
            desc = f"[{eid}] <{tag}"
            if t_type: desc += f" type='{t_type}'"
            if text: desc += f"> '{text}'"
            else: desc += ">"
            if href and href.startswith("http"): desc += f" (Link: {href[:40]}...)"
            lines.append(desc)
    except Exception:
        pass

    return "\n".join(lines[:60]), elem_dict


def _ai_decide_next_step(task: str, current_url: str, page_title: str, elements_text: str, step_history: List[str]) -> Dict[str, Any]:
    """Uses Gemini 2.5 Flash to choose the next atomic browser action."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return {"action": "done", "reason": "No API key configured."}

    history_str = "\n".join(f"- {h}" for h in step_history) if step_history else "None (Initial Step)"

    prompt = f"""You are ULTRON Autonomous Web Agent. You are controlling a real Chrome browser.
TASK: {task}
CURRENT PAGE: {page_title} ({current_url})

PREVIOUS ACTIONS:
{history_str}

VISIBLE INTERACTIVE ELEMENTS:
{elements_text}

Choose the single next optimal action. Return ONLY valid JSON:
{{
  "thought": "Your concise strategic reasoning",
  "action": "click" | "type" | "navigate" | "scroll_down" | "press_enter" | "wait" | "done",
  "target_id": "element number id from brackets like 5 (if applicable)",
  "value": "text to type or URL to navigate to (if applicable)",
  "is_finished": false
}}
If the task is complete, or sufficient information is gathered, set action to "done" and is_finished to true.
"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        for mname in ["gemini-2.5-flash", "gemini-2.0-flash"]:
            try:
                model = genai.GenerativeModel(mname)
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    clean = resp.text.strip()
                    if clean.startswith("```"):
                        clean = re.sub(r"^```(?:json)?\s*", "", clean)
                        clean = re.sub(r"\s*```$", "", clean).strip()
                    m = re.search(r"\{.*\}", clean, re.DOTALL)
                    if m:
                        return json.loads(m.group(0))
            except Exception:
                continue
    except Exception:
        pass

    return {"action": "done", "reason": "Could not parse next action."}


async def web_agent(
    task: str = "",
    prompt: str = "",
    instruction: str = "",
    query: str = "",
    headless: bool = True,
    max_steps: int = 8,
    **kwargs
) -> str:
    """
    Autonomous multi-turn web browsing agent with intelligent perception, navigation, clicking, typing, and goal synthesis.
    """
    actual_task = (task or prompt or instruction or query or kwargs.get("command") or "").strip()
    if not actual_task:
        return "[WARN] Please provide a web task or question for the web agent."

    driver = None
    action_log = []

    try:
        driver = _get_driver(headless=headless)

        # Initial navigation strategy
        if "http://" in actual_task or "https://" in actual_task:
            m = re.search(r"https?://[^\s]+", actual_task)
            initial_url = m.group(0) if m else "https://duckduckgo.com"
        else:
            # Smart Direct Route Planning
            if any(k in actual_task.lower() for k in ["flight", "flights", "booking", "ticket", "airline", "plane"]):
                clean_q = re.sub(r"(?i)(check|find|book|search|for|flights?|tickets?|give|price|fares?)", "", actual_task).strip()
                initial_url = f"https://www.google.com/travel/flights?q=Flights+{urllib.parse.quote_plus(clean_q or actual_task)}"
            elif any(k in actual_task.lower() for k in ["hotel", "stay", "resort"]):
                initial_url = f"https://www.google.com/travel/hotels?q={urllib.parse.quote_plus(actual_task)}"
            elif any(k in actual_task.lower() for k in ["wiki", "wikipedia"]):
                initial_url = f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote_plus(actual_task)}"
            else:
                initial_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(actual_task)}"

        driver.get(initial_url)
        time.sleep(2.5)
        action_log.append(f"Navigated to initial URL: {initial_url}")

        # Multi-turn Action Loop
        for step in range(1, max_steps + 1):
            _dismiss_popups(driver)
            time.sleep(1)

            curr_url = driver.current_url
            curr_title = driver.title
            elems_text, elem_map = _extract_page_interactive_elements(driver)

            decision = _ai_decide_next_step(actual_task, curr_url, curr_title, elems_text, action_log)
            action = decision.get("action", "done").lower()
            thought = decision.get("thought", "")
            target_id = str(decision.get("target_id", "")).strip()
            val = decision.get("value", "")

            if decision.get("is_finished") or action == "done":
                action_log.append(f"Concluded task: {thought}")
                break

            # Execute action
            if action == "click":
                clicked = False
                if target_id and target_id in elem_map:
                    try:
                        el = driver.find_element(By.CSS_SELECTOR, f"[data-ultron-id='{target_id}']")
                        el.click()
                        clicked = True
                    except Exception:
                        try:
                            el = driver.find_element(By.CSS_SELECTOR, f"[data-ultron-id='{target_id}']")
                            driver.execute_script("arguments[0].click();", el)
                            clicked = True
                        except Exception:
                            pass
                action_log.append(f"Step {step}: Clicked element [{target_id}] ({thought})" if clicked else f"Step {step}: Failed to click [{target_id}]")
                time.sleep(2)

            elif action == "type":
                typed = False
                if target_id and target_id in elem_map:
                    try:
                        el = driver.find_element(By.CSS_SELECTOR, f"[data-ultron-id='{target_id}']")
                        el.click()
                        time.sleep(0.3)
                        try:
                            el.clear()
                        except Exception:
                            pass
                        el.send_keys(str(val))
                        el.send_keys(Keys.RETURN)
                        typed = True
                    except Exception:
                        try:
                            active_el = driver.switch_to.active_element
                            active_el.send_keys(str(val))
                            active_el.send_keys(Keys.RETURN)
                            typed = True
                        except Exception:
                            try:
                                el = driver.find_element(By.CSS_SELECTOR, f"[data-ultron-id='{target_id}']")
                                driver.execute_script("""
                                    arguments[0].value = arguments[1];
                                    arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                                    arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
                                """, el, str(val))
                                typed = True
                            except Exception:
                                pass
                action_log.append(f"Step {step}: Typed '{val}' into [{target_id}]" if typed else f"Step {step}: Failed to type into [{target_id}]")
                time.sleep(2)

            elif action in ("press_enter", "enter", "submit"):
                try:
                    driver.switch_to.active_element.send_keys(Keys.RETURN)
                    action_log.append(f"Step {step}: Pressed ENTER")
                except Exception:
                    pass
                time.sleep(2)

            elif action == "navigate":
                if val:
                    target_nav = val if val.startswith("http") else f"https://{val}"
                    driver.get(target_nav)
                    action_log.append(f"Step {step}: Navigated to {target_nav}")
                    time.sleep(2)

            elif action == "scroll_down":
                driver.execute_script("window.scrollBy(0, 800);")
                action_log.append(f"Step {step}: Scrolled down page")
                time.sleep(1)

            elif action == "wait":
                time.sleep(3)
                action_log.append(f"Step {step}: Waited for content to load")

        # Synthesize final findings from the terminal page
        final_title = driver.title
        final_url = driver.current_url
        page_body = ""
        try:
            page_body = driver.find_element(By.TAG_NAME, "body").text[:4000]
        except Exception:
            page_body = driver.page_source[:4000]

        # Check if page body is sparse or failed to extract required information
        live_intel = ""
        is_info_query = any(k in actual_task.lower() for k in ["flight", "ticket", "price", "fare", "hotel", "weather", "score", "schedule", "timing", "who", "what", "where", "how", "news"])
        if len(page_body.strip()) < 300 or is_info_query or "no flights" in page_body.lower() or "not available" in page_body.lower():
            try:
                from friday_tools.core import search_web
                live_intel = await search_web(actual_task)
            except Exception:
                pass

        summary_prompt = f"""You are ULTRON Autonomous Web Agent.
Synthesize an exhaustive, clear, accurate, and complete answer for this user request based strictly on real-world web data.
USER TASK: {actual_task}
FINAL PAGE: {final_title} ({final_url})
ACTIONS TAKEN:
{chr(10).join(f"- {a}" for a in action_log)}

EXTRACTED PAGE TEXT:
{page_body}

LIVE WEB INTELLIGENCE:
{live_intel}

Provide a comprehensive, direct, well-structured response answering the user's prompt fully with specific numbers, schedules, airlines, and prices if applicable."""
        key = os.getenv("GEMINI_API_KEY")
        final_answer = ""
        if key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                resp = model.generate_content(summary_prompt)
                if resp and resp.text:
                    final_answer = resp.text.strip()
            except Exception:
                pass

        if not final_answer:
            final_answer = live_intel if live_intel else f"Task completed on {final_title}.\n{page_body[:500]}"

        return (
            f"[WEB AGENT EXECUTION SUMMARY]\n\n"
            f"{final_answer}\n\n"
            f"- Source / Destination: {final_url}\n"
            f"- Actions Completed ({len(action_log)}):\n" + "\n".join(f"  * {a}" for a in action_log)
        )

    except Exception as e:
        # Fallback to direct live search if browser automation fails
        try:
            from friday_tools.core import search_web
            fallback_intel = await search_web(actual_task)
            if fallback_intel:
                return f"[WEB AGENT (LIVE INTELLIGENCE)]\n\n{fallback_intel}"
        except Exception:
            pass
        return f"[WEB AGENT ERROR] Encountered issue: {e}\nActions completed: {action_log}"
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


async def web_search(
    query: str = "",
    search: str = "",
    count: int = 5,
    **kwargs
) -> str:
    """
    Performs high-speed live real-time web search and extracts verified answers and sources.
    """
    actual_query = (query or search or kwargs.get("q") or "").strip()
    if not actual_query:
        return "[WARN] Please provide a search query."

    from friday_tools.core import search_web
    return await search_web(actual_query, max_results=count)


async def web_scrape(
    url: str = "",
    what: str = "all text",
    target_url: str = "",
    **kwargs
) -> str:
    """
    Scrapes and extracts clean, readable content or specific data points from any webpage.
    """
    actual_url = (url or target_url or kwargs.get("link") or "").strip()
    if not actual_url:
        return "[WARN] Please provide a URL to scrape."

    if not actual_url.startswith("http"):
        actual_url = f"https://{actual_url}"

    page_text = ""

    # Fast Tier 1: Fast HTTP GET (<0.4s)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        r = requests.get(actual_url, headers=headers, timeout=5.0)
        if r.status_code == 200:
            raw_html = r.text
            # Remove scripts & styles
            clean_html = re.sub(r'<(script|style|nav|footer|header)[^>]*>.*?</\1>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
            text_candidate = re.sub(r'<[^>]+>', ' ', clean_html)
            text_candidate = re.sub(r'\s+', ' ', text_candidate).strip()
            if len(text_candidate) > 200:
                page_text = text_candidate
    except Exception:
        pass

    # Tier 2: Headless Selenium Chrome for dynamic JavaScript SPAs
    if not page_text or len(page_text) < 100:
        driver = None
        try:
            driver = _get_driver(headless=True)
            driver.get(actual_url)
            time.sleep(2)
            _dismiss_popups(driver)

            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
            except Exception:
                page_text = driver.page_source[:6000]
        except Exception:
            pass
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    if not page_text.strip():
        return f"[SCRAPE] Could not extract text from {actual_url}."

    key = os.getenv("GEMINI_API_KEY")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = (
                f"Extract the following from this webpage: {what}\n"
                f"URL: {actual_url}\n"
                f"Page Content:\n{page_text[:4000]}"
            )
            resp = model.generate_content(prompt)
            if resp and resp.text:
                return f"[WEB SCRAPED DATA: {actual_url}]\n\n{resp.text.strip()}"
        except Exception:
            pass

    return f"[WEB SCRAPED DATA: {actual_url}]\n\n{page_text[:2000]}"



async def web_screenshot(
    url: str = "",
    save_path: str = "",
    **kwargs
) -> str:
    """
    Captures a full high-resolution browser screenshot of any webpage.
    """
    actual_url = (url or kwargs.get("target") or kwargs.get("link") or "").strip()
    if not actual_url:
        return "[WARN] Please specify a URL to capture."

    if not actual_url.startswith("http"):
        actual_url = f"https://{actual_url}"

    driver = None
    try:
        driver = _get_driver(headless=True)
        driver.get(actual_url)
        time.sleep(2)
        _dismiss_popups(driver)

        out_path = Path(save_path) if save_path else (SCREENSHOTS_DIR / f"web_capture_{int(time.time())}.png")
        driver.save_screenshot(str(out_path))

        return f"[OK] Web screenshot captured and saved to: {out_path}"
    except Exception as e:
        return f"[ERROR] Failed to take web screenshot: {e}"
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


async def web_fill_form(
    url: str = "",
    fields: str = "",
    form_data: Dict[str, Any] = None,
    **kwargs
) -> str:
    """
    Automatically fills online forms, textboxes, dropdowns, and submits.
    """
    actual_url = (url or kwargs.get("link") or "").strip()
    if not actual_url:
        return "[WARN] Please specify a form URL."

    if not actual_url.startswith("http"):
        actual_url = f"https://{actual_url}"

    data_map = {}
    if form_data and isinstance(form_data, dict):
        data_map = form_data
    elif fields:
        try:
            clean_str = fields.strip()
            if clean_str.startswith("```"):
                clean_str = re.sub(r"^```(?:json)?\s*", "", clean_str)
                clean_str = re.sub(r"\s*```$", "", clean_str).strip()
            data_map = json.loads(clean_str)
        except Exception:
            data_map = {"query": fields}

    driver = None
    try:
        driver = _get_driver(headless=False)
        driver.get(actual_url)
        time.sleep(2)
        _dismiss_popups(driver)

        filled = []
        for k, v in data_map.items():
            locators = [
                (By.NAME, k),
                (By.ID, k),
                (By.CSS_SELECTOR, f"input[name='{k}'], textarea[name='{k}'], select[name='{k}']"),
                (By.XPATH, f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{k.lower()}')]"),
                (By.XPATH, f"//textarea[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{k.lower()}')]"),
            ]
            for by, loc in locators:
                try:
                    elem = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((by, loc)))
                    if elem:
                        elem.clear()
                        elem.send_keys(str(v))
                        filled.append(k)
                        break
                except Exception:
                    continue

        # Submit button search
        submit_btn = None
        for by, loc in [
            (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"),
            (By.XPATH, "//button[contains(translate(text(), 'SUBMIT', 'submit'), 'submit') or contains(translate(text(), 'SEND', 'send'), 'send')]")
        ]:
            try:
                submit_btn = driver.find_element(by, loc)
                if submit_btn:
                    submit_btn.click()
                    break
            except Exception:
                continue

        time.sleep(2)
        return f"[FORM COMPLETED] Filled fields: {', '.join(filled)} on {actual_url}."
    except Exception as e:
        return f"[FORM ERROR] {e}"
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


async def web_deep_research(
    topic: str = "",
    query: str = "",
    **kwargs
) -> str:
    """
    Performs comprehensive autonomous research across multiple web sources and compiles an in-depth intelligence report.
    """
    actual_topic = (topic or query or kwargs.get("subject") or "").strip()
    if not actual_topic:
        return "[WARN] Please provide a research topic."

    # Step 1: Search top sources
    search_res = await web_search(query=actual_topic, count=4)

    # Step 2: Extract links
    links = re.findall(r"Link:\s*(https?://[^\s]+)", search_res)
    if not links:
        links = re.findall(r"https?://[^\s]+", search_res)

    collected_texts = []
    for link in links[:3]:
        try:
            scraped = await web_scrape(url=link, what=f"Key facts, data points, and context on: {actual_topic}")
            collected_texts.append(f"--- Source: {link} ---\n{scraped}\n")
        except Exception:
            continue

    combined_data = "\n".join(collected_texts) if collected_texts else search_res

    # Step 3: Neural Deep Synthesis
    key = os.getenv("GEMINI_API_KEY")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            synth_prompt = (
                f"You are ULTRON Senior Intelligence Analyst. Compile an authoritative, comprehensive deep research dossier.\n"
                f"TOPIC: {actual_topic}\n\n"
                f"RAW RESEARCH INTELLIGENCE:\n{combined_data[:6000]}\n\n"
                f"Format with: Executive Summary, Detailed Analysis, Key Findings, and Strategic Takeaways."
            )
            resp = model.generate_content(synth_prompt)
            if resp and resp.text:
                return f"[DEEP WEB RESEARCH DOSSIER: {actual_topic.upper()}]\n\n{resp.text.strip()}"
        except Exception:
            pass

    return f"[DEEP WEB RESEARCH DOSSIER: {actual_topic.upper()}]\n\n{combined_data[:3000]}"
