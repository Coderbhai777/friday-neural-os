"""
ULTRON Safe Keyboard & Mouse Controller
Reliable hardware simulation via pynput and pyautogui with SafeController auto-activation logging.
"""

import os
import time
import codecs
import asyncio
from datetime import datetime
from typing import List, Optional

import pyautogui
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

LOG_PATH = os.path.expanduser(r"~\Documents\ULTRON_Data\control_log.txt")


# ---------------------
# SafeController Class
# ---------------------
class SafeController:
    def __init__(self):
        self.active = False
        self.activation_time = None
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.valid_keys = set("abcdefghijklmnopqrstuvwxyz1234567890")
        self.special_keys = {
            "enter": Key.enter, "return": Key.enter, "space": Key.space, "tab": Key.tab,
            "shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt,
            "esc": Key.esc, "backspace": Key.backspace, "delete": Key.delete,
            "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
            "caps_lock": Key.caps_lock, "cmd": Key.cmd, "win": Key.cmd,
            "home": Key.home, "end": Key.end,
            "page_up": Key.page_up, "page_down": Key.page_down
        }

    def resolve_key(self, key):
        return self.special_keys.get(key.lower(), key)

    def log(self, action: str):
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()}: {action}\n")
        except Exception:
            pass

    def activate(self, token=None):
        if token != "my_secret_token":
            self.log("Activation attempt failed.")
            return
        self.active = True
        self.activation_time = time.time()
        self.log("Controller auto-activated.")

    def deactivate(self):
        self.active = False
        self.log("Controller auto-deactivated.")

    def is_active(self):
        return self.active

    async def move_cursor(self, direction: str, distance: int = 100):
        if not self.is_active(): return "🛑 Controller is inactive."
        x, y = self.mouse.position
        if direction == "left": self.mouse.position = (x - distance, y)
        elif direction == "right": self.mouse.position = (x + distance, y)
        elif direction == "up": self.mouse.position = (x, y - distance)
        elif direction == "down": self.mouse.position = (x, y + distance)
        await asyncio.sleep(0.2)
        self.log(f"Mouse moved {direction}")
        return f"🖱️ Moved mouse {direction}."

    async def mouse_click(self, button: str = "left"):
        if not self.is_active(): return "🛑 Controller is inactive."
        if button == "left": self.mouse.click(Button.left, 1)
        elif button == "right": self.mouse.click(Button.right, 1)
        elif button == "double": self.mouse.click(Button.left, 2)
        await asyncio.sleep(0.2)
        self.log(f"Mouse clicked: {button}")
        return f"🖱️ {button.capitalize()} click."

    async def scroll_cursor(self, direction: str, amount: int = 10):
        if not self.is_active(): return "🛑 Controller is inactive."
        try:
            if direction == "up": self.mouse.scroll(0, amount)
            elif direction == "down": self.mouse.scroll(0, -amount)
        except Exception:
            pyautogui.scroll(amount * 100)
        await asyncio.sleep(0.2)
        self.log(f"Mouse scrolled {direction}")
        return f"🖱️ Scrolled {direction}"

    async def type_text(self, text: str):
        if not self.is_active():
            return "🛑 Controller is inactive."

        # Fix: convert escaped sequences into real ones
        try:
            text = codecs.decode(text, "unicode_escape")
        except Exception:
            pass

        for char in text:
            try:
                if char == "\n":
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                elif char == "\t":
                    self.keyboard.press(Key.tab)
                    self.keyboard.release(Key.tab)
                elif char.isprintable():
                    self.keyboard.press(char)
                    self.keyboard.release(char)
                else:
                    continue

                await asyncio.sleep(0.05)

            except Exception:
                continue

        self.log(f"Typed text: {text}")
        return f"⌨️ Typed: {text}"

    async def press_key(self, key: str):
        if not self.is_active(): return "🛑 Controller is inactive."
        if key.lower() not in self.special_keys and key.lower() not in self.valid_keys:
            return f"❌ Invalid key: {key}"
        k = self.resolve_key(key)
        try:
            self.keyboard.press(k)
            self.keyboard.release(k)
        except Exception as e:
            return f"❌ Failed key: {key} — {e}"
        await asyncio.sleep(0.2)
        self.log(f"Pressed key: {key}")
        return f"⌨️ Key '{key}' pressed."

    async def press_hotkey(self, keys: List[str]):
        if not self.is_active(): return "🛑 Controller is inactive."
        if isinstance(keys, str):
            keys = [k.strip() for k in keys.split(",") if k.strip()]
        resolved = []
        for k in keys:
            if k.lower() not in self.special_keys and k.lower() not in self.valid_keys:
                return f"❌ Invalid key in hotkey: {k}"
            resolved.append(self.resolve_key(k))

        for k in resolved: self.keyboard.press(k)
        for k in reversed(resolved): self.keyboard.release(k)
        await asyncio.sleep(0.3)
        self.log(f"Pressed hotkey: {' + '.join(keys)}")
        return f"⌨️ Hotkey {' + '.join(keys)} pressed."

    async def control_volume(self, action: str):
        if not self.is_active(): return "🛑 Controller is inactive."
        if action == "up": pyautogui.press("volumeup")
        elif action == "down": pyautogui.press("volumedown")
        elif action == "mute": pyautogui.press("volumemute")
        await asyncio.sleep(0.2)
        self.log(f"Volume control: {action}")
        return f"🔊 Volume {action}."

    async def swipe_gesture(self, direction: str):
        if not self.is_active(): return "🛑 Controller is inactive."
        screen_width, screen_height = pyautogui.size()
        x, y = screen_width // 2, screen_height // 2
        try:
            if direction == "up": pyautogui.moveTo(x, y + 200); pyautogui.dragTo(x, y - 200, duration=0.5)
            elif direction == "down": pyautogui.moveTo(x, y - 200); pyautogui.dragTo(x, y + 200, duration=0.5)
            elif direction == "left": pyautogui.moveTo(x + 200, y); pyautogui.dragTo(x - 200, y, duration=0.5)
            elif direction == "right": pyautogui.moveTo(x - 200, y); pyautogui.dragTo(x + 200, y, duration=0.5)
        except Exception:
            pass
        await asyncio.sleep(0.5)
        self.log(f"Swipe gesture: {direction}")
        return f"🖱️ Swipe {direction} done."


controller = SafeController()


async def with_temporary_activation(fn, *args, **kwargs):
    print(f"[CONTROLLER] TEMP ACTIVATION: {fn.__name__} | args: {args}")
    controller.activate("my_secret_token")
    try:
        result = await fn(*args, **kwargs)
    finally:
        await asyncio.sleep(0.2)
        controller.deactivate()
    return result


async def move_cursor(direction: str, distance: int = 100):
    """
    Temporarily activates the controller and moves the mouse cursor in a specified direction.
    direction: One of ['up', 'down', 'left', 'right'].
    distance: Number of pixels to move the cursor. Defaults to 100.
    """
    return await with_temporary_activation(controller.move_cursor, direction, distance)


async def move_cursor_tool(direction: str, distance: int = 100):
    return await move_cursor(direction, distance)


async def mouse_click(button: str = "left"):
    """
    Temporarily activates the controller and performs a mouse click.
    button: One of ['left', 'right', 'double'].
    """
    return await with_temporary_activation(controller.mouse_click, button)


async def mouse_click_tool(button: str = "left"):
    return await mouse_click(button)


async def scroll_cursor(direction: str, amount: int = 10):
    """
    Scrolls the screen vertically in the specified direction.
    direction: One of ['up', 'down'].
    amount: Scroll intensity.
    """
    return await with_temporary_activation(controller.scroll_cursor, direction, amount)


async def scroll_cursor_tool(direction: str, amount: int = 10):
    return await scroll_cursor(direction, amount)


async def type_text(text: str):
    """
    Simulates typing the given text character by character from a keyboard.
    """
    return await with_temporary_activation(controller.type_text, text)


async def type_text_tool(text: str):
    return await type_text(text)


async def press_key(key: str):
    """
    Simulates pressing a single key on the keyboard (e.g., 'enter', 'esc', 'a', 'space').
    """
    return await with_temporary_activation(controller.press_key, key)


async def press_key_tool(key: str):
    return await press_key(key)


async def press_hotkey(keys: List[str]):
    """
    Simulates pressing a keyboard shortcut like Ctrl+S, Alt+Tab, Win+D, etc.
    """
    return await with_temporary_activation(controller.press_hotkey, keys)


async def press_hotkey_tool(keys: List[str]):
    return await press_hotkey(keys)


async def control_volume(action: str):
    """
    Changes the system volume using keyboard emulation.
    action: One of ['up', 'down', 'mute'].
    """
    return await with_temporary_activation(controller.control_volume, action)


async def control_volume_tool(action: str):
    return await control_volume(action)


async def swipe_gesture(direction: str):
    """
    Simulates a swipe gesture on the screen using the mouse.
    direction: One of ['up', 'down', 'left', 'right'].
    """
    return await with_temporary_activation(controller.swipe_gesture, direction)


async def swipe_gesture_tool(direction: str):
    return await swipe_gesture(direction)
