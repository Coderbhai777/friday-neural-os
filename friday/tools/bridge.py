FRIDAY_DECLARATIONS = [
  {
    "name": "play_on_youtube",
    "description": "YouTube pe video/song chalao",
    "parameters": {
      "type": "object",
      "properties": {
        "topic": {
          "type": "string"
        }
      },
      "required": [
        "topic"
      ]
    }
  },
  {
    "name": "search_on_google",
    "description": "Google pe search karo",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "system_control",
    "description": "System control: volume_up/down, mute, lock, sleep, shutdown, restart, abort_shutdown",
    "parameters": {
      "type": "object",
      "properties": {
        "command": {
          "type": "string"
        }
      },
      "required": [
        "command"
      ]
    }
  },
  {
    "name": "execute_shortcut",
    "description": "Windows shortcut: file_explorer, settings, screenshot_tool, show_desktop, emoji, clipboard_history",
    "parameters": {
      "type": "object",
      "properties": {
        "shortcut_name": {
          "type": "string"
        }
      },
      "required": [
        "shortcut_name"
      ]
    }
  },
  {
    "name": "open_app",
    "description": "Koi bhi app kholo sirf naam se — chrome, vlc, spotify, notepad, vs code, whatsapp, discord, zoom, steam etc. Path dene ki zaroorat nahi.",
    "parameters": {
      "type": "object",
      "properties": {
        "app_name": {
          "type": "string"
        }
      },
      "required": [
        "app_name"
      ]
    }
  },
  {
    "name": "open_app_and_do",
    "description": "App kholo aur kuch karo — jaise notepad kholo aur text type karo",
    "parameters": {
      "type": "object",
      "properties": {
        "app_name": {
          "type": "string"
        },
        "action": {
          "type": "string"
        }
      },
      "required": [
        "app_name"
      ]
    }
  },
  {
    "name": "control_media",
    "description": "Media: play_pause, next, previous, stop",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "set_system_theme",
    "description": "Theme badlo: dark ya light",
    "parameters": {
      "type": "object",
      "properties": {
        "mode": {
          "type": "string"
        }
      },
      "required": [
        "mode"
      ]
    }
  },
  {
    "name": "open_folder",
    "description": "Folder kholo: downloads, documents, desktop etc",
    "parameters": {
      "type": "object",
      "properties": {
        "folder_name": {
          "type": "string"
        }
      },
      "required": [
        "folder_name"
      ]
    }
  },
  {
    "name": "snap_window",
    "description": "Window snap: left, right, up, down",
    "parameters": {
      "type": "object",
      "properties": {
        "direction": {
          "type": "string"
        }
      },
      "required": [
        "direction"
      ]
    }
  },
  {
    "name": "empty_recycle_bin",
    "description": "Recycle Bin saaf karo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "toggle_desktop_icons",
    "description": "Desktop icons show/hide karo",
    "parameters": {
      "type": "object",
      "properties": {
        "visible": {
          "type": "boolean"
        }
      },
      "required": []
    }
  },
  {
    "name": "zoom_screen",
    "description": "Screen zoom: in, out, reset",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "get_clipboard",
    "description": "Clipboard content dekho",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "set_clipboard",
    "description": "Text clipboard mein copy karo",
    "parameters": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string"
        }
      },
      "required": [
        "text"
      ]
    }
  },
  {
    "name": "edit_text",
    "description": "Text edit: copy, paste, cut, undo, redo, select_all",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "generate_password",
    "description": "Strong password banao",
    "parameters": {
      "type": "object",
      "properties": {
        "length": {
          "type": "integer"
        }
      },
      "required": []
    }
  },
  {
    "name": "create_qr_code",
    "description": "QR code banao kisi text ya URL ka",
    "parameters": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string"
        }
      },
      "required": []
    }
  },
  {
    "name": "find_file",
    "description": "File dhoondo. filename, folder (optional), file_type (optional, e.g. .pdf), newest (boolean) parameters do.",
    "parameters": {
      "type": "object",
      "properties": {
        "filename": {
          "type": "string"
        },
        "folder": {
          "type": "string"
        },
        "file_type": {
          "type": "string"
        },
        "newest": {
          "type": "boolean"
        }
      },
      "required": [
        "filename"
      ]
    }
  },
  {
    "name": "organize_downloads",
    "description": "Downloads folder organize karo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "take_screenshot",
    "description": "Screenshot lo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "open_camera",
    "description": "Webcam kholo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "download_youtube",
    "description": "YouTube video download karo",
    "parameters": {
      "type": "object",
      "properties": {
        "url_or_query": {
          "type": "string"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_ip_info",
    "description": "IP aur location info",
    "parameters": {
      "type": "object",
      "properties": {
        "ip": {
          "type": "string"
        }
      },
      "required": []
    }
  },
  {
    "name": "check_internet_speed",
    "description": "Internet speed check karo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_wifi_passwords",
    "description": "Saved WiFi passwords dekho",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_news",
    "description": "Latest news lo",
    "parameters": {
      "type": "object",
      "properties": {
        "topic": {
          "type": "string"
        }
      },
      "required": []
    }
  },
  {
    "name": "search_wikipedia",
    "description": "Wikipedia pe search karo",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "create_note",
    "description": "Quick note banao",
    "parameters": {
      "type": "object",
      "properties": {
        "content": {
          "type": "string"
        },
        "filename": {
          "type": "string"
        }
      },
      "required": [
        "content"
      ]
    }
  },
  {
    "name": "read_latest_note",
    "description": "Sabse latest note padho",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "send_notification",
    "description": "Windows desktop notification bhejo",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "message": {
          "type": "string"
        }
      },
      "required": [
        "title",
        "message"
      ]
    }
  },
  {
    "name": "list_processes",
    "description": "Running processes list karo",
    "parameters": {
      "type": "object",
      "properties": {
        "filter_name": {
          "type": "string"
        }
      },
      "required": []
    }
  },
  {
    "name": "terminate_process",
    "description": "Process band karo",
    "parameters": {
      "type": "object",
      "properties": {
        "process_name": {
          "type": "string"
        }
      },
      "required": [
        "process_name"
      ]
    }
  },
  {
    "name": "set_timer",
    "description": "Timer set karo",
    "parameters": {
      "type": "object",
      "properties": {
        "seconds": {
          "type": "integer"
        },
        "label": {
          "type": "string"
        }
      },
      "required": [
        "seconds"
      ]
    }
  },
  {
    "name": "record_voice",
    "description": "Voice record karo",
    "parameters": {
      "type": "object",
      "properties": {
        "duration_seconds": {
          "type": "integer"
        }
      },
      "required": []
    }
  },
  {
    "name": "record_screen",
    "description": "Screen record karo",
    "parameters": {
      "type": "object",
      "properties": {
        "duration_seconds": {
          "type": "integer"
        }
      },
      "required": []
    }
  },
  {
    "name": "change_wallpaper",
    "description": "Change desktop wallpaper by topic query (e.g. Iron Man 4k, cyberpunk city, anime, nature), image URL, or local file path. Blank selects curated 4K wallpaper.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Topic, theme, or character for the wallpaper (e.g. 'Iron Man 4k', 'cyberpunk', 'mountains sunset')"
        },
        "image_path": {
          "type": "string",
          "description": "Optional direct local file path or image URL"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_open_windows",
    "description": "Sab open windows ki list",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "manage_window",
    "description": "Window manage karo: activate, minimize, maximize, restore, close",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "action": {
          "type": "string"
        }
      },
      "required": [
        "title",
        "action"
      ]
    }
  },
  {
    "name": "start_security_mode",
    "description": "Security/motion detection mode shuru karo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "stop_security_mode",
    "description": "Security mode band karo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "clean_system",
    "description": "Temp files aur junk saaf karo",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "read_pdf",
    "description": "PDF file padho",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string"
        }
      },
      "required": [
        "file_path"
      ]
    }
  },
  {
    "name": "merge_pdfs",
    "description": "Ek folder ke sab PDFs merge karo",
    "parameters": {
      "type": "object",
      "properties": {
        "folder": {
          "type": "string"
        },
        "output_name": {
          "type": "string"
        }
      },
      "required": [
        "folder"
      ]
    }
  },
  {
    "name": "images_to_pdf",
    "description": "Images ko PDF mein convert karo",
    "parameters": {
      "type": "object",
      "properties": {
        "folder": {
          "type": "string"
        },
        "output_name": {
          "type": "string"
        }
      },
      "required": [
        "folder"
      ]
    }
  },
  {
    "name": "get_battery_status",
    "description": "Battery level aur charging status dekho",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_system_status",
    "description": "CPU RAM Disk ka system status dekho",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "adjust_brightness",
    "description": "Screen brightness: get/set/increase/decrease",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string"
        },
        "level": {
          "type": "integer"
        }
      },
      "required": []
    }
  },
  {
    "name": "whatsapp_read_last_message",
    "description": "WhatsApp ka last message padho",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "whatsapp_send_message",
    "description": "WhatsApp pe message bhejo — contact naam do toh search karega in english text",
    "parameters": {
      "type": "object",
      "properties": {
        "message": {
          "type": "string"
        },
        "contact": {
          "type": "string"
        }
      },
      "required": [
        "message"
      ]
    }
  },
  {
    "name": "whatsapp_reply_last",
    "description": "Current WhatsApp chat mein reply karo",
    "parameters": {
      "type": "object",
      "properties": {
        "reply": {
          "type": "string"
        }
      },
      "required": [
        "reply"
      ]
    }
  },
  {
    "name": "whatsapp_wait_for_reply",
    "description": "WhatsApp mein naya message aane ka wait karo",
    "parameters": {
      "type": "object",
      "properties": {
        "wait_seconds": {
          "type": "integer"
        }
      },
      "required": []
    }
  },
  {
    "name": "whatsapp_open_chat",
    "description": "WhatsApp mein contact ka chat kholo",
    "parameters": {
      "type": "object",
      "properties": {
        "contact": {
          "type": "string"
        }
      },
      "required": [
        "contact"
      ]
    }
  },
  {
    "name": "write_code",
    "description": "Koi bhi code likho (Python/JS/HTML/batch etc) aur VS Code ya Notepad mein kholo. User jo bhi banane ko bole — login page, calculator, game, tool — seedha file mein likh ke run karo.",
    "parameters": {
      "type": "object",
      "properties": {
        "code": {
          "type": "string"
        },
        "language": {
          "type": "string"
        },
        "filename": {
          "type": "string"
        },
        "run_after": {
          "type": "boolean"
        },
        "open_editor": {
          "type": "boolean"
        }
      },
      "required": [
        "code"
      ]
    }
  },
  {
    "name": "run_code_file",
    "description": "Pehle se save ki hui code file run karo",
    "parameters": {
      "type": "object",
      "properties": {
        "filename": {
          "type": "string"
        }
      },
      "required": [
        "filename"
      ]
    }
  },
  {
    "name": "read_screen",
    "description": "Screen pe jo kuch bhi dikh raha hai uska text padho — kisi bhi app ka content, error message, webpage text. region: full/top/bottom/left/right/center",
    "parameters": {
      "type": "object",
      "properties": {
        "region": {
          "type": "string"
        }
      },
      "required": []
    }
  },
  {
    "name": "read_active_window",
    "description": "Jo window abhi active/foreground mein hai uska title aur content padho",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "switch_tab",
    "description": "Instantly switches browser, editor, or application tabs (<10ms). Call this whenever the user asks to switch tab, next tab, previous tab, or go to tab 1-9.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "direction": {
          "type": "STRING",
          "description": "'next' for next tab, 'previous' or 'prev' for previous tab, or a number 1-9 for specific tab index."
        }
      },
      "required": []
    }
  },
  {
    "name": "new_tab",
    "description": "Opens a new browser tab (Ctrl+T) and navigates to the URL if provided.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "Optional website URL to navigate to in the new tab."
        }
      },
      "required": []
    }
  },
  {
    "name": "close_tab",
    "description": "Instantly closes the current active browser or application tab (Ctrl+W).",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "mouse_click",
    "description": "Clicks the mouse. Can click at current position or at specific screen coordinates (x, y). Button can be 'left', 'right', 'double', or 'middle'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "button": {
          "type": "STRING",
          "description": "Mouse button: 'left', 'right', 'double', 'middle'. Defaults to 'left'."
        },
        "clicks": {
          "type": "INTEGER",
          "description": "Number of clicks: 1 for single click, 2 for double click."
        },
        "x": {
          "type": "INTEGER",
          "description": "Optional X coordinate on screen to move to before clicking."
        },
        "y": {
          "type": "INTEGER",
          "description": "Optional Y coordinate on screen to move to before clicking."
        }
      },
      "required": []
    }
  },
  {
    "name": "mouse_move",
    "description": "Moves the mouse cursor to specific screen coordinates (x, y).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "x": {
          "type": "INTEGER",
          "description": "Target X screen coordinate in pixels."
        },
        "y": {
          "type": "INTEGER",
          "description": "Target Y screen coordinate in pixels."
        }
      },
      "required": [
        "x",
        "y"
      ]
    }
  },
  {
    "name": "mouse_scroll",
    "description": "Scrolls the mouse wheel up or down. Positive amount scrolls UP, negative scrolls DOWN (e.g. -300 to scroll down).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "amount": {
          "type": "INTEGER",
          "description": "Scroll delta (e.g. -300 for down, 300 for up)."
        }
      },
      "required": [
        "amount"
      ]
    }
  },
  {
    "name": "keyboard_type",
    "description": "Types text into the active window or input field with exact spelling and zero mistakes.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "text": {
          "type": "STRING",
          "description": "The exact string of text to type or paste into the active field."
        }
      },
      "required": [
        "text"
      ]
    }
  },
  {
    "name": "keyboard_press",
    "description": "Presses a single key on the keyboard: 'enter', 'tab', 'esc', 'space', 'backspace', 'delete', 'f5', 'up', 'down', 'left', 'right', 'win'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "key": {
          "type": "STRING",
          "description": "Key name to press, e.g. 'enter', 'esc', 'space', 'tab', 'backspace'."
        }
      },
      "required": [
        "key"
      ]
    }
  },
  {
    "name": "keyboard_hotkey",
    "description": "Executes keyboard shortcut combination: 'ctrl,c', 'ctrl,v', 'ctrl,t', 'ctrl,w', 'alt,tab', 'win,d', 'ctrl,shift,esc', 'alt,f4'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "keys": {
          "type": "STRING",
          "description": "Comma-separated keys, e.g. 'ctrl,c' or 'win,d' or 'alt,tab'."
        }
      },
      "required": [
        "keys"
      ]
    }
  },
  {
    "name": "control_screen",
    "description": "Controls desktop screen state: 'minimize_all' (show desktop), 'maximize', 'minimize', 'restore', 'snap_left', 'snap_right', 'lock', 'task_manager', 'switch_window'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "'minimize_all' / 'show_desktop', 'maximize', 'minimize', 'snap_left', 'snap_right', 'lock', 'task_manager', 'switch_window'."
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "add_to_logs",
    "description": "Appends a timestamped memory to the logs in ultron_memory.json.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "content": {
          "type": "STRING",
          "description": "Parameter content"
        }
      },
      "required": [
        "content"
      ]
    }
  },
  {
    "name": "auto_detect_and_store",
    "description": "Automatically detects important info in user messages and stores it in ultron_memory.json.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "message": {
          "type": "STRING",
          "description": "Parameter message"
        }
      },
      "required": [
        "message"
      ]
    }
  },
  {
    "name": "battery_status",
    "description": "Ultron capability: battery_status",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "check_internet",
    "description": "Ultron capability: check_internet",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "clear_old_logs",
    "description": "Removes log entries older than the specified number of days from ultron_memory.json.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "days_old": {
          "type": "INTEGER",
          "description": "Parameter days_old"
        }
      },
      "required": []
    }
  },
  {
    "name": "current_time",
    "description": "Ultron capability: current_time",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "delete_contact",
    "description": "Deletes a contact.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "name": {
          "type": "STRING",
          "description": "Parameter name"
        }
      },
      "required": [
        "name"
      ]
    }
  },
  {
    "name": "delete_log",
    "description": "Removes a specific log entry from ultron_memory.json by matching its content.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "search_text": {
          "type": "STRING",
          "description": "Parameter search_text"
        }
      },
      "required": [
        "search_text"
      ]
    }
  },
  {
    "name": "forget",
    "description": "Removes a specific fact from ULTRON's memory (ultron_memory.json kv store).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "key": {
          "type": "STRING",
          "description": "Parameter key"
        }
      },
      "required": [
        "key"
      ]
    }
  },
  {
    "name": "get_contact_phone",
    "description": "Retrieves a phone number for a contact by name.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "name": {
          "type": "STRING",
          "description": "Parameter name"
        }
      },
      "required": [
        "name"
      ]
    }
  },
  {
    "name": "get_weather",
    "description": "Ultron capability: get_weather",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "city": {
          "type": "STRING",
          "description": "Parameter city"
        }
      },
      "required": [
        "city"
      ]
    }
  },
  {
    "name": "google_custom_search",
    "description": "Performs a Google Search using the Google Search API key.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "list_all_contacts",
    "description": "Lists all saved contacts.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "load_memory",
    "description": "Ultron capability: load_memory",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "publish_to_sandbox",
    "description": "Publishes the current application state to the LiveKit sandbox friday-ak3nk6.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "recall",
    "description": "Recalls a specific piece of knowledge by key from ultron_memory.json.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "key": {
          "type": "STRING",
          "description": "Parameter key"
        }
      },
      "required": [
        "key"
      ]
    }
  },
  {
    "name": "remember",
    "description": "Saves a key-value fact to ULTRON's brain (ultron_memory.json). Use this to store any important information.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "key": {
          "type": "STRING",
          "description": "Parameter key"
        },
        "value": {
          "type": "STRING",
          "description": "Parameter value"
        }
      },
      "required": [
        "key",
        "value"
      ]
    }
  },
  {
    "name": "save_contact",
    "description": "Saves a contact with their phone number.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "name": {
          "type": "STRING",
          "description": "Parameter name"
        },
        "phone": {
          "type": "STRING",
          "description": "Parameter phone"
        },
        "notes": {
          "type": "STRING",
          "description": "Parameter notes"
        }
      },
      "required": [
        "name",
        "phone"
      ]
    }
  },
  {
    "name": "save_memory",
    "description": "Ultron capability: save_memory",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "data": {
          "type": "STRING",
          "description": "Parameter data"
        }
      },
      "required": [
        "data"
      ]
    }
  },
  {
    "name": "search_contacts",
    "description": "Searches contacts.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "search_memory",
    "description": "Searches both KV and logs for relevant information.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        },
        "limit": {
          "type": "INTEGER",
          "description": "Parameter limit"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "search_web",
    "description": "Ultron capability: search_web",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "system_health_report",
    "description": "Ultron capability: system_health_report",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "system_status",
    "description": "Ultron capability: system_status",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "system_uptime",
    "description": "Ultron capability: system_uptime",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "track_active_application",
    "description": "Ultron capability: track_active_application",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "update_memory",
    "description": "Updates an existing memory in ultron_memory.json. If it doesn't exist, creates it.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "key": {
          "type": "STRING",
          "description": "Parameter key"
        },
        "new_value": {
          "type": "STRING",
          "description": "Parameter new_value"
        }
      },
      "required": [
        "key",
        "new_value"
      ]
    }
  },
  {
    "name": "view_brain",
    "description": "Shows all of ULTRON's memories from ultron_memory.json (both facts and event logs).",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "weekly_app_usage_report",
    "description": "Ultron capability: weekly_app_usage_report",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "create_file",
    "description": "Ultron capability: create_file",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        },
        "content": {
          "type": "STRING",
          "description": "Parameter content"
        }
      },
      "required": [
        "path"
      ]
    }
  },
  {
    "name": "create_folder",
    "description": "Ultron capability: create_folder",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": [
        "path"
      ]
    }
  },
  {
    "name": "create_project_files",
    "description": "Creates multiple files in a directory. useful for saving generated code projects.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "base_path": {
          "type": "STRING",
          "description": "Parameter base_path"
        },
        "files": {
          "type": "STRING",
          "description": "Parameter files"
        }
      },
      "required": [
        "base_path",
        "files"
      ]
    }
  },
  {
    "name": "delete_file",
    "description": "Ultron capability: delete_file",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": [
        "path"
      ]
    }
  },
  {
    "name": "disk_usage",
    "description": "Ultron capability: disk_usage",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": []
    }
  },
  {
    "name": "list_directory",
    "description": "Ultron capability: list_directory",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": []
    }
  },
  {
    "name": "read_file",
    "description": "Ultron capability: read_file",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": [
        "path"
      ]
    }
  },
  {
    "name": "rename_file",
    "description": "Ultron capability: rename_file",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "old_path": {
          "type": "STRING",
          "description": "Parameter old_path"
        },
        "new_path": {
          "type": "STRING",
          "description": "Parameter new_path"
        }
      },
      "required": [
        "old_path",
        "new_path"
      ]
    }
  },
  {
    "name": "close_active_window",
    "description": "Ultron capability: close_active_window",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "control_bluetooth",
    "description": "Ultron capability: control_bluetooth",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        },
        "device_name": {
          "type": "STRING",
          "description": "Parameter device_name"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "control_windows_settings",
    "description": "Ultron capability: control_windows_settings",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "page": {
          "type": "STRING",
          "description": "Parameter page"
        },
        "toggle": {
          "type": "STRING",
          "description": "Parameter toggle"
        }
      },
      "required": [
        "page"
      ]
    }
  },
  {
    "name": "copy_to_clipboard",
    "description": "Ultron capability: copy_to_clipboard",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "text": {
          "type": "STRING",
          "description": "Parameter text"
        }
      },
      "required": [
        "text"
      ]
    }
  },
  {
    "name": "execute_cmd",
    "description": "Ultron capability: execute_cmd",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "command": {
          "type": "STRING",
          "description": "Parameter command"
        }
      },
      "required": [
        "command"
      ]
    }
  },
  {
    "name": "execute_powershell",
    "description": "Ultron capability: execute_powershell",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "command": {
          "type": "STRING",
          "description": "Parameter command"
        }
      },
      "required": [
        "command"
      ]
    }
  },
  {
    "name": "get_active_window",
    "description": "Ultron capability: get_active_window",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "hibernate_system",
    "description": "Ultron capability: hibernate_system",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "keyboard_mouse_control",
    "description": "Controls keyboard and mouse with high reliability on Windows.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        },
        "value": {
          "type": "STRING",
          "description": "Parameter value"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "lock_system",
    "description": "Ultron capability: lock_system",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "login_with_gmail",
    "description": "Automates the 'Sign in with Google' sequence for a specified website.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "website": {
          "type": "STRING",
          "description": "Parameter website"
        }
      },
      "required": [
        "website"
      ]
    }
  },
  {
    "name": "maximize_window",
    "description": "Ultron capability: maximize_window",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "minimize_window",
    "description": "Ultron capability: minimize_window",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "open_clipboard_history",
    "description": "Ultron capability: open_clipboard_history",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "open_file_or_folder",
    "description": "Ultron capability: open_file_or_folder",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": [
        "path"
      ]
    }
  },
  {
    "name": "open_website_or_app",
    "description": "Ultron capability: open_website_or_app",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "play_game_pc",
    "description": "Autonomous PC Gaming: ULTRON takes control of a PC game for the specified duration.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "game_name": {
          "type": "STRING",
          "description": "Parameter game_name"
        },
        "duration_minutes": {
          "type": "INTEGER",
          "description": "Parameter duration_minutes"
        }
      },
      "required": [
        "game_name"
      ]
    }
  },
  {
    "name": "read_clipboard",
    "description": "Ultron capability: read_clipboard",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "restart_system",
    "description": "Ultron capability: restart_system",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "run_command",
    "description": "Ultron capability: run_command",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "command": {
          "type": "STRING",
          "description": "Parameter command"
        }
      },
      "required": [
        "command"
      ]
    }
  },
  {
    "name": "running_processes",
    "description": "Ultron capability: running_processes",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "schedule_task",
    "description": "Ultron capability: schedule_task",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task_name": {
          "type": "STRING",
          "description": "Parameter task_name"
        },
        "command": {
          "type": "STRING",
          "description": "Parameter command"
        },
        "time": {
          "type": "STRING",
          "description": "Parameter time"
        }
      },
      "required": [
        "task_name",
        "command",
        "time"
      ]
    }
  },
  {
    "name": "set_brightness",
    "description": "Ultron capability: set_brightness",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "level": {
          "type": "INTEGER",
          "description": "Parameter level"
        }
      },
      "required": [
        "level"
      ]
    }
  },
  {
    "name": "show_notification",
    "description": "Ultron capability: show_notification",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "title": {
          "type": "STRING",
          "description": "Parameter title"
        },
        "message": {
          "type": "STRING",
          "description": "Parameter message"
        }
      },
      "required": [
        "title",
        "message"
      ]
    }
  },
  {
    "name": "shutdown_system",
    "description": "Ultron capability: shutdown_system",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "sleep_system",
    "description": "Ultron capability: sleep_system",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "switch_window",
    "description": "Ultron capability: switch_window",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "volume_control",
    "description": "Ultron capability: volume_control",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "level": {
          "type": "INTEGER",
          "description": "Parameter level"
        }
      },
      "required": [
        "level"
      ]
    }
  },
  {
    "name": "access_network_share",
    "description": "Ultron capability: access_network_share",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "share_name": {
          "type": "STRING",
          "description": "Parameter share_name"
        }
      },
      "required": [
        "ip_address",
        "share_name"
      ]
    }
  },
  {
    "name": "check_admin_privileges",
    "description": "Ultron capability: check_admin_privileges",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "connect_wifi",
    "description": "Ultron capability: connect_wifi",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ssid": {
          "type": "STRING",
          "description": "Parameter ssid"
        }
      },
      "required": [
        "ssid"
      ]
    }
  },
  {
    "name": "control_network_adapter",
    "description": "Ultron capability: control_network_adapter",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "disconnect_device_from_internet",
    "description": "Ultron capability: disconnect_device_from_internet",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "mac_address": {
          "type": "STRING",
          "description": "Parameter mac_address"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "disconnect_network_drive",
    "description": "Ultron capability: disconnect_network_drive",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "drive_letter": {
          "type": "STRING",
          "description": "Parameter drive_letter"
        }
      },
      "required": [
        "drive_letter"
      ]
    }
  },
  {
    "name": "disconnect_wifi",
    "description": "Ultron capability: disconnect_wifi",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "enable_packet_forwarding",
    "description": "Ultron capability: enable_packet_forwarding",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "execute_remote_command",
    "description": "Attempts to execute a command on a remote Windows machine using PowerShell Remoting.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "command": {
          "type": "STRING",
          "description": "Parameter command"
        },
        "username": {
          "type": "STRING",
          "description": "Parameter username"
        },
        "password": {
          "type": "STRING",
          "description": "Parameter password"
        }
      },
      "required": [
        "ip_address",
        "command"
      ]
    }
  },
  {
    "name": "flush_dns",
    "description": "Ultron capability: flush_dns",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_active_connections",
    "description": "Ultron capability: get_active_connections",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_detailed_network_info",
    "description": "Ultron capability: get_detailed_network_info",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_device_services",
    "description": "Ultron capability: get_device_services",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "get_network_devices_with_names",
    "description": "Ultron capability: get_network_devices_with_names",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_network_speed",
    "description": "Ultron capability: get_network_speed",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_remote_device_info",
    "description": "Ultron capability: get_remote_device_info",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "get_router_admin_page",
    "description": "Ultron capability: get_router_admin_page",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_router_info",
    "description": "Ultron capability: get_router_info",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_saved_wifi_passwords",
    "description": "Ultron capability: get_saved_wifi_passwords",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "ip_information",
    "description": "Ultron capability: ip_information",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "limit_device_bandwidth",
    "description": "Ultron capability: limit_device_bandwidth",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "limit_kbps": {
          "type": "INTEGER",
          "description": "Parameter limit_kbps"
        }
      },
      "required": [
        "ip_address",
        "limit_kbps"
      ]
    }
  },
  {
    "name": "list_network_shares",
    "description": "Ultron capability: list_network_shares",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        }
      },
      "required": []
    }
  },
  {
    "name": "list_wifi_networks",
    "description": "Ultron capability: list_wifi_networks",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "map_network_drive",
    "description": "Ultron capability: map_network_drive",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "drive_letter": {
          "type": "STRING",
          "description": "Parameter drive_letter"
        },
        "network_path": {
          "type": "STRING",
          "description": "Parameter network_path"
        }
      },
      "required": [
        "drive_letter",
        "network_path"
      ]
    }
  },
  {
    "name": "monitor_network_traffic",
    "description": "Ultron capability: monitor_network_traffic",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration_seconds": {
          "type": "INTEGER",
          "description": "Parameter duration_seconds"
        }
      },
      "required": []
    }
  },
  {
    "name": "network_bandwidth_usage",
    "description": "Ultron capability: network_bandwidth_usage",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "network_kill_switch",
    "description": "Ultron capability: network_kill_switch",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "ping_device",
    "description": "Ultron capability: ping_device",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "Parameter target"
        }
      },
      "required": [
        "target"
      ]
    }
  },
  {
    "name": "port_scan",
    "description": "Ultron capability: port_scan",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "ports": {
          "type": "STRING",
          "description": "Parameter ports"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "reconnect_device_to_internet",
    "description": "Ultron capability: reconnect_device_to_internet",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "mac_address": {
          "type": "STRING",
          "description": "Parameter mac_address"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "remote_desktop_connect",
    "description": "Ultron capability: remote_desktop_connect",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "username": {
          "type": "STRING",
          "description": "Parameter username"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "remote_file_copy",
    "description": "Ultron capability: remote_file_copy",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "local_file": {
          "type": "STRING",
          "description": "Parameter local_file"
        },
        "remote_ip": {
          "type": "STRING",
          "description": "Parameter remote_ip"
        },
        "remote_path": {
          "type": "STRING",
          "description": "Parameter remote_path"
        }
      },
      "required": [
        "local_file",
        "remote_ip",
        "remote_path"
      ]
    }
  },
  {
    "name": "remote_restart",
    "description": "Ultron capability: remote_restart",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "username": {
          "type": "STRING",
          "description": "Parameter username"
        },
        "password": {
          "type": "STRING",
          "description": "Parameter password"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "remote_shutdown",
    "description": "Ultron capability: remote_shutdown",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "username": {
          "type": "STRING",
          "description": "Parameter username"
        },
        "password": {
          "type": "STRING",
          "description": "Parameter password"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "remove_bandwidth_limit",
    "description": "Ultron capability: remove_bandwidth_limit",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        }
      },
      "required": [
        "ip_address"
      ]
    }
  },
  {
    "name": "remove_network_share",
    "description": "Ultron capability: remove_network_share",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "share_name": {
          "type": "STRING",
          "description": "Parameter share_name"
        }
      },
      "required": [
        "share_name"
      ]
    }
  },
  {
    "name": "renew_ip_address",
    "description": "Ultron capability: renew_ip_address",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "scan_network_devices",
    "description": "Ultron capability: scan_network_devices",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "send_network_message",
    "description": "Ultron capability: send_network_message",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_address": {
          "type": "STRING",
          "description": "Parameter ip_address"
        },
        "message": {
          "type": "STRING",
          "description": "Parameter message"
        }
      },
      "required": [
        "ip_address",
        "message"
      ]
    }
  },
  {
    "name": "share_folder_on_network",
    "description": "Ultron capability: share_folder_on_network",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "folder_path": {
          "type": "STRING",
          "description": "Parameter folder_path"
        },
        "share_name": {
          "type": "STRING",
          "description": "Parameter share_name"
        }
      },
      "required": [
        "folder_path",
        "share_name"
      ]
    }
  },
  {
    "name": "trace_route",
    "description": "Ultron capability: trace_route",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "Parameter target"
        }
      },
      "required": [
        "target"
      ]
    }
  },
  {
    "name": "wake_on_lan",
    "description": "Ultron capability: wake_on_lan",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mac_address": {
          "type": "STRING",
          "description": "Parameter mac_address"
        }
      },
      "required": [
        "mac_address"
      ]
    }
  },
  {
    "name": "analyze_screen_content",
    "description": "Takes a screenshot and analyzes screen content using Ultron Vision.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": {
          "type": "STRING",
          "description": "Parameter prompt"
        }
      },
      "required": []
    }
  },
  {
    "name": "generate_image",
    "description": "Generates a high-definition AI image for FREE using Pollinations AI Engine.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": {
          "type": "STRING",
          "description": "Parameter prompt"
        },
        "style": {
          "type": "STRING",
          "description": "Parameter style"
        },
        "save_folder": {
          "type": "STRING",
          "description": "Parameter save_folder"
        }
      },
      "required": [
        "prompt"
      ]
    }
  },
  {
    "name": "get_youtube_subscribers",
    "description": "Ultron capability: get_youtube_subscribers",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "channel_name": {
          "type": "STRING",
          "description": "Parameter channel_name"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_youtube_video_link",
    "description": "Searches YouTube and returns only the link of the first result.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "open_youtube_studio",
    "description": "Ultron capability: open_youtube_studio",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        }
      },
      "required": []
    }
  },
  {
    "name": "play_music",
    "description": "Ultron capability: play_music",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "song": {
          "type": "STRING",
          "description": "Parameter song"
        }
      },
      "required": [
        "song"
      ]
    }
  },
  {
    "name": "select_video_by_index",
    "description": "Ultron capability: select_video_by_index",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "index": {
          "type": "INTEGER",
          "description": "Parameter index"
        }
      },
      "required": [
        "index"
      ]
    }
  },
  {
    "name": "click_youtube_video",
    "description": "Clicks on a specific YouTube video from search results on screen (e.g. 1st, 2nd, 3rd video).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "video_index": {
          "type": "INTEGER",
          "description": "The 1-based index of the video to click (e.g. 1 for first, 2 for second, 3 for third)"
        }
      },
      "required": [
        "video_index"
      ]
    }
  },
  {
    "name": "share_youtube_video_background",
    "description": "Searches for a YouTube video and shares the link via WhatsApp in the background.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        },
        "phone": {
          "type": "STRING",
          "description": "Parameter phone"
        }
      },
      "required": [
        "query",
        "phone"
      ]
    }
  },
  {
    "name": "youtube_search_results",
    "description": "Ultron capability: youtube_search_results",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "adb_cmd",
    "description": "Ultron capability: adb_cmd",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "cmd_list": {
          "type": "STRING",
          "description": "Parameter cmd_list"
        }
      },
      "required": [
        "cmd_list"
      ]
    }
  },
  {
    "name": "check_gmail_for_otp",
    "description": "Scans the inbox for latest emails containing 'OTP' or 'verification code'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "common_phone_location_tracker",
    "description": "Ultron capability: common_phone_location_tracker",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone_number": {
          "type": "STRING",
          "description": "Parameter phone_number"
        }
      },
      "required": [
        "phone_number"
      ]
    }
  },
  {
    "name": "get_email_count",
    "description": "Ultron capability: get_email_count",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "folder": {
          "type": "STRING",
          "description": "Parameter folder"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_latest_call_info",
    "description": "Ultron capability: get_latest_call_info",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_recent_email_senders",
    "description": "Ultron capability: get_recent_email_senders",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "count": {
          "type": "INTEGER",
          "description": "Parameter count"
        }
      },
      "required": []
    }
  },
  {
    "name": "google_duo_call",
    "description": "Ultron capability: google_duo_call",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "contact": {
          "type": "STRING",
          "description": "Parameter contact"
        }
      },
      "required": [
        "contact"
      ]
    }
  },
  {
    "name": "make_phone_call",
    "description": "Initiates a real phone call via ADB.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone_number": {
          "type": "STRING",
          "description": "Parameter phone_number"
        }
      },
      "required": [
        "phone_number"
      ]
    }
  },
  {
    "name": "manage_google_account",
    "description": "Safely manage Google account tasks.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        },
        "account_index": {
          "type": "INTEGER",
          "description": "Parameter account_index"
        },
        "details": {
          "type": "STRING",
          "description": "Parameter details"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "proximal_phone_unlocker",
    "description": "Unlocks phones via Bluetooth/Wi-Fi proximity.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "read_specific_email",
    "description": "Ultron capability: read_specific_email",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "index": {
          "type": "INTEGER",
          "description": "Parameter index"
        }
      },
      "required": []
    }
  },
  {
    "name": "reply_to_latest_email",
    "description": "Ultron capability: reply_to_latest_email",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "reply_text": {
          "type": "STRING",
          "description": "Parameter reply_text"
        }
      },
      "required": [
        "reply_text"
      ]
    }
  },
  {
    "name": "send_email",
    "description": "Ultron capability: send_email",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "to_email": {
          "type": "STRING",
          "description": "Parameter to_email"
        },
        "subject": {
          "type": "STRING",
          "description": "Parameter subject"
        },
        "message": {
          "type": "STRING",
          "description": "Parameter message"
        }
      },
      "required": [
        "to_email",
        "subject",
        "message"
      ]
    }
  },
  {
    "name": "send_whatsapp_image",
    "description": "Sends an image via WhatsApp using ADB.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone": {
          "type": "STRING",
          "description": "Parameter phone"
        },
        "image_path": {
          "type": "STRING",
          "description": "Parameter image_path"
        },
        "message": {
          "type": "STRING",
          "description": "Parameter message"
        }
      },
      "required": [
        "phone",
        "image_path"
      ]
    }
  },
  {
    "name": "send_whatsapp_message",
    "description": "Sends a WhatsApp message. Accepts a phone number (e.g. '9805321926') OR a contact name (e.g. 'Mom', 'Papa', 'Rohan'). Automatically resolves contact, opens chat, and sends the message.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone": {
          "type": "STRING",
          "description": "Phone number or contact name (e.g. '9805321926', 'Papa', 'Mummy')"
        },
        "message": {
          "type": "STRING",
          "description": "The message text to send"
        }
      },
      "required": [
        "phone",
        "message"
      ]
    }
  },
  {
    "name": "send_whatsapp_to_contact",
    "description": "Searches for a contact by name in WhatsApp, navigates to select the chat, and sends the message.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "contact_name": {
          "type": "STRING",
          "description": "Name of the WhatsApp contact (e.g. 'Mummy', 'Papa', 'Rohan')"
        },
        "message": {
          "type": "STRING",
          "description": "The message text to send"
        }
      },
      "required": [
        "contact_name",
        "message"
      ]
    }
  },
  {
    "name": "send_whatsapp_to_group",
    "description": "Searches for a WhatsApp group by name, navigates to select the group chat, and sends the message.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "group_name": {
          "type": "STRING",
          "description": "Exact name of the WhatsApp group"
        },
        "message": {
          "type": "STRING",
          "description": "The message text to send"
        }
      },
      "required": [
        "group_name",
        "message"
      ]
    }
  },
  {
    "name": "send_whatsapp_message_background",
    "description": "Sends a WhatsApp message directly via ADB without using the PC browser.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone": {
          "type": "STRING",
          "description": "Parameter phone"
        },
        "message": {
          "type": "STRING",
          "description": "Parameter message"
        }
      },
      "required": [
        "phone",
        "message"
      ]
    }
  },
  {
    "name": "start_google_meet",
    "description": "Ultron capability: start_google_meet",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "track_phone_number",
    "description": "Ultron capability: track_phone_number",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone_number": {
          "type": "STRING",
          "description": "Parameter phone_number"
        }
      },
      "required": [
        "phone_number"
      ]
    }
  },
  {
    "name": "universal_phone_unlocker",
    "description": "Advanced Android Unlocker.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "STRING",
          "description": "Parameter pin"
        }
      },
      "required": []
    }
  },
  {
    "name": "whatsapp_call",
    "description": "Ultron capability: whatsapp_call",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone": {
          "type": "STRING",
          "description": "Parameter phone"
        },
        "call_type": {
          "type": "STRING",
          "description": "Parameter call_type"
        }
      },
      "required": [
        "phone"
      ]
    }
  },
  {
    "name": "arp_poison_router_attack",
    "description": "Executes a real ARP spoofing attack between a target host and the gateway.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_ip": {
          "type": "STRING",
          "description": "Parameter target_ip"
        },
        "gateway_ip": {
          "type": "STRING",
          "description": "Parameter gateway_ip"
        }
      },
      "required": [
        "target_ip",
        "gateway_ip"
      ]
    }
  },
  {
    "name": "decrypt_payload",
    "description": "Ultron capability: decrypt_payload",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "cipher": {
          "type": "STRING",
          "description": "Parameter cipher"
        },
        "payload": {
          "type": "STRING",
          "description": "Parameter payload"
        }
      },
      "required": [
        "cipher",
        "payload"
      ]
    }
  },
  {
    "name": "defense_protocol_alpha",
    "description": "Executes a real system lockdown: locks workstation, kills non-essential networking and minimizes all windows.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "dns_spoofing_attack",
    "description": "Intercepts real DNS queries for a domain and injects forged redirect responses.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "domain_to_spoof": {
          "type": "STRING",
          "description": "Parameter domain_to_spoof"
        },
        "redirect_ip": {
          "type": "STRING",
          "description": "Parameter redirect_ip"
        }
      },
      "required": [
        "domain_to_spoof",
        "redirect_ip"
      ]
    }
  },
  {
    "name": "extract_browser_passwords",
    "description": "Accesses Chrome's Login Data database, retrieves the master key via DPAPI, ",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "generate_intelligence_briefing",
    "description": "Synthesizes a real multi-source intelligence briefing using the GenAI core.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "topic": {
          "type": "STRING",
          "description": "Parameter topic"
        }
      },
      "required": [
        "topic"
      ]
    }
  },
  {
    "name": "generate_phone_location_map",
    "description": "Advanced Phone Tracker: Identifies carrier, region, and real-time estimated geolocation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone_number": {
          "type": "STRING",
          "description": "Parameter phone_number"
        }
      },
      "required": [
        "phone_number"
      ]
    }
  },
  {
    "name": "get_chrome_key",
    "description": "Ultron capability: get_chrome_key",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_exact_location_via_adb",
    "description": "Pulls real-time GPS coordinates directly from the connected Android device via ADB positioning services.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "identify_object_from_camera",
    "description": "Captures a camera frame and performs instant visual identification.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": {
          "type": "STRING",
          "description": "Parameter prompt"
        }
      },
      "required": []
    }
  },
  {
    "name": "local_network_brute_force",
    "description": "Attempts a real credential verification against a target IP (e.g., SMB/FTP/SSH).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_ip": {
          "type": "STRING",
          "description": "Parameter target_ip"
        }
      },
      "required": [
        "target_ip"
      ]
    }
  },
  {
    "name": "metasploit_demo_console",
    "description": "Executes real commands through the local Metasploit RPC or CLI if installed.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "command": {
          "type": "STRING",
          "description": "Parameter command"
        }
      },
      "required": []
    }
  },
  {
    "name": "perform_signal_intelligence_scan",
    "description": "Scans real Wi-Fi and Bluetooth signals to identify nearby hardware entities.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration": {
          "type": "INTEGER",
          "description": "Parameter duration"
        }
      },
      "required": []
    }
  },
  {
    "name": "play_chess_move_autonomously",
    "description": "Uses a real chess engine (Stockfish-lite) to calculate the best legal move.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "fen": {
          "type": "STRING",
          "description": "Parameter fen"
        }
      },
      "required": []
    }
  },
  {
    "name": "satellite_recon",
    "description": "Deploys real-time satellite visualization via the high-resolution mapping system.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "location": {
          "type": "STRING",
          "description": "Parameter location"
        }
      },
      "required": [
        "location"
      ]
    }
  },
  {
    "name": "smb_eternalblue_scan",
    "description": "Sends a real MS17-010 (EternalBlue) probe to a target IP and checks for transaction error.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_ip": {
          "type": "STRING",
          "description": "Parameter target_ip"
        }
      },
      "required": [
        "target_ip"
      ]
    }
  },
  {
    "name": "sniff_network_packets",
    "description": "Uses Scapy to capture and analyze real network traffic on the host interface.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration": {
          "type": "INTEGER",
          "description": "Parameter duration"
        }
      },
      "required": []
    }
  },
  {
    "name": "stealth_microphone_record",
    "description": "Captures real audio from the system microphone and saves it as an encrypted-ready WAV file.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration": {
          "type": "INTEGER",
          "description": "Parameter duration"
        }
      },
      "required": []
    }
  },
  {
    "name": "summarize_website",
    "description": "Downloads raw HTML from a website and uses LLM to generate a real intelligence summary.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "Parameter url"
        }
      },
      "required": [
        "url"
      ]
    }
  },
  {
    "name": "system_rootkit_scan",
    "description": "Performs a real integrity check by comparing logical process lists ",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "vulnerability_scanner",
    "description": "Performs a real TCP port scan on the target system.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "Parameter target"
        }
      },
      "required": [
        "target"
      ]
    }
  },
  {
    "name": "wifi_deauth_attack",
    "description": "Sends raw IEEE 802.11 deauthentication frames to the target BSSID using Scapy.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_bssid": {
          "type": "STRING",
          "description": "Parameter target_bssid"
        }
      },
      "required": [
        "target_bssid"
      ]
    }
  },
  {
    "name": "add_smart_reminder",
    "description": "Sets a reminder for a specific time (HH:MM).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Parameter task"
        },
        "time_at": {
          "type": "STRING",
          "description": "Parameter time_at"
        }
      },
      "required": [
        "task",
        "time_at"
      ]
    }
  },
  {
    "name": "check_and_notify_reminders",
    "description": "Ultron capability: check_and_notify_reminders",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "session": {
          "type": "STRING",
          "description": "Parameter session"
        }
      },
      "required": [
        "session"
      ]
    }
  },
  {
    "name": "disable_focus_mode",
    "description": "Restores the original hosts file to unblock websites.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "enable_focus_mode",
    "description": "Blocks the specified websites by modifying the hosts file.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "websites": {
          "type": "ARRAY",
          "description": "Parameter websites",
          "items": {
            "type": "STRING"
          }
        }
      },
      "required": [
        "websites"
      ]
    }
  },
  {
    "name": "set_alarm",
    "description": "Sets an alarm for a specific time (HH:MM).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "time_at": {
          "type": "STRING",
          "description": "Parameter time_at"
        },
        "task": {
          "type": "STRING",
          "description": "Parameter task"
        }
      },
      "required": [
        "time_at"
      ]
    }
  },
  {
    "name": "activate_stealth_mode",
    "description": "Enables Focus Mode and sets system volume to zero for 'Stealth'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "holographic_threat_assessment",
    "description": "Simulates a high-level tactical scan of the network/environment to identify 'threats'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "Parameter target"
        }
      },
      "required": []
    }
  },
  {
    "name": "house_party_protocol",
    "description": "Emergency protocol: Minimizes all windows, stops non-essential media, and locks the system.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "locate_avenger_base",
    "description": "Finds geographic coordinates and maps a simulated 'Avenger' base.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "base_name": {
          "type": "STRING",
          "description": "Parameter base_name"
        }
      },
      "required": []
    }
  },
  {
    "name": "suit_integrity_diagnostics",
    "description": "Performs a deep scan of the 'Mark' system (Local Machine), checking CPU, RAM, and Power.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "github_create_repository",
    "description": "Creates a new repository on GitHub.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "name": {
          "type": "STRING",
          "description": "Parameter name"
        },
        "description": {
          "type": "STRING",
          "description": "Parameter description"
        },
        "private": {
          "type": "BOOLEAN",
          "description": "Parameter private"
        }
      },
      "required": [
        "name"
      ]
    }
  },
  {
    "name": "github_delete_repository",
    "description": "Deletes a repository on GitHub. Requires admin permissions.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "owner": {
          "type": "STRING",
          "description": "Parameter owner"
        },
        "repo_name": {
          "type": "STRING",
          "description": "Parameter repo_name"
        }
      },
      "required": [
        "owner",
        "repo_name"
      ]
    }
  },
  {
    "name": "github_get_repo_count",
    "description": "Returns the total number of repositories for the authenticated user.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "github_get_user_info",
    "description": "Retrieves the authenticated user's information, including account name (login).",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "github_list_repositories",
    "description": "Lists the names of the authenticated user's repositories.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "limit": {
          "type": "INTEGER",
          "description": "Parameter limit"
        }
      },
      "required": []
    }
  },
  {
    "name": "analyze_and_play",
    "description": "Vision-Assisted Gaming: EDITH captures the screen, analyzes the situation, and takes the best action.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "game_name": {
          "type": "STRING",
          "description": "Parameter game_name"
        },
        "goal": {
          "type": "STRING",
          "description": "Parameter goal"
        }
      },
      "required": [
        "game_name",
        "goal"
      ]
    }
  },
  {
    "name": "generate_adb_pairing_qr",
    "description": "Generates a Neural Pairing QR Code for Wireless Debugging.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_phone_battery_and_status",
    "description": "Checks the current battery level and connection health of the phone.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_screen_info_via_adb",
    "description": "Gets screen resolution and current activity for context.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "maintain_247_phone_link",
    "description": "Ensures the phone stays connected 24/7 to EDITH.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip": {
          "type": "STRING",
          "description": "Parameter ip"
        }
      },
      "required": []
    }
  },
  {
    "name": "play_full_game",
    "description": "Autonomous Full Game Play: EDITH takes complete control of the game for a specified duration.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "game_name": {
          "type": "STRING",
          "description": "Parameter game_name"
        },
        "duration_minutes": {
          "type": "INTEGER",
          "description": "Parameter duration_minutes"
        }
      },
      "required": [
        "game_name"
      ]
    }
  },
  {
    "name": "play_game_action",
    "description": "Executes specific ADB actions for game automation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        },
        "params": {
          "type": "STRING",
          "description": "Parameter params"
        }
      },
      "required": [
        "action"
      ]
    }
  },
  {
    "name": "play_game_scenario",
    "description": "Executes advanced game-specific sequences.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "game": {
          "type": "STRING",
          "description": "Parameter game"
        },
        "scenario": {
          "type": "STRING",
          "description": "Parameter scenario"
        }
      },
      "required": [
        "game",
        "scenario"
      ]
    }
  },
  {
    "name": "wireless_adb_connect",
    "description": "Connects to a device via Wireless Debugging (ADB over TCP/IP).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip": {
          "type": "STRING",
          "description": "Parameter ip"
        },
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": [
        "ip"
      ]
    }
  },
  {
    "name": "access_antigravity_neural_link",
    "description": "Opens the direct neural link to the ANTI-GRAVITY Creator (The AI Assistant located on the right).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "objective": {
          "type": "STRING",
          "description": "Parameter objective"
        }
      },
      "required": [
        "objective"
      ]
    }
  },
  {
    "name": "analyze_data_structure",
    "description": "Performs deep analysis on a local data file (JSON, CSV, LOG).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "data_path": {
          "type": "STRING",
          "description": "Parameter data_path"
        },
        "focus": {
          "type": "STRING",
          "description": "Parameter focus"
        }
      },
      "required": [
        "data_path"
      ]
    }
  },
  {
    "name": "deep_intelligence_search",
    "description": "Performs a deep, multi-pass search across global data sources.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "execute_autonomous_chain",
    "description": "Executes a high-level plan by breaking it down into individual tasks.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "plan": {
          "type": "STRING",
          "description": "Parameter plan"
        }
      },
      "required": [
        "plan"
      ]
    }
  },
  {
    "name": "generate_predictive_suggestions",
    "description": "Analyzes memory and usage logs to predict the user's next likely needs.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "local_knowledge_cache",
    "description": "Manages a local offline knowledge base.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Parameter action"
        },
        "topic": {
          "type": "STRING",
          "description": "Parameter topic"
        },
        "content": {
          "type": "STRING",
          "description": "Parameter content"
        }
      },
      "required": [
        "action",
        "topic"
      ]
    }
  },
  {
    "name": "update_edith_logic",
    "description": "Allows the assistant to update its own tool scripts or create new ones.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "script_name": {
          "type": "STRING",
          "description": "Parameter script_name"
        },
        "new_code": {
          "type": "STRING",
          "description": "Parameter new_code"
        }
      },
      "required": [
        "script_name",
        "new_code"
      ]
    }
  },
  {
    "name": "update_ultron_logic",
    "description": "Allows the assistant to update its own tool scripts or create new ones.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "script_name": {
          "type": "STRING",
          "description": "Parameter script_name"
        },
        "new_code": {
          "type": "STRING",
          "description": "Parameter new_code"
        }
      },
      "required": [
        "script_name",
        "new_code"
      ]
    }
  },
  {
    "name": "activate_app_backend",
    "description": "Enables backend features (Database, Auth) for your apps to make them 'Real Apps'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "features": {
          "type": "ARRAY",
          "description": "Parameter features",
          "items": {
            "type": "STRING"
          }
        }
      },
      "required": []
    }
  },
  {
    "name": "build_and_deploy_app",
    "description": "Builds and deploys a modern Web App (React, Next.js, Vite) for free.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "app_id": {
          "type": "STRING",
          "description": "Parameter app_id"
        },
        "source_directory": {
          "type": "STRING",
          "description": "Parameter source_directory"
        },
        "build_command": {
          "type": "STRING",
          "description": "Parameter build_command"
        },
        "output_directory": {
          "type": "STRING",
          "description": "Parameter output_directory"
        }
      },
      "required": [
        "app_id",
        "source_directory"
      ]
    }
  },
  {
    "name": "deploy_to_firebase",
    "description": "Deploys a professionally coded website to Firebase Hosting for free.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "site_id": {
          "type": "STRING",
          "description": "Parameter site_id"
        },
        "html_content": {
          "type": "STRING",
          "description": "Parameter html_content"
        },
        "css_content": {
          "type": "STRING",
          "description": "Parameter css_content"
        },
        "js_content": {
          "type": "STRING",
          "description": "Parameter js_content"
        }
      },
      "required": [
        "site_id",
        "html_content"
      ]
    }
  },
  {
    "name": "get_active_project",
    "description": "Dynamically determines the project to use, ensuring we stay within limits.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "sanitize_id",
    "description": "Sanitizes a string to be used as a Firebase site/project ID.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "id_str": {
          "type": "STRING",
          "description": "Parameter id_str"
        }
      },
      "required": [
        "id_str"
      ]
    }
  },
  {
    "name": "get_fact",
    "description": "Get a saved fact.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "key": {
          "type": "STRING",
          "description": "Parameter key"
        }
      },
      "required": [
        "key"
      ]
    }
  },
  {
    "name": "save_fact",
    "description": "Save a fact about the user.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "key": {
          "type": "STRING",
          "description": "Parameter key"
        },
        "value": {
          "type": "STRING",
          "description": "Parameter value"
        }
      },
      "required": [
        "key",
        "value"
      ]
    }
  },
  {
    "name": "rag_ask_documents",
    "description": "Asks a question across all your indexed documents.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "question": {
          "type": "STRING",
          "description": "Parameter question"
        },
        "folder_path": {
          "type": "STRING",
          "description": "Parameter folder_path"
        }
      },
      "required": [
        "question"
      ]
    }
  },
  {
    "name": "rag_index_file",
    "description": "Indexes a single document (PDF, DOCX, TXT, MD, Code) into Ultron's RAG knowledge base.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Parameter file_path"
        }
      },
      "required": [
        "file_path"
      ]
    }
  },
  {
    "name": "rag_index_folder",
    "description": "Indexes all documents in a folder into Ultron's RAG knowledge base.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "folder_path": {
          "type": "STRING",
          "description": "Parameter folder_path"
        }
      },
      "required": []
    }
  },
  {
    "name": "rag_list_indexed_docs",
    "description": "Lists all files currently indexed in Ultron's RAG knowledge base.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "rag_search_documents",
    "description": "Searches indexed personal documents and returns the top relevant excerpts.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        },
        "top_k": {
          "type": "INTEGER",
          "description": "Parameter top_k"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "generate_speech_audio",
    "description": "Generates a high-quality neural voice audio file (.mp3) from text.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "text": {
          "type": "STRING",
          "description": "Parameter text"
        },
        "output_path": {
          "type": "STRING",
          "description": "Parameter output_path"
        },
        "voice": {
          "type": "STRING",
          "description": "Parameter voice"
        },
        "pitch": {
          "type": "STRING",
          "description": "Parameter pitch"
        }
      },
      "required": [
        "text"
      ]
    }
  },
  {
    "name": "list_neural_voices",
    "description": "Lists the top recommended neural voices for Ultron.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "speak_text",
    "description": "Speaks text aloud using Edge Neural TTS (en-GB-RyanNeural JARVIS style).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "text": {
          "type": "STRING",
          "description": "Parameter text"
        },
        "voice": {
          "type": "STRING",
          "description": "Parameter voice"
        },
        "rate": {
          "type": "STRING",
          "description": "Parameter rate"
        },
        "pitch": {
          "type": "STRING",
          "description": "Parameter pitch"
        }
      },
      "required": [
        "text"
      ]
    }
  },
  {
    "name": "control_brightness",
    "description": "Sets monitor screen brightness (0 to 100%).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "level": {
          "type": "INTEGER",
          "description": "Parameter level"
        }
      },
      "required": [
        "level"
      ]
    }
  },
  {
    "name": "diagnose_slow_pc",
    "description": "Autonomous JARVIS PC Diagnostic: Inspects CPU, RAM, GPU, Disk, and Rogue processes to diagnose slowness.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_battery_status",
    "description": "Returns battery charge percentage, plugged-in status, and remaining runtime.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_cpu_usage",
    "description": "Returns real-time CPU percentage across all cores and load averages.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_disk_usage",
    "description": "Returns disk capacity and free space across all drives.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_gpu_usage",
    "description": "Returns GPU model, VRAM utilization, temperature, and compute load via nvidia-smi / WMI.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_network_status",
    "description": "Returns active network interfaces, IP addresses, and throughput statistics.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_ram_usage",
    "description": "Returns total, used, available RAM and swap memory.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_system_info",
    "description": "Returns complete machine specifications (OS, Architecture, Python, Hostname).",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_temperature",
    "description": "Returns hardware thermal sensor readings.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "list_running_processes",
    "description": "Returns top resource-consuming running processes sorted by RAM/CPU.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "limit": {
          "type": "INTEGER",
          "description": "Parameter limit"
        }
      },
      "required": []
    }
  },
  {
    "name": "lock_pc",
    "description": "Immediately locks the Windows desktop workstation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "restart_pc",
    "description": "Schedules a safe computer restart with a delay in seconds.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "delay_seconds": {
          "type": "INTEGER",
          "description": "Parameter delay_seconds"
        }
      },
      "required": []
    }
  },
  {
    "name": "sleep_pc",
    "description": "Puts the workstation into sleep / standby mode.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "analyze_image",
    "description": "Analyzes an image from disk using multimodal neural vision (Gemini Vision).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "image_path": {
          "type": "STRING",
          "description": "Parameter image_path"
        },
        "prompt": {
          "type": "STRING",
          "description": "Parameter prompt"
        }
      },
      "required": []
    }
  },
  {
    "name": "capture_camera",
    "description": "Captures a high-resolution still frame from the connected webcam or laboratory camera.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "camera_index": {
          "type": "INTEGER",
          "description": "Parameter camera_index"
        },
        "save_path": {
          "type": "STRING",
          "description": "Parameter save_path"
        }
      },
      "required": []
    }
  },
  {
    "name": "describe_scene",
    "description": "Captures live webcam feed and provides a physical environment report (e.g. objects on desk, room lighting, user presence).",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "detect_objects",
    "description": "Detects and localizes objects in the camera view (or screen if camera unavailable).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_labels": {
          "type": "STRING",
          "description": "Parameter target_labels"
        }
      },
      "required": []
    }
  },
  {
    "name": "find_object",
    "description": "Searches the camera field of view for a specific object (e.g. 'water bottle', 'phone', 'ESP32 board', 'chess board').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "object_name": {
          "type": "STRING",
          "description": "Parameter object_name"
        }
      },
      "required": [
        "object_name"
      ]
    }
  },
  {
    "name": "ocr_screen",
    "description": "Performs OCR and semantic text extraction on the current desktop workstation screen.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "read_screen",
    "description": "Takes a real-time screenshot of the desktop workstation and performs neural multimodal visual reasoning.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": {
          "type": "STRING",
          "description": "Parameter prompt"
        }
      },
      "required": []
    }
  },
  {
    "name": "track_object",
    "description": "Monitors and tracks movement of an object or person in the camera feed.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "object_name": {
          "type": "STRING",
          "description": "Parameter object_name"
        }
      },
      "required": [
        "object_name"
      ]
    }
  },
  {
    "name": "compare_sources",
    "description": "Synthesizes and compares information across multiple online sources.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        },
        "urls": {
          "type": "ARRAY",
          "description": "Parameter urls",
          "items": {
            "type": "STRING"
          }
        }
      },
      "required": [
        "query",
        "urls"
      ]
    }
  },
  {
    "name": "download_file",
    "description": "Downloads a file or dataset from the internet to local storage.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "Parameter url"
        },
        "save_path": {
          "type": "STRING",
          "description": "Parameter save_path"
        }
      },
      "required": [
        "url"
      ]
    }
  },
  {
    "name": "extract_webpage",
    "description": "Extracts cleaned readable text content and removes ads/scripts from a webpage URL.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "Parameter url"
        }
      },
      "required": [
        "url"
      ]
    }
  },
  {
    "name": "open_webpage",
    "description": "Opens a webpage in the default desktop browser or stealth web automation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "Parameter url"
        }
      },
      "required": [
        "url"
      ]
    }
  },
  {
    "name": "search_documentation",
    "description": "Searches official technical documentation for APIs, microcontrollers (ESP32, Arduino, Raspberry Pi, Python, PyQt5, C++).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "technology": {
          "type": "STRING",
          "description": "Parameter technology"
        },
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "technology",
        "query"
      ]
    }
  },
  {
    "name": "search_github",
    "description": "Searches GitHub repositories, code libraries, and open-source tools.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "search_news",
    "description": "Searches recent breaking news and technical announcements.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "summarize_page",
    "description": "Fetches a webpage and generates an executive technical summary using AI.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "Parameter url"
        }
      },
      "required": [
        "url"
      ]
    }
  },
  {
    "name": "debug_project",
    "description": "Autonomous Multi-Step Debugger:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_path": {
          "type": "STRING",
          "description": "Parameter project_path"
        },
        "error_description": {
          "type": "STRING",
          "description": "Parameter error_description"
        }
      },
      "required": [
        "project_path",
        "error_description"
      ]
    }
  },
  {
    "name": "edit_file",
    "description": "Performs an exact string replacement inside an existing file.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        },
        "target": {
          "type": "STRING",
          "description": "Parameter target"
        },
        "replacement": {
          "type": "STRING",
          "description": "Parameter replacement"
        }
      },
      "required": [
        "path",
        "target",
        "replacement"
      ]
    }
  },
  {
    "name": "git_commit",
    "description": "Stages all changes and creates a git commit.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "message": {
          "type": "STRING",
          "description": "Parameter message"
        }
      },
      "required": [
        "message"
      ]
    }
  },
  {
    "name": "git_diff",
    "description": "Returns git diff summary of unstaged changes.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "git_status",
    "description": "Returns git status of the current project directory.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "inspect_error",
    "description": "Analyzes an error log or stack traceback using AI reasoning, diagnosing the root cause and suggesting a precise fix.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "error_log": {
          "type": "STRING",
          "description": "Parameter error_log"
        }
      },
      "required": [
        "error_log"
      ]
    }
  },
  {
    "name": "install_package",
    "description": "Installs a Python package using pip.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "package_name": {
          "type": "STRING",
          "description": "Parameter package_name"
        }
      },
      "required": [
        "package_name"
      ]
    }
  },
  {
    "name": "prepare_coding_environment",
    "description": "JARVIS Coding Environment Preparation:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_name": {
          "type": "STRING",
          "description": "Parameter project_name"
        }
      },
      "required": [
        "project_name"
      ]
    }
  },
  {
    "name": "run_python",
    "description": "Executes a snippet of Python code and captures stdout/stderr.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code": {
          "type": "STRING",
          "description": "Parameter code"
        }
      },
      "required": [
        "code"
      ]
    }
  },
  {
    "name": "run_tests",
    "description": "Runs automated test suite and reports test failures and tracebacks.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "test_command": {
          "type": "STRING",
          "description": "Parameter test_command"
        }
      },
      "required": []
    }
  },
  {
    "name": "search_code",
    "description": "Searches for code patterns, function names, or variables across a directory.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        },
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "activate_preset_scene",
    "description": "Activates complete JARVIS environmental scenes:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "scene_name": {
          "type": "STRING",
          "description": "Parameter scene_name"
        }
      },
      "required": [
        "scene_name"
      ]
    }
  },
  {
    "name": "control_ac",
    "description": "Controls Air Conditioner temperature (°C) and mode ('cool', 'fan', 'eco', 'off').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "temp": {
          "type": "INTEGER",
          "description": "Parameter temp"
        },
        "mode": {
          "type": "STRING",
          "description": "Parameter mode"
        }
      },
      "required": [
        "temp"
      ]
    }
  },
  {
    "name": "control_fan",
    "description": "Controls the room ventilation/cooling fan speed (0 to 100%).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "speed": {
          "type": "INTEGER",
          "description": "Parameter speed"
        }
      },
      "required": [
        "speed"
      ]
    }
  },
  {
    "name": "control_plug",
    "description": "Controls smart power relays and bench equipment ('on' / 'off').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "device": {
          "type": "STRING",
          "description": "Parameter device"
        },
        "state": {
          "type": "STRING",
          "description": "Parameter state"
        }
      },
      "required": [
        "device",
        "state"
      ]
    }
  },
  {
    "name": "get_device_status",
    "description": "Queries real-time telemetry and status of all connected IoT devices.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "device": {
          "type": "STRING",
          "description": "Parameter device"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_room_temperature",
    "description": "Reads real-time ambient laboratory/room temperature and humidity sensors.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "set_light_brightness",
    "description": "Sets the brightness level (0 to 100%) for a lighting device.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "level": {
          "type": "INTEGER",
          "description": "Parameter level"
        },
        "device": {
          "type": "STRING",
          "description": "Parameter device"
        }
      },
      "required": [
        "level"
      ]
    }
  },
  {
    "name": "set_light_color",
    "description": "Sets RGB color hex or color name (e.g. 'orange', 'cyan', 'warm white', '#FF9100') for smart lights.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "color": {
          "type": "STRING",
          "description": "Parameter color"
        },
        "device": {
          "type": "STRING",
          "description": "Parameter device"
        }
      },
      "required": [
        "color"
      ]
    }
  },
  {
    "name": "turn_light_off",
    "description": "Turns off the specified light or LED strip ('main', 'desk_led', 'ambient', 'all').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "device": {
          "type": "STRING",
          "description": "Parameter device"
        }
      },
      "required": []
    }
  },
  {
    "name": "turn_light_on",
    "description": "Turns on the specified light or LED strip ('main', 'desk_led', 'ambient', 'all').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "device": {
          "type": "STRING",
          "description": "Parameter device"
        }
      },
      "required": []
    }
  },
  {
    "name": "control_motor",
    "description": "Controls DC/Stepper motor speed (0 to 255) and direction ('forward' / 'reverse' / 'brake').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "motor_id": {
          "type": "INTEGER",
          "description": "Parameter motor_id"
        },
        "speed": {
          "type": "INTEGER",
          "description": "Parameter speed"
        },
        "direction": {
          "type": "STRING",
          "description": "Parameter direction"
        }
      },
      "required": [
        "motor_id",
        "speed"
      ]
    }
  },
  {
    "name": "detect_obstacle",
    "description": "Checks forward sonar sensors for potential navigational obstacles.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "follow_person",
    "description": "Commands rover/camera to continuously track and follow target movement.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "grab_object",
    "description": "Actuates the robotic arm gripper claw (0° = Fully Open, 90° = Firm Grip, 180° = Maximum Clamping).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "gripper_angle": {
          "type": "INTEGER",
          "description": "Parameter gripper_angle"
        }
      },
      "required": []
    }
  },
  {
    "name": "move_robot",
    "description": "Drives a robotic rover/chassis in a direction ('forward', 'backward', 'left', 'right', 'stop') for N seconds.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "direction": {
          "type": "STRING",
          "description": "Parameter direction"
        },
        "duration_sec": {
          "type": "NUMBER",
          "description": "Parameter duration_sec"
        },
        "speed": {
          "type": "INTEGER",
          "description": "Parameter speed"
        }
      },
      "required": [
        "direction"
      ]
    }
  },
  {
    "name": "move_servo",
    "description": "Commands a PWM servo motor on the specified pin/channel to rotate to the given angle (0 to 180 degrees).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "INTEGER",
          "description": "Parameter pin"
        },
        "angle": {
          "type": "INTEGER",
          "description": "Parameter angle"
        },
        "channel": {
          "type": "INTEGER",
          "description": "Parameter channel"
        }
      },
      "required": [
        "pin",
        "angle"
      ]
    }
  },
  {
    "name": "read_distance",
    "description": "Reads distance to nearest physical obstacle using HC-SR04 ultrasonic / LiDAR sensor.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "sensor_type": {
          "type": "STRING",
          "description": "Parameter sensor_type"
        }
      },
      "required": []
    }
  },
  {
    "name": "track_person",
    "description": "Employs camera neural tracking to orient servo pan-tilt mount towards user's face/body.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "cancel_mission",
    "description": "Cancels and archives a mission.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mission_id": {
          "type": "STRING",
          "description": "Parameter mission_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "create_mission",
    "description": "Initializes a new persistent multi-step mission objective for ULTRON to track and execute.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "title": {
          "type": "STRING",
          "description": "Parameter title"
        },
        "objective": {
          "type": "STRING",
          "description": "Parameter objective"
        },
        "steps": {
          "type": "ARRAY",
          "description": "Parameter steps",
          "items": {
            "type": "STRING"
          }
        }
      },
      "required": [
        "title",
        "objective"
      ]
    }
  },
  {
    "name": "emergency_stop",
    "description": "JARVIS Emergency Override: Immediately halts all active subagents, robotic motors, and automated script loops.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "execute_mission",
    "description": "Executes or advances the active mission to its next chronological milestone.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mission_id": {
          "type": "STRING",
          "description": "Parameter mission_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_mission_status",
    "description": "Returns the live status, progress bar, and logs of the active mission.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mission_id": {
          "type": "STRING",
          "description": "Parameter mission_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "pause_mission",
    "description": "Pauses execution of the active mission.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mission_id": {
          "type": "STRING",
          "description": "Parameter mission_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "permission_check",
    "description": "Validates security clearance and permission matrix for an operation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action_name": {
          "type": "STRING",
          "description": "Parameter action_name"
        }
      },
      "required": [
        "action_name"
      ]
    }
  },
  {
    "name": "plan_mission",
    "description": "Uses AI neural reasoning to decompose a high-level goal into an optimized step-by-step execution roadmap.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "objective": {
          "type": "STRING",
          "description": "Parameter objective"
        }
      },
      "required": [
        "objective"
      ]
    }
  },
  {
    "name": "request_confirmation",
    "description": "JARVIS Safety Gate: Requests explicit verbal or UI confirmation before executing high-impact actions.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action_description": {
          "type": "STRING",
          "description": "Parameter action_description"
        },
        "risk_level": {
          "type": "STRING",
          "description": "Parameter risk_level"
        }
      },
      "required": [
        "action_description"
      ]
    }
  },
  {
    "name": "resume_mission",
    "description": "Resumes a paused mission.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mission_id": {
          "type": "STRING",
          "description": "Parameter mission_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "complete_todo",
    "description": "Marks a todo task as completed.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task_id_or_keyword": {
          "type": "STRING",
          "description": "Parameter task_id_or_keyword"
        }
      },
      "required": [
        "task_id_or_keyword"
      ]
    }
  },
  {
    "name": "create_calendar_event",
    "description": "Adds an event, competition, or meeting to ULTRON's master calendar.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "title": {
          "type": "STRING",
          "description": "Parameter title"
        },
        "date_time": {
          "type": "STRING",
          "description": "Parameter date_time"
        },
        "description": {
          "type": "STRING",
          "description": "Parameter description"
        }
      },
      "required": [
        "title",
        "date_time"
      ]
    }
  },
  {
    "name": "create_note",
    "description": "Saves a rich text note or code snippet to ULTRON's persistent notebook.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "title": {
          "type": "STRING",
          "description": "Parameter title"
        },
        "content": {
          "type": "STRING",
          "description": "Parameter content"
        },
        "tags": {
          "type": "STRING",
          "description": "Parameter tags"
        }
      },
      "required": [
        "title",
        "content"
      ]
    }
  },
  {
    "name": "create_reminder",
    "description": "Sets a voice/visual reminder for a specific time or event.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "reminder_text": {
          "type": "STRING",
          "description": "Parameter reminder_text"
        },
        "time_str": {
          "type": "STRING",
          "description": "Parameter time_str"
        }
      },
      "required": [
        "reminder_text",
        "time_str"
      ]
    }
  },
  {
    "name": "list_todos",
    "description": "Lists todos filtered by status ('pending', 'completed', 'all').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "status": {
          "type": "STRING",
          "description": "Parameter status"
        }
      },
      "required": []
    }
  },
  {
    "name": "make_todo",
    "description": "Adds a task to ULTRON's actionable Todo checklist.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Parameter task"
        },
        "priority": {
          "type": "STRING",
          "description": "Parameter priority"
        },
        "due_date": {
          "type": "STRING",
          "description": "Parameter due_date"
        }
      },
      "required": [
        "task"
      ]
    }
  },
  {
    "name": "read_calendar",
    "description": "Reads all scheduled events, competitions, and milestones from calendar.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "date_or_range": {
          "type": "STRING",
          "description": "Parameter date_or_range"
        }
      },
      "required": []
    }
  },
  {
    "name": "search_notes",
    "description": "Searches saved notes by title, content, or tags.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "remember_project_decision",
    "description": "Records an architectural design decision, framework choice, or constraint for a project.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project": {
          "type": "STRING",
          "description": "Parameter project"
        },
        "decision": {
          "type": "STRING",
          "description": "Parameter decision"
        },
        "rationale": {
          "type": "STRING",
          "description": "Parameter rationale"
        }
      },
      "required": [
        "project",
        "decision"
      ]
    }
  },
  {
    "name": "remember_user_preference",
    "description": "Stores a specific user preference, style guideline, or habit.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "preference": {
          "type": "STRING",
          "description": "Parameter preference"
        },
        "category": {
          "type": "STRING",
          "description": "Parameter category"
        }
      },
      "required": [
        "preference"
      ]
    }
  },
  {
    "name": "retrieve_memory",
    "description": "Retrieves all matching facts, preferences, project decisions, and event logs.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        },
        "category": {
          "type": "STRING",
          "description": "Parameter category"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "save_conversation",
    "description": "Saves a milestone conversation summary to persistent memory.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "summary": {
          "type": "STRING",
          "description": "Parameter summary"
        },
        "tags": {
          "type": "ARRAY",
          "description": "Parameter tags",
          "items": {
            "type": "STRING"
          }
        }
      },
      "required": [
        "summary"
      ]
    }
  },
  {
    "name": "search_knowledge",
    "description": "Searches indexed documentation and knowledge base articles.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Parameter query"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "store_document",
    "description": "Indexes a technical specification, API reference, or design document into ULTRON's local knowledge base.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "title": {
          "type": "STRING",
          "description": "Parameter title"
        },
        "content": {
          "type": "STRING",
          "description": "Parameter content"
        },
        "doc_type": {
          "type": "STRING",
          "description": "Parameter doc_type"
        }
      },
      "required": [
        "title",
        "content"
      ]
    }
  },
  {
    "name": "open_youtube",
    "description": "Directly opens YouTube in the browser and plays a requested song or searches a video.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Optional song title, artist, or search phrase to play directly on YouTube."
        }
      }
    }
  },
  {
    "name": "tool_selector",
    "description": "Intelligent tool router that maps high-level user commands to the optimal ULTRON tool and executes it immediately.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "command": {
          "type": "STRING",
          "description": "The exact user command to analyze and route to a tool."
        }
      },
      "required": [
        "command"
      ]
    }
  },
  {
    "name": "get_active_tasks",
    "description": "Returns currently running background subagents and active mission milestones.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_current_goal",
    "description": "Returns the primary high-level strategic goal ULTRON is currently executing.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_device_state",
    "description": "Returns connected microcontrollers, sensors, actuators, and serial links.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_environment_state",
    "description": "Returns ambient temperature, lighting scene, and physical environment state.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_user_context",
    "description": "Returns real-time profile, active tasks, and context of the user.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_world_state",
    "description": "Returns the complete consolidated live world model: User Focus, Workstation, Hardware, Environment, and Active Mission.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "update_world_state",
    "description": "Updates a section of the live world model ('user', 'workstation', 'hardware_bus', 'environment', 'active_mission').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "section": {
          "type": "STRING",
          "description": "Parameter section"
        },
        "data_json_or_text": {
          "type": "STRING",
          "description": "Parameter data_json_or_text"
        }
      },
      "required": [
        "section",
        "data_json_or_text"
      ]
    }
  },
  {
    "name": "detect_failure",
    "description": "Analyzes a tool or command output for syntax errors, return codes, and exceptions.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "result_payload": {
          "type": "STRING",
          "description": "Parameter result_payload"
        }
      },
      "required": [
        "result_payload"
      ]
    }
  },
  {
    "name": "diagnose_failure",
    "description": "Diagnoses the root cause of an execution failure and drafts a targeted repair patch.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "error_trace": {
          "type": "STRING",
          "description": "Parameter error_trace"
        },
        "context": {
          "type": "STRING",
          "description": "Parameter context"
        }
      },
      "required": [
        "error_trace"
      ]
    }
  },
  {
    "name": "repair_failure",
    "description": "Autonomously analyzes an error trace, inspects the target file, and applies the corrected code patch.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "error_trace": {
          "type": "STRING",
          "description": "Parameter error_trace"
        },
        "target_file": {
          "type": "STRING",
          "description": "Parameter target_file"
        }
      },
      "required": [
        "error_trace"
      ]
    }
  },
  {
    "name": "rollback_action",
    "description": "Restores the most recent file or state backup created prior to an automated repair.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action_id": {
          "type": "STRING",
          "description": "Parameter action_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "validate_mission",
    "description": "Verifies all completed steps of the active mission and asserts integrity.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mission_id": {
          "type": "STRING",
          "description": "Parameter mission_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "verify_action",
    "description": "Evaluates whether an action succeeded by comparing actual output against the expected objective.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action_name": {
          "type": "STRING",
          "description": "Parameter action_name"
        },
        "expected_outcome": {
          "type": "STRING",
          "description": "Parameter expected_outcome"
        },
        "actual_output": {
          "type": "STRING",
          "description": "Parameter actual_output"
        }
      },
      "required": [
        "action_name",
        "expected_outcome",
        "actual_output"
      ]
    }
  },
  {
    "name": "capture_serial_logs",
    "description": "Retrieves recent serial log buffer from active device.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        },
        "lines_count": {
          "type": "INTEGER",
          "description": "Parameter lines_count"
        }
      },
      "required": []
    }
  },
  {
    "name": "detect_connected_actuators",
    "description": "Identifies all active servos, motor drivers (L298N/DRV8833), and relays.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "detect_connected_sensors",
    "description": "Identifies all active environmental, motion, ultrasonic, and analog sensors.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "identify_arduino_board",
    "description": "Identifies connected Arduino microcontrollers (Uno, Nano, Mega, Leonardo).",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "identify_esp32_board",
    "description": "Detects and queries connected ESP32 / ESP8266 boards via esptool.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "identify_raspberry_pi",
    "description": "Checks for local Raspberry Pi Pico / RP2040 bootloader devices.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "identify_usb_devices",
    "description": "Scans and identifies all connected USB devices via PowerShell/WMI.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "monitor_serial",
    "description": "Captures live stream of serial packets and logs from connected microcontroller.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        },
        "baud": {
          "type": "INTEGER",
          "description": "Parameter baud"
        },
        "duration_sec": {
          "type": "NUMBER",
          "description": "Parameter duration_sec"
        }
      },
      "required": []
    }
  },
  {
    "name": "read_analog_pin",
    "description": "Reads raw 12-bit ADC value (0-4095) from an analog pin.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "INTEGER",
          "description": "Parameter pin"
        },
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": [
        "pin"
      ]
    }
  },
  {
    "name": "read_gpio_state",
    "description": "Reads digital logic level (HIGH=1 / LOW=0) of a GPIO pin.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "INTEGER",
          "description": "Parameter pin"
        },
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": [
        "pin"
      ]
    }
  },
  {
    "name": "reset_microcontroller",
    "description": "Triggers hardware DTR/RTS pulse to reset microcontroller.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": []
    }
  },
  {
    "name": "scan_i2c_devices",
    "description": "Scans I2C bus (0x00 to 0x7F) and identifies connected sensors (e.g. MPU6050, BMP280, OLED, TMP102).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": []
    }
  },
  {
    "name": "scan_serial_ports",
    "description": "Scans and lists all connected serial COM ports, VID/PID, and USB hardware descriptions.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "scan_spi_devices",
    "description": "Scans SPI bus devices (SPI Flash, SD Card Module, NRF24L01 RF transceiver).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": []
    }
  },
  {
    "name": "set_pwm",
    "description": "Configures hardware PWM duty cycle (0-255 or 0-1023) and frequency (Hz) on a pin.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "INTEGER",
          "description": "Parameter pin"
        },
        "duty": {
          "type": "INTEGER",
          "description": "Parameter duty"
        },
        "freq": {
          "type": "INTEGER",
          "description": "Parameter freq"
        },
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": [
        "pin",
        "duty"
      ]
    }
  },
  {
    "name": "upload_firmware",
    "description": "Flashes compiled binary payload to target microcontroller.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        },
        "binary_path": {
          "type": "STRING",
          "description": "Parameter binary_path"
        }
      },
      "required": [
        "port",
        "binary_path"
      ]
    }
  },
  {
    "name": "verify_firmware",
    "description": "Performs CRC and bootloader self-test on running microcontroller firmware.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": []
    }
  },
  {
    "name": "write_gpio_state",
    "description": "Sets digital logic level (1 or 0) on a GPIO pin.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "INTEGER",
          "description": "Parameter pin"
        },
        "state": {
          "type": "INTEGER",
          "description": "Parameter state"
        },
        "port": {
          "type": "STRING",
          "description": "Parameter port"
        }
      },
      "required": [
        "pin",
        "state"
      ]
    }
  },
  {
    "name": "run_hardware_diagnostics",
    "description": "Executes a complete, end-to-end laboratory testbench diagnostic on all connected microcontrollers and sensors.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "scan_lab",
    "description": "Comprehensive physical lab sweep: scans serial ports, I2C/SPI buses, webcams, and USB instruments.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "start_lab_mode",
    "description": "Engages full JARVIS Hardware Laboratory Mode:",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "stop_lab_mode",
    "description": "Disengages Hardware Laboratory Mode and restores standard focus environment.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "test_gpio",
    "description": "Toggles GPIO pin logic high and low to test pull-up/pull-down circuitry.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "INTEGER",
          "description": "Parameter pin"
        }
      },
      "required": []
    }
  },
  {
    "name": "test_motor",
    "description": "Executes a momentary forward/reverse speed test on the specified motor channel.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "motor_id": {
          "type": "INTEGER",
          "description": "Parameter motor_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "test_relay",
    "description": "Cycles smart power relay contacts to verify actuation and continuity.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "channel": {
          "type": "INTEGER",
          "description": "Parameter channel"
        }
      },
      "required": []
    }
  },
  {
    "name": "test_sensor",
    "description": "Tests and calibrates specified sensor ('ultrasonic', 'temperature', 'imu', 'all').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "sensor_name": {
          "type": "STRING",
          "description": "Parameter sensor_name"
        }
      },
      "required": []
    }
  },
  {
    "name": "test_servo",
    "description": "Sweeps servo through 0° -> 90° -> 180° -> 90° to verify mechanical gear integrity.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pin": {
          "type": "INTEGER",
          "description": "Parameter pin"
        }
      },
      "required": []
    }
  },
  {
    "name": "analyze_repository",
    "description": "Analyzes an entire codebase: directory tree, key modules, entrypoints, dependencies, and architectural patterns.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "repo_path": {
          "type": "STRING",
          "description": "Parameter repo_path"
        }
      },
      "required": []
    }
  },
  {
    "name": "create_implementation_plan",
    "description": "Generates an end-to-end architectural design document and step-by-step diff plan for a new feature.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "feature_request": {
          "type": "STRING",
          "description": "Parameter feature_request"
        }
      },
      "required": [
        "feature_request"
      ]
    }
  },
  {
    "name": "create_pull_request",
    "description": "Automates git branch creation and prepares a pull request summary.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "branch": {
          "type": "STRING",
          "description": "Parameter branch"
        },
        "title": {
          "type": "STRING",
          "description": "Parameter title"
        },
        "body": {
          "type": "STRING",
          "description": "Parameter body"
        }
      },
      "required": [
        "branch",
        "title",
        "body"
      ]
    }
  },
  {
    "name": "find_security_issues",
    "description": "Scans code for hardcoded secrets, injection vectors, buffer overflows, and unsafe dependencies.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": []
    }
  },
  {
    "name": "generate_release",
    "description": "Builds release binaries, tags commit, and writes CHANGELOG.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tag": {
          "type": "STRING",
          "description": "Parameter tag"
        },
        "notes": {
          "type": "STRING",
          "description": "Parameter notes"
        }
      },
      "required": [
        "tag"
      ]
    }
  },
  {
    "name": "generate_tests",
    "description": "Autonomously writes pytest unit tests and edge-case assertions for a target file.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "source_file": {
          "type": "STRING",
          "description": "Parameter source_file"
        }
      },
      "required": [
        "source_file"
      ]
    }
  },
  {
    "name": "implement_feature",
    "description": "Autonomously executes multi-file feature implementation, creating or editing files according to architectural requirements.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "feature_description": {
          "type": "STRING",
          "description": "Parameter feature_description"
        },
        "repo_path": {
          "type": "STRING",
          "description": "Parameter repo_path"
        }
      },
      "required": [
        "feature_description"
      ]
    }
  },
  {
    "name": "optimize_code",
    "description": "Identifies asymptotic bottlenecks, redundant allocations, and optimizes algorithms.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "path": {
          "type": "STRING",
          "description": "Parameter path"
        }
      },
      "required": [
        "path"
      ]
    }
  },
  {
    "name": "refactor_project",
    "description": "Applies structured codebase refactoring across modular layers.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "instructions": {
          "type": "STRING",
          "description": "Parameter instructions"
        },
        "repo_path": {
          "type": "STRING",
          "description": "Parameter repo_path"
        }
      },
      "required": [
        "instructions"
      ]
    }
  },
  {
    "name": "review_code",
    "description": "Performs rigorous static analysis, style check, and algorithmic review of code.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_file_or_diff": {
          "type": "STRING",
          "description": "Parameter target_file_or_diff"
        }
      },
      "required": [
        "target_file_or_diff"
      ]
    }
  },
  {
    "name": "run_test_and_repair",
    "description": "Closed-Loop Test & Auto-Repair:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "test_cmd": {
          "type": "STRING",
          "description": "Parameter test_cmd"
        },
        "max_attempts": {
          "type": "INTEGER",
          "description": "Parameter max_attempts"
        }
      },
      "required": []
    }
  },
  {
    "name": "understand_project",
    "description": "High-level semantic architectural review of the active workspace.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_name": {
          "type": "STRING",
          "description": "Parameter project_name"
        }
      },
      "required": []
    }
  },
  {
    "name": "compare_scene",
    "description": "Compares the current physical camera feed against the stored reference baseline and reports moved or missing items.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "scene_tag": {
          "type": "STRING",
          "description": "Parameter scene_tag"
        }
      },
      "required": []
    }
  },
  {
    "name": "detect_object_change",
    "description": "Detects if any hardware board, phone, or tool was placed or removed from the desk.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "detect_person_entry",
    "description": "Detects if a person has entered or approached the workstation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "detect_scene_change",
    "description": "Calculates optical scene difference and reports if physical changes occurred.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "scene_tag": {
          "type": "STRING",
          "description": "Parameter scene_tag"
        }
      },
      "required": []
    }
  },
  {
    "name": "remember_visual_scene",
    "description": "Captures the current camera scene and stores it as a golden reference baseline in visual memory.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "scene_tag": {
          "type": "STRING",
          "description": "Parameter scene_tag"
        }
      },
      "required": []
    }
  },
  {
    "name": "stop_watching",
    "description": "Disengages the background visual watcher thread.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "watch_area",
    "description": "Initiates continuous background visual monitoring of a physical area (e.g. 'workbench', 'lab door').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "area_name": {
          "type": "STRING",
          "description": "Parameter area_name"
        },
        "interval_sec": {
          "type": "INTEGER",
          "description": "Parameter interval_sec"
        }
      },
      "required": []
    }
  },
  {
    "name": "change_voice",
    "description": "Switches the neural text-to-speech voice model and timbre.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "voice_id": {
          "type": "STRING",
          "description": "Parameter voice_id"
        }
      },
      "required": []
    }
  },
  {
    "name": "detect_interruption",
    "description": "Detects if user spoke while ULTRON was speaking (barge-in support) to halt audio output immediately.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "detect_speech",
    "description": "Checks audio buffers for incoming user speech energy.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "listen_continuously",
    "description": "Engages continuous background microphone stream with voice activity detection (VAD).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration_sec": {
          "type": "INTEGER",
          "description": "Parameter duration_sec"
        }
      },
      "required": []
    }
  },
  {
    "name": "resume_speaking",
    "description": "Resumes paused speech audio stream.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "set_voice_personality",
    "description": "Sets the conversational tone and prosody:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "preset": {
          "type": "STRING",
          "description": "Parameter preset"
        }
      },
      "required": []
    }
  },
  {
    "name": "stop_speaking",
    "description": "Immediately halts any currently playing text-to-speech audio stream.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "voice_command_history",
    "description": "Returns the most recent vocal commands processed by the speech pipeline.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "limit": {
          "type": "INTEGER",
          "description": "Parameter limit"
        }
      },
      "required": []
    }
  },
  {
    "name": "voice_confirmation",
    "description": "JARVIS Voice Confirmation Gate: Queries the user and waits for 'Yes/Proceed' or 'No/Cancel'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": {
          "type": "STRING",
          "description": "Parameter prompt"
        }
      },
      "required": []
    }
  },
  {
    "name": "wake_word",
    "description": "Configures the primary neural wake word (e.g. 'ULTRON', 'JARVIS').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "word": {
          "type": "STRING",
          "description": "Parameter word"
        }
      },
      "required": []
    }
  },
  {
    "name": "disable_tool",
    "description": "Temporarily disables a tool from active dispatching.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "enable_tool",
    "description": "Re-enables a tool for autonomous execution.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "find_capability",
    "description": "Semantically searches the entire 421+ tool ecosystem and returns the most relevant tool functions and parameter schemas.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task_description": {
          "type": "STRING",
          "description": "Parameter task_description"
        }
      },
      "required": [
        "task_description"
      ]
    }
  },
  {
    "name": "get_tool_dependencies",
    "description": "Returns Python packages and hardware peripherals required by a tool.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "get_tool_status",
    "description": "Checks if a tool is ready, enabled, or experiencing runtime errors.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "inspect_tool",
    "description": "Returns docstring, parameter schema, and implementation details for a tool.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "learn_tool",
    "description": "Dynamically registers a new custom tool function created at runtime.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        },
        "code_definition": {
          "type": "STRING",
          "description": "Parameter code_definition"
        }
      },
      "required": [
        "tool_name",
        "code_definition"
      ]
    }
  },
  {
    "name": "list_capabilities",
    "description": "Returns an indexed summary of all capabilities across functional categories.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "category": {
          "type": "STRING",
          "description": "Parameter category"
        }
      },
      "required": []
    }
  },
  {
    "name": "test_tool",
    "description": "Executes a non-destructive dry-run of a tool function to assert operational health.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "get_hud_state",
    "description": "Returns the unified HUD telemetry object for UI rendering and status inspection.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_active_tools",
    "description": "Displays count and status of active tools in the ecosystem.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_alerts",
    "description": "Displays current system alerts, upcoming reminders, and security warnings.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_hardware_status",
    "description": "Displays connected boards, sensors, and actuators.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_hud_ascii",
    "description": "Renders an Iron Man / JARVIS styled ASCII status HUD directly to the terminal/chat window.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_mission_progress",
    "description": "Displays visual progress bar and milestones for the active mission.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_network_status",
    "description": "Displays network interfaces, active connections, and packet flow.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_subagents",
    "description": "Displays table of background subagent workers.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_system_metrics",
    "description": "Displays CPU, GPU, RAM, and Disk metrics.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "coding_agent",
    "description": "Specialized Agent: Software engineer that drafts production-ready code files and modules.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Parameter task"
        }
      },
      "required": [
        "task"
      ]
    }
  },
  {
    "name": "hardware_agent",
    "description": "Specialized Agent: Embedded systems engineer managing ESP32, Arduino, I2C/SPI sensors, and firmware.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Parameter task"
        }
      },
      "required": [
        "task"
      ]
    }
  },
  {
    "name": "planning_agent",
    "description": "Specialized Agent: Decomposes complex strategic goals into technical execution roadmaps.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "objective": {
          "type": "STRING",
          "description": "Parameter objective"
        }
      },
      "required": [
        "objective"
      ]
    }
  },
  {
    "name": "research_agent",
    "description": "Specialized Agent: Conducts exhaustive internet research, extracts documentation, and synthesizes findings.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "topic": {
          "type": "STRING",
          "description": "Parameter topic"
        }
      },
      "required": [
        "topic"
      ]
    }
  },
  {
    "name": "review_agent",
    "description": "Specialized Agent: Code auditor inspecting pull requests, logic bugs, and algorithmic performance.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code_diff": {
          "type": "STRING",
          "description": "Parameter code_diff"
        }
      },
      "required": [
        "code_diff"
      ]
    }
  },
  {
    "name": "security_agent",
    "description": "Specialized Agent: Cybersecurity specialist auditing ports, packets, vulnerabilities, and rootkits.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "Parameter target"
        }
      },
      "required": [
        "target"
      ]
    }
  },
  {
    "name": "testing_agent",
    "description": "Specialized Agent: Quality assurance specialist writing and asserting unit tests.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "Parameter target"
        }
      },
      "required": [
        "target"
      ]
    }
  },
  {
    "name": "vision_agent",
    "description": "Specialized Agent: Computer vision and spatial awareness specialist analyzing camera and screen feeds.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Parameter task"
        }
      },
      "required": [
        "task"
      ]
    }
  },
  {
    "name": "enforce_policy",
    "description": "Enforces safety policy before executing a tool.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        },
        "params": {
          "type": "STRING",
          "description": "Parameter params"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "evaluate_action_safety",
    "description": "Evaluates safety tier of a requested tool execution:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "tool_name": {
          "type": "STRING",
          "description": "Parameter tool_name"
        },
        "params": {
          "type": "STRING",
          "description": "Parameter params"
        }
      },
      "required": [
        "tool_name"
      ]
    }
  },
  {
    "name": "list_policy_tiers",
    "description": "Lists summary of the security clearance tiers.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "add_feature_to_project",
    "description": "Autonomously adds a new feature or module to an existing project:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_name": {
          "type": "STRING",
          "description": "Parameter project_name"
        },
        "feature_description": {
          "type": "STRING",
          "description": "Parameter feature_description"
        }
      },
      "required": [
        "project_name",
        "feature_description"
      ]
    }
  },
  {
    "name": "audit_and_fix_project",
    "description": "Autonomous Full-Codebase Audit & Auto-Repair:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_path": {
          "type": "STRING",
          "description": "Parameter project_path"
        }
      },
      "required": []
    }
  },
  {
    "name": "build_complete_project",
    "description": "Autonomously builds an entire end-to-end software or embedded hardware project:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_name": {
          "type": "STRING",
          "description": "Parameter project_name"
        },
        "specification": {
          "type": "STRING",
          "description": "Parameter specification"
        },
        "tech_stack": {
          "type": "STRING",
          "description": "Parameter tech_stack"
        }
      },
      "required": [
        "project_name",
        "specification"
      ]
    }
  },
  {
    "name": "list_ultron_projects",
    "description": "Lists all active and completed projects managed by ULTRON.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "auto_fix_syntax",
    "description": "Self-healing loop: Feeds syntax traceback directly to AI model to generate an immediate AST-compliant fix.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code": {
          "type": "STRING",
          "description": "Parameter code"
        },
        "error_msg": {
          "type": "STRING",
          "description": "Parameter error_msg"
        },
        "language": {
          "type": "STRING",
          "description": "Parameter language"
        },
        "max_retries": {
          "type": "INTEGER",
          "description": "Parameter max_retries"
        }
      },
      "required": [
        "code",
        "error_msg"
      ]
    }
  },
  {
    "name": "clean_code_snippet",
    "description": "Strips conversational preambles, trailing markdown comments, and extracts 100% pure code.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "raw_text": {
          "type": "STRING",
          "description": "Parameter raw_text"
        },
        "language": {
          "type": "STRING",
          "description": "Parameter language"
        }
      },
      "required": [
        "raw_text"
      ]
    }
  },
  {
    "name": "execute_python_safe",
    "description": "Executes Python code with pre-flight AST checks and automated runtime traceback repair.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code": {
          "type": "STRING",
          "description": "Parameter code"
        },
        "timeout_sec": {
          "type": "INTEGER",
          "description": "Parameter timeout_sec"
        }
      },
      "required": [
        "code"
      ]
    }
  },
  {
    "name": "generate_esp32_firmware",
    "description": "Generates complete Arduino C++ firmware for ESP32 with auto-included headers, GPIO pinouts, and bracket verification.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "description": {
          "type": "STRING",
          "description": "Parameter description"
        },
        "libraries": {
          "type": "ARRAY",
          "description": "Parameter libraries",
          "items": {
            "type": "STRING"
          }
        }
      },
      "required": [
        "description"
      ]
    }
  },
  {
    "name": "validate_syntax",
    "description": "Strict pre-execution syntax validation:",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code": {
          "type": "STRING",
          "description": "Parameter code"
        },
        "language": {
          "type": "STRING",
          "description": "Parameter language"
        }
      },
      "required": [
        "code"
      ]
    }
  },
  {
    "name": "start_minecraft_player_bot",
    "description": "MUST USE when user asks to join SMP, join Minecraft server, connect to server, or log into the game. Spawns the autonomous in-game ULTRON player bot into the Minecraft SMP.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "host": {
          "type": "STRING",
          "description": "The server address or hostname (default: hamaraserverkabap.aternos.me)"
        },
        "port": {
          "type": "INTEGER",
          "description": "The server port (default: 40350)"
        },
        "username": {
          "type": "STRING",
          "description": "In-game player username (default: ULTRON)"
        },
        "edition": {
          "type": "STRING",
          "description": "Minecraft edition: bedrock or java (default: bedrock)"
        }
      }
    }
  },
  {
    "name": "stop_minecraft_player_bot",
    "description": "MUST USE when user asks to leave SMP, disconnect from Minecraft, quit server, or stop the Minecraft bot.",
    "parameters": {
      "type": "OBJECT",
      "properties": {}
    }
  },
  {
    "name": "minecraft_server_status",
    "description": "Queries real-time Minecraft server status, MOTD, ping latency, and online player list.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "host": {
          "type": "STRING",
          "description": "Server host/IP"
        },
        "port": {
          "type": "INTEGER",
          "description": "Server port"
        }
      }
    }
  },
  {
    "name": "computer_use",
    "description": "Autonomously sees the screen and interacts with GUI elements to complete a task using AI vision",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Detailed description of the GUI task to automate on screen"
        },
        "max_steps": {
          "type": "INTEGER",
          "description": "Maximum automation steps (default 10)"
        }
      },
      "required": []
    }
  },
  {
    "name": "screen_analyze",
    "description": "Captures the current screen and uses AI vision to answer any question about what is displayed",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "question": {
          "type": "STRING",
          "description": "Question to ask about what is currently visible on screen"
        }
      },
      "required": []
    }
  },
  {
    "name": "find_and_click",
    "description": "Finds a described UI element on screen using AI vision and clicks it",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "element": {
          "type": "STRING",
          "description": "Description of the UI element to find and click on screen"
        }
      },
      "required": []
    }
  },
  {
    "name": "solve_homework",
    "description": "Captures the screen showing homework/questions and provides complete step-by-step solutions",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "subject": {
          "type": "STRING",
          "description": "Subject area (math, science, english, history, general)"
        }
      },
      "required": []
    }
  },
  {
    "name": "solve_from_photo",
    "description": "Captures a photo from webcam of textbook or notebook and solves the visible problem",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "solve_math",
    "description": "Solves a mathematical equation step by step with full working shown",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "equation": {
          "type": "STRING",
          "description": "Mathematical equation or problem to solve"
        }
      },
      "required": []
    }
  },
  {
    "name": "explain_concept",
    "description": "Explains an academic or technical concept with examples and analogies at specified level",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "topic": {
          "type": "STRING",
          "description": "Academic or technical topic to explain"
        },
        "level": {
          "type": "STRING",
          "description": "Comprehension level: elementary, high school, college, expert"
        }
      },
      "required": []
    }
  },
  {
    "name": "email_inbox_summary",
    "description": "Fetches and provides an AI-analyzed summary of recent emails with categorization and urgency flags",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "count": {
          "type": "INTEGER",
          "description": "Number of recent emails to summarize (default 10)"
        },
        "account": {
          "type": "STRING",
          "description": "Email account: primary or secondary"
        }
      },
      "required": []
    }
  },
  {
    "name": "email_draft_reply",
    "description": "Reads an email and drafts an AI-generated reply in the specified tone",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "index": {
          "type": "INTEGER",
          "description": "Email index (1=newest)"
        },
        "tone": {
          "type": "STRING",
          "description": "Reply tone: professional, casual, formal, friendly"
        },
        "account": {
          "type": "STRING",
          "description": "Email account: primary or secondary"
        }
      },
      "required": []
    }
  },
  {
    "name": "email_send_reply",
    "description": "Sends a reply to a specific email",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "index": {
          "type": "INTEGER",
          "description": "Email index to reply to (1=newest)"
        },
        "reply_text": {
          "type": "STRING",
          "description": "The reply text to send"
        },
        "account": {
          "type": "STRING",
          "description": "Email account: primary or secondary"
        }
      },
      "required": []
    }
  },
  {
    "name": "email_smart_compose",
    "description": "Composes and sends an AI-written email about a given topic",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "to": {
          "type": "STRING",
          "description": "Recipient email address"
        },
        "about": {
          "type": "STRING",
          "description": "What the email should be about"
        },
        "tone": {
          "type": "STRING",
          "description": "Email tone: professional, casual, formal"
        },
        "account": {
          "type": "STRING",
          "description": "Email account: primary or secondary"
        }
      },
      "required": []
    }
  },
  {
    "name": "email_extract_otp",
    "description": "Searches recent emails and extracts OTP/verification codes",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "account": {
          "type": "STRING",
          "description": "Email account: primary or secondary"
        }
      },
      "required": []
    }
  },
  {
    "name": "email_search",
    "description": "Searches emails by subject and returns matching results",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Search query for email subjects"
        },
        "count": {
          "type": "INTEGER",
          "description": "Max results to return"
        },
        "account": {
          "type": "STRING",
          "description": "Email account: primary or secondary"
        }
      },
      "required": []
    }
  },
  {
    "name": "email_detect_phishing",
    "description": "Analyzes an email for phishing indicators using AI and gives SAFE/SUSPICIOUS/DANGEROUS verdict",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "index": {
          "type": "INTEGER",
          "description": "Email index to analyze (1=newest)"
        },
        "account": {
          "type": "STRING",
          "description": "Email account: primary or secondary"
        }
      },
      "required": []
    }
  },
  {
    "name": "web_agent",
    "description": "Autonomous web browsing agent that navigates websites and completes tasks using Chrome",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Web task to perform autonomously"
        },
        "headless": {
          "type": "BOOLEAN",
          "description": "Run browser in headless mode (default false)"
        }
      },
      "required": []
    }
  },
  {
    "name": "web_fill_form",
    "description": "Opens a webpage and fills out a form with the provided field values",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "URL of the form to fill"
        },
        "fields": {
          "type": "STRING",
          "description": "JSON string of field name-value pairs to fill"
        }
      },
      "required": []
    }
  },
  {
    "name": "web_scrape",
    "description": "Opens a URL and extracts specific information using AI analysis",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "URL to scrape"
        },
        "what": {
          "type": "STRING",
          "description": "What specific information to extract"
        }
      },
      "required": []
    }
  },
  {
    "name": "web_search",
    "description": "Performs a web search and returns concise result snippets with URLs",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Search query"
        },
        "max_results": {
          "type": "INTEGER",
          "description": "Maximum number of results to return"
        }
      },
      "required": []
    }
  },
  {
    "name": "spawn_subagent",
    "description": "Spawns an autonomous background subagent to execute a task in parallel",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "task": {
          "type": "STRING",
          "description": "Task description for the subagent to execute"
        },
        "agent_type": {
          "type": "STRING",
          "description": "Type: research, automation, email, web, homework, general"
        }
      },
      "required": []
    }
  },
  {
    "name": "list_subagents",
    "description": "Lists all spawned subagents with their ID, type, status, and task preview",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_subagent_result",
    "description": "Gets the result of a completed subagent or checks its current status",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "agent_id": {
          "type": "STRING",
          "description": "The 8-character subagent ID"
        }
      },
      "required": []
    }
  },
  {
    "name": "kill_subagent",
    "description": "Cancels a running subagent",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "agent_id": {
          "type": "STRING",
          "description": "The 8-character subagent ID to cancel"
        }
      },
      "required": []
    }
  },
  {
    "name": "wait_for_subagents",
    "description": "Waits for subagents to finish and returns their combined results",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "agent_ids": {
          "type": "STRING",
          "description": "Comma-separated agent IDs to wait for, or empty for all"
        },
        "timeout": {
          "type": "INTEGER",
          "description": "Max seconds to wait (default 45)"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_scan_devices",
    "description": "Scans for connected ESP32, Arduino, and USB microcontrollers",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "esp32_send_command",
    "description": "Sends a command to an ESP32 via USB Serial or network",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "COM port or IP address of ESP32"
        },
        "command": {
          "type": "STRING",
          "description": "Command to send"
        },
        "baudrate": {
          "type": "INTEGER",
          "description": "Serial baud rate (default 115200)"
        },
        "timeout": {
          "type": "NUMBER",
          "description": "Response timeout in seconds"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_control_gpio",
    "description": "Controls an ESP32 GPIO pin for LED, relay, or sensor control",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "COM port or IP"
        },
        "pin": {
          "type": "INTEGER",
          "description": "GPIO pin number"
        },
        "state": {
          "type": "STRING",
          "description": "Pin state: HIGH, LOW, or PWM value"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_read_sensor_data",
    "description": "Reads sensor data from an ESP32",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "COM port or IP"
        },
        "sensor_type": {
          "type": "STRING",
          "description": "Sensor type: dht, ultrasonic, light, all"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_camera_analyze",
    "description": "Captures and analyzes a frame from ESP32-CAM using AI vision",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "camera_ip": {
          "type": "STRING",
          "description": "IP address of ESP32-CAM"
        },
        "question": {
          "type": "STRING",
          "description": "Question about what the camera sees"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_generate_firmware_code",
    "description": "Generates complete production-ready Arduino C++ or MicroPython firmware code",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_description": {
          "type": "STRING",
          "description": "Description of the firmware project"
        },
        "wifi_ssid": {
          "type": "STRING",
          "description": "WiFi SSID for network-enabled projects"
        },
        "wifi_password": {
          "type": "STRING",
          "description": "WiFi password"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_direct_upload",
    "description": "Compiles and uploads firmware to an ESP32 in one step",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code_or_prompt": {
          "type": "STRING",
          "description": "Code to upload or natural language description of desired firmware"
        },
        "port": {
          "type": "STRING",
          "description": "COM port (auto for auto-detect)"
        },
        "board_type": {
          "type": "STRING",
          "description": "Board type: esp32, esp8266, arduino"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_flash_firmware",
    "description": "Flashes a compiled firmware binary to an ESP32",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "STRING",
          "description": "COM port (auto for auto-detect)"
        },
        "binary_path": {
          "type": "STRING",
          "description": "Path to .bin firmware file"
        },
        "baudrate": {
          "type": "INTEGER",
          "description": "Flash baud rate"
        },
        "chip": {
          "type": "STRING",
          "description": "Chip type: esp32, esp8266"
        }
      },
      "required": []
    }
  },
  {
    "name": "esp32_upload_micropython",
    "description": "Uploads a MicroPython script to ESP32 or Raspberry Pi Pico",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "script_code": {
          "type": "STRING",
          "description": "Python/MicroPython code to upload"
        },
        "port": {
          "type": "STRING",
          "description": "COM port"
        },
        "filename": {
          "type": "STRING",
          "description": "Filename on device (default main.py)"
        }
      },
      "required": []
    }
  },
  {
    "name": "send_telegram_message",
    "description": "Sends a message to your Telegram account",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "message": {
          "type": "STRING",
          "description": "Message text to send"
        },
        "chat_id": {
          "type": "STRING",
          "description": "Telegram chat ID (optional, uses default)"
        }
      },
      "required": []
    }
  },
  {
    "name": "start_telegram_bridge",
    "description": "Starts the 2-way Telegram Remote Control Bridge for ULTRON",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "stop_telegram_bridge",
    "description": "Stops the Telegram bridge listener",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "toggle_hand_gesture_mouse",
    "description": "Toggles touchless hand gesture mouse control using webcam",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "enable": {
          "type": "BOOLEAN",
          "description": "True to enable, False to disable, omit to toggle"
        }
      },
      "required": []
    }
  },
  {
    "name": "inspect_live_packet_stream",
    "description": "Captures and parses live network packets showing IPs, protocols, and payload previews",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "packet_count": {
          "type": "INTEGER",
          "description": "Number of packets to capture (default 15)"
        }
      },
      "required": []
    }
  },
  {
    "name": "detect_wifi_threats_and_deauth",
    "description": "Scans for rogue WiFi access points and evil twin attacks",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "open_application",
    "description": "Launches any installed desktop app, system tool, or website by name",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "app_name": {
          "type": "STRING",
          "description": "Name of the application to launch"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_daily_briefing",
    "description": "Generates a full morning briefing with time, events, weather, and birthday status",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "list_upcoming_events",
    "description": "Lists all saved upcoming events, competitions, and deadlines",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "delete_upcoming_event",
    "description": "Deletes a scheduled event from the calendar",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "event_name": {
          "type": "STRING",
          "description": "Name of the event to delete"
        }
      },
      "required": []
    }
  },
  {
    "name": "add_upcoming_event",
    "description": "Adds a new event, competition, or deadline to the calendar",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "event_name": {
          "type": "STRING",
          "description": "Name of the event"
        },
        "event_date": {
          "type": "STRING",
          "description": "Date (e.g. 2025-03-15)"
        },
        "event_time": {
          "type": "STRING",
          "description": "Time (e.g. 14:00)"
        },
        "description": {
          "type": "STRING",
          "description": "Event description"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_my_live_location",
    "description": "Returns the current live GPS location with coordinates",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "show_live_location_map",
    "description": "Generates an interactive map of the current location",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "set_my_location",
    "description": "Manually sets and locks the current physical location",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "location_name": {
          "type": "STRING",
          "description": "Location name to set (e.g. NMIMS Shirpur Campus)"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_local_weather_forecast",
    "description": "Gets real-time weather and forecast for a city",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "city": {
          "type": "STRING",
          "description": "City name (optional, defaults to current location)"
        }
      },
      "required": []
    }
  },
  {
    "name": "list_timers",
    "description": "Lists all active timers and alarms",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "check_subagent_progress",
    "description": "Returns the real-time visual progress bar, completion percentage (e.g. 90%), current execution stage, and elapsed time for running and completed subagents.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "agent_id": {
          "type": "STRING",
          "description": "The optional 8-character subagent ID to check progress for. Leave blank to check all active subagents."
        }
      },
      "required": []
    }
  },
  {
    "name": "kill_process_by_port",
    "description": "Terminates rogue processes or servers blocking a specific network port (e.g. 3000, 8080, 5000)",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": {
          "type": "INTEGER",
          "description": "Network port number to liberate (e.g. 3000, 8080)"
        }
      },
      "required": [
        "port"
      ]
    }
  },
  {
    "name": "system_telemetry_boost",
    "description": "Purges RAM standby working sets, clears temporary caches, and maximizes Windows CPU power plan",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "bluetooth_device_switch",
    "description": "Discovers, connects, or disconnects paired Bluetooth audio and peripheral devices",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "device_name": {
          "type": "STRING",
          "description": "Name of the Bluetooth device (e.g. AirPods, Headphones, Phone)"
        },
        "action": {
          "type": "STRING",
          "description": "Action to perform: connect, disconnect, or list"
        }
      },
      "required": []
    }
  },
  {
    "name": "brightness_and_night_light_toggle",
    "description": "Adjusts screen brightness level (0-100) and toggles Windows Night Light eye protection mode",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "level": {
          "type": "INTEGER",
          "description": "Screen brightness percentage (0-100)"
        },
        "night_mode": {
          "type": "BOOLEAN",
          "description": "Set true to enable night light warm color balance"
        }
      },
      "required": []
    }
  },
  {
    "name": "network_speedtest_fast",
    "description": "Performs real-time network speed test measuring ping latency, download speed, and upload throughput",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "local_subnet_scanner",
    "description": "Scans local Wi-Fi / LAN to discover all active connected devices, IP addresses, and hostnames",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "subnet": {
          "type": "STRING",
          "description": "Optional subnet base to scan (e.g. 192.168.1)"
        }
      },
      "required": []
    }
  },
  {
    "name": "public_ip_and_vpn_check",
    "description": "Queries public WAN IP, ISP, geolocation coordinates, and verifies VPN Proxy detection status",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "cloud_file_upload_transfer",
    "description": "Uploads any local file to secure cloud storage and returns an instant shareable download link",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Absolute path to the local file to upload"
        }
      },
      "required": [
        "file_path"
      ]
    }
  },
  {
    "name": "youtube_video_downloader_and_mp3",
    "description": "Downloads high-resolution 1080p/4K YouTube videos or extracts 320kbps MP3 audio directly to PC",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "YouTube video URL"
        },
        "extract_audio": {
          "type": "BOOLEAN",
          "description": "Set true to extract high-bitrate MP3 audio instead of video"
        }
      },
      "required": [
        "url"
      ]
    }
  },
  {
    "name": "voice_memo_transcribe_and_summarize",
    "description": "Transcribes audio recordings, voice notes, or lecture files and extracts structured action items",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "audio_file": {
          "type": "STRING",
          "description": "Path to the audio recording file (.mp3, .wav, .m4a)"
        }
      },
      "required": [
        "audio_file"
      ]
    }
  },
  {
    "name": "smart_clipboard_history_search",
    "description": "Searches persistent clipboard history by keyword or returns recent copied text clips",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "keyword": {
          "type": "STRING",
          "description": "Search keyword to look up in copied history (leave empty for recent history)"
        }
      },
      "required": []
    }
  },
  {
    "name": "spotify_smart_search_and_play",
    "description": "Searches Spotify for songs, artists, albums, or mood vibes and triggers instant playback",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": {
          "type": "STRING",
          "description": "Song title, artist name, or mood vibe to search and play"
        },
        "mood": {
          "type": "STRING",
          "description": "Optional mood descriptor (e.g. focus, chill, workout, coding)"
        }
      },
      "required": [
        "query"
      ]
    }
  },
  {
    "name": "identify_person_in_camera",
    "description": "Instantly captures camera frame and identifies who is in front of the camera, their features, clothing, and activity",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "question": {
          "type": "STRING",
          "description": "Specific question about the person in camera (e.g. Who is this?, What is he wearing?)"
        }
      },
      "required": []
    }
  },
  {
    "name": "capture_fast_camera_image",
    "description": "Captures sub-second high-resolution webcam image and generates multimodal scene analysis",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": {
          "type": "STRING",
          "description": "Description prompt for analyzing the captured camera scene"
        }
      },
      "required": []
    }
  },
  {
    "name": "who_is_in_camera",
    "description": "Instant convenience trigger to look at webcam and tell who is in front of the camera right now",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "web_screenshot",
    "description": "Captures a full high-resolution browser screenshot of any webpage",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "URL of the webpage to capture"
        },
        "save_path": {
          "type": "STRING",
          "description": "Optional local path to save the screenshot image"
        }
      },
      "required": [
        "url"
      ]
    }
  },
  {
    "name": "web_deep_research",
    "description": "Conducts multi-source deep web research on any topic and synthesizes an intelligence report",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "topic": {
          "type": "STRING",
          "description": "Research topic, question, or technology to investigate"
        }
      },
      "required": [
        "topic"
      ]
    }
  },
  {
    "name": "verify_face_identity",
    "description": "Scans live webcam and verifies if the person is the registered master owner, Shivansh",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "face_lock_scan",
    "description": "Performs instant biometric face scan; locks Windows workstation immediately if an unrecognized person is detected",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "face_lock_guard",
    "description": "Enables or disables autonomous background face security sentry guard that locks PC if an intruder approaches",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "action": {
          "type": "STRING",
          "description": "Action: 'start' (enable sentry), 'stop' (disable sentry), or 'status'"
        },
        "interval": {
          "type": "INTEGER",
          "description": "Scan interval in seconds (default 15)"
        }
      },
      "required": []
    }
  },
  {
    "name": "open_code",
    "description": "High-precision smart code editor. Reads target file, applies intelligent code edits or exact snippet replacements, verifies AST syntax, creates backups, and synchronizes across environments.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Path or module name of the code file to edit (e.g. 'window_manager.py', 'ui.py', 'tools.py')"
        },
        "instruction": {
          "type": "STRING",
          "description": "Natural language instruction describing the exact logic change or bug fix"
        },
        "code": {
          "type": "STRING",
          "description": "Full replacement code (optional)"
        },
        "target_snippet": {
          "type": "STRING",
          "description": "Exact existing code snippet to replace (optional)"
        },
        "replacement_snippet": {
          "type": "STRING",
          "description": "Exact replacement code for target_snippet (optional)"
        }
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "read_code_file",
    "description": "Reads a code file with line numbers and structure for accurate inspection before making edits.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Path or module name of file to read (e.g. 'window_manager.py')"
        },
        "start_line": {
          "type": "INTEGER",
          "description": "Starting line number (1-indexed)"
        },
        "end_line": {
          "type": "INTEGER",
          "description": "Ending line number (-1 for all)"
        }
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "window_close",
    "description": "Closes an open application window, browser tab, or active foreground window matching target query.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "Name or title of window/tab to close (e.g. 'chatgpt', 'chrome', 'antigravity', 'active', 'notepad')"
        }
      },
      "required": []
    }
  },
  {
    "name": "side_by_side",
    "description": "Positions two application windows side-by-side on the screen (50% left and 50% right split screen).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "primary_app": {
          "type": "STRING",
          "description": "Name or title of application to place on the left (e.g. 'antigravity', 'code', 'chrome', 'active')"
        },
        "secondary_app": {
          "type": "STRING",
          "description": "Name or title of application to place on the right (e.g. 'chrome', 'edge', 'terminal')"
        }
      },
      "required": []
    }
  },
  {
    "name": "window_snap_layout",
    "description": "Arranges open application windows into predefined workstation layouts ('side_by_side', 'focus', 'grid', 'code_and_browser').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "layout": {
          "type": "STRING",
          "description": "Layout preset: 'side_by_side', 'focus', 'grid', 'code_and_browser'"
        },
        "primary_app": {
          "type": "STRING",
          "description": "Primary application title or process"
        },
        "secondary_app": {
          "type": "STRING",
          "description": "Secondary application title or process"
        }
      },
      "required": []
    }
  },
  {
    "name": "window_snap_to",
    "description": "Snaps a specific window or active application to a screen position (left, right, top, bottom, maximize, minimize, center).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "window": {
          "type": "STRING",
          "description": "Name or title of application window (e.g. 'chrome', 'vscode', 'antigravity', 'active')"
        },
        "position": {
          "type": "STRING",
          "description": "Target screen position: 'left', 'right', 'top', 'bottom', 'maximize', 'minimize', 'center'"
        }
      },
      "required": ["position"]
    }
  },
  {
    "name": "activate_workspace_mode",
    "description": "Activates an intelligent workstation layout preset tailored for Development (with Antigravity), Deep Focus, Gaming, Media, or Research.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mode": {
          "type": "STRING",
          "description": "Workspace preset mode: 'dev_mode', 'focus_mode', 'gaming_mode', 'media_mode', 'research_mode', 'reading_mode'"
        }
      },
      "required": ["mode"]
    }
  },
  {
    "name": "list_workspace_modes",
    "description": "Returns a list of all available workstation preset modes and their layout behaviors.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "auto_diagnose_and_heal_error",
    "description": "Autonomously diagnoses a Python stack trace or command error, inspects affected source code, and applies an AST-verified repair.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "error_trace": {
          "type": "STRING",
          "description": "Full or partial error traceback string / stderr"
        },
        "target_file": {
          "type": "STRING",
          "description": "Optional path of the broken source file"
        }
      },
      "required": ["error_trace"]
    }
  },
  {
    "name": "check_file_syntax_health",
    "description": "Inspects a Python file for AST syntax health, undefined imports, and structure errors.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Path to Python source file to inspect"
        }
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "arm_sentry_mode",
    "description": "Arms ULTRON Sentry Defense: monitors the webcam for unauthorized faces, captures evidence, emails an alert, and locks workstation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration_minutes": {
          "type": "INTEGER",
          "description": "How many minutes to stay actively armed (default: 60)"
        },
        "notify_email": {
          "type": "STRING",
          "description": "Email address to send intruder photo evidence to (default: shivamogh.12@gmail.com)"
        }
      },
      "required": []
    }
  },
  {
    "name": "disarm_sentry_mode",
    "description": "Disarms the active Sentry Defense camera surveillance.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "stealth_duress_lock",
    "description": "Discreetly minimizes all windows, purges temporary clipboard, and displays lock screen.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "transcribe_meeting_audio",
    "description": "Transcribes audio from a meeting or voice recording and generates structured minutes, key takeaways, and action items.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "audio_path": {
          "type": "STRING",
          "description": "Path to .mp3, .wav, or .m4a recording file (optional)"
        },
        "meeting_title": {
          "type": "STRING",
          "description": "Title or topic of the meeting"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_latest_meeting_summary",
    "description": "Returns the most recent meeting notes and action items.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "generate_fullstack_project",
    "description": "Generates a complete, production-ready React/Vite/Tailwind and FastAPI full-stack application from a description.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_name": {
          "type": "STRING",
          "description": "Name of the project directory (e.g. 'cyber_dashboard', 'ai_resume_builder')"
        },
        "description": {
          "type": "STRING",
          "description": "Comprehensive description of features, UI, and data models"
        },
        "template": {
          "type": "STRING",
          "description": "Project template: 'fastapi-react', 'python-cli', 'html5-app'"
        }
      },
      "required": ["project_name", "description"]
    }
  },
  {
    "name": "list_user_projects",
    "description": "Lists all projects generated in the user's Projects directory.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "git_smart_commit",
    "description": "Analyzes staged/unstaged changes in a Git repository, generates a conventional semantic commit message, and commits.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "repo_path": {
          "type": "STRING",
          "description": "Root directory of Git repository"
        },
        "auto_push": {
          "type": "BOOLEAN",
          "description": "If True, pushes the commit to origin main/master"
        },
        "custom_hint": {
          "type": "STRING",
          "description": "Optional guidance on what was changed"
        }
      },
      "required": []
    }
  },
  {
    "name": "git_review_changes",
    "description": "Provides an AI-powered code review and risk analysis of all uncommitted Git changes.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "repo_path": {
          "type": "STRING",
          "description": "Root directory of Git repository"
        }
      },
      "required": []
    }
  },
  {
    "name": "start_ambient_watcher",
    "description": "Starts the proactive zero-prompt ambient watcher daemon in the background.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "interval_seconds": {
          "type": "INTEGER",
          "description": "Check interval in seconds (default: 30)"
        }
      },
      "required": []
    }
  },
  {
    "name": "stop_ambient_watcher",
    "description": "Stops the ambient watcher daemon.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "send_wake_on_lan",
    "description": "Sends a Wake-on-LAN magic packet to remotely power on a PC or device on the local network.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "mac_address": {
          "type": "STRING",
          "description": "Target MAC address (e.g. 'AA:BB:CC:DD:EE:FF')"
        }
      },
      "required": ["mac_address"]
    }
  },
  {
    "name": "ping_network_device",
    "description": "Pings a network host or smart device IP to verify online/offline status and latency.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "host": {
          "type": "STRING",
          "description": "IP address or hostname"
        }
      },
      "required": ["host"]
    }
  },
  {
    "name": "toggle_dynamic_island",
    "description": "Toggles the floating, frameless Dynamic Island telemetry pill on the top of the monitor.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "visible": {
          "type": "BOOLEAN",
          "description": "True to display the floating HUD pill, False to hide"
        }
      },
      "required": []
    }
  },
  {
    "name": "trigger_jarvis_sfx",
    "description": "Plays high-tech JARVIS UI sound effect ('chime', 'success', 'alert', 'whoosh', 'lock', 'scan').",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "sound_effect": {
          "type": "STRING",
          "description": "Sound type: 'chime', 'success', 'alert', 'whoosh', 'lock', 'scan'"
        }
      },
      "required": ["sound_effect"]
    }
  },
  {
    "name": "switch_window",
    "description": "Switches focus between open desktop application windows (real Windows Alt+Tab / App Switcher), or activates a specific app like 'chrome', 'antigravity', 'vscode', 'terminal', 'notepad'.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target": {
          "type": "STRING",
          "description": "'next' (or 'cycle' / 'alt_tab' to switch to next active window), or specific app name (e.g. 'chrome', 'antigravity', 'vscode', 'terminal', 'notepad')"
        }
      },
      "required": []
    }
  },
  {
    "name": "switch_app",
    "description": "Switches focus to another desktop application (e.g. 'chrome', 'antigravity', 'vscode', 'terminal', 'notepad') or cycles to next open window.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "app": {
          "type": "STRING",
          "description": "Application name to switch to (e.g. 'chrome', 'antigravity', 'vscode', 'terminal', 'notepad', or 'next')"
        }
      },
      "required": []
    }
  },
  {
    "name": "alt_tab",
    "description": "Performs Windows OS Alt+Tab window cycling across open desktop applications.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "switch_tab",
    "description": "Switches tabs within the active application (browser or code editor) via Ctrl+Tab or Ctrl+Shift+Tab.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "direction": {
          "type": "STRING",
          "description": "'next' for forward tab, 'prev' or 'back' for previous tab"
        }
      },
      "required": []
    }
  },
  {
    "name": "focus_window",
    "description": "Brings a specific application window or document to the foreground.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "app_or_title": {
          "type": "STRING",
          "description": "Application name or window title to focus"
        }
      },
      "required": ["app_or_title"]
    }
  },
  {
    "name": "get_stock_quote",
    "description": "Fetches real-time market quote, day range, volume, 52-week range, and P/E ratio for any global stock or index.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "symbol": {
          "type": "STRING",
          "description": "Ticker symbol (e.g. 'AAPL', 'NVDA', 'TSLA', 'RELIANCE.NS', 'BTC-USD')"
        }
      },
      "required": ["symbol"]
    }
  },
  {
    "name": "get_crypto_ticker",
    "description": "Fetches live cryptocurrency prices (USD & INR), 24h high/low, volume, and market stats.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "coin": {
          "type": "STRING",
          "description": "Coin name or symbol (e.g. 'bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'xrp')"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_market_technical_analysis",
    "description": "Computes technical indicators (SMA-20, SMA-50, RSI 14, MACD, Bollinger Bands) and provides an AI technical outlook.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "symbol": {
          "type": "STRING",
          "description": "Stock or Crypto ticker (e.g. 'NVDA', 'AAPL', 'TSLA', 'BTC-USD')"
        },
        "period": {
          "type": "STRING",
          "description": "Timeframe ('1mo', '3mo', '6mo', '1y')"
        }
      },
      "required": ["symbol"]
    }
  },
  {
    "name": "get_market_overview",
    "description": "Provides a real-time macro overview of key global market indices, commodities, and benchmark cryptos.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "set_price_alert",
    "description": "Sets an automated threshold alert for a stock or cryptocurrency.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "symbol": {
          "type": "STRING",
          "description": "Ticker symbol (e.g. 'NVDA', 'BTC', 'TSLA')"
        },
        "target_price": {
          "type": "NUMBER",
          "description": "Trigger price number"
        },
        "condition": {
          "type": "STRING",
          "description": "'above' or 'below'"
        }
      },
      "required": ["symbol", "target_price"]
    }
  },
  {
    "name": "generate_executive_dossier",
    "description": "Synthesizes exhaustive intelligence on any topic and compiles a formatted, multi-page Executive Dossier PDF.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "topic": {
          "type": "STRING",
          "description": "The subject, technology, market sector, architecture, or entity to investigate"
        },
        "filename": {
          "type": "STRING",
          "description": "Optional output filename (e.g. 'quantum_computing.pdf')"
        },
        "depth": {
          "type": "STRING",
          "description": "'deep', 'executive_summary', or 'technical_whitepaper'"
        }
      },
      "required": ["topic"]
    }
  },
  {
    "name": "generate_project_architecture_pdf",
    "description": "Creates a formal Software & Systems Architecture Whitepaper PDF for a software or hardware project.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_name": {
          "type": "STRING",
          "description": "Name of the project"
        },
        "tech_stack": {
          "type": "STRING",
          "description": "Technology stack"
        },
        "description": {
          "type": "STRING",
          "description": "Overview description"
        }
      },
      "required": ["project_name"]
    }
  },
  {
    "name": "enroll_voiceprint",
    "description": "CRITICAL: STRICTLY ONLY call when the user gives an explicit direct command like 'enroll my voice now' or 'setup voiceprint profile'. DO NOT call automatically or during general chat.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "profile_name": {
          "type": "STRING",
          "description": "Name of the voice profile (default: 'shivansh')"
        },
        "duration_seconds": {
          "type": "INTEGER",
          "description": "Recording duration in seconds (1 to 3)"
        }
      },
      "required": []
    }
  },
  {
    "name": "verify_speaker_voice",
    "description": "CRITICAL: STRICTLY ONLY call when user explicitly asks 'verify my voice' or 'check voice biometric'. DO NOT call automatically.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration_seconds": {
          "type": "INTEGER",
          "description": "Recording duration in seconds (1 to 3)"
        },
        "threshold": {
          "type": "NUMBER",
          "description": "Match threshold between 0.0 and 1.0"
        }
      },
      "required": []
    }
  },
  {
    "name": "toggle_voice_biometric_gate",
    "description": "Enables or disables continuous voiceprint biometric security gate for ULTRON.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "enabled": {
          "type": "BOOLEAN",
          "description": "True to activate biometric gate, False to deactivate"
        }
      },
      "required": []
    }
  },
  {
    "name": "get_voiceprint_status",
    "description": "Returns the status of enrolled voice profiles and biometric authentication parameters.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "analyze_file",
    "description": "Analyzes any uploaded or local file (image, PDF, code, document, dataset) using multi-modal AI intelligence.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Absolute or relative file path to analyze"
        },
        "instruction": {
          "type": "STRING",
          "description": "Specific instruction, query, or task for the file"
        }
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "osint_username_scan",
    "description": "Deep OSINT tool that scans 30+ social media platforms, forums, and developer networks for a username or online alias.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "username": {
          "type": "STRING",
          "description": "The target username or alias to search"
        }
      },
      "required": ["username"]
    }
  },
  {
    "name": "osint_metadata_analyze",
    "description": "Extracts hidden EXIF metadata, camera telemetry, author information, and exact GPS coordinates from images/PDFs. Optionally scrubs all metadata.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Path to the image or document file"
        },
        "scrub_exif": {
          "type": "BOOLEAN",
          "description": "Set to True to create an anonymous sanitized copy stripped of all metadata"
        }
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "osint_domain_recon",
    "description": "Performs deep domain reconnaissance: finds all subdomains via Certificate Transparency (crt.sh), resolves DNS records, inspects SSL/TLS certificates, and audits security headers.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "domain": {
          "type": "STRING",
          "description": "The target domain name (e.g. example.com)"
        }
      },
      "required": ["domain"]
    }
  },
  {
    "name": "osint_wayback_history",
    "description": "Queries the Wayback Machine to discover historical archived snapshots and changelogs of any URL.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": {
          "type": "STRING",
          "description": "Target webpage URL to inspect historical snapshots for"
        },
        "limit": {
          "type": "INTEGER",
          "description": "Maximum number of snapshots to retrieve (default 5)"
        }
      },
      "required": ["url"]
    }
  },
  {
    "name": "osint_ip_lookup",
    "description": "Performs IP/Host threat intelligence: resolves geolocation, ISP, ASN, reverse DNS, and detects proxy/hosting servers.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "ip_or_host": {
          "type": "STRING",
          "description": "Target IP address or domain hostname"
        }
      },
      "required": ["ip_or_host"]
    }
  },
  {
    "name": "osint_phone_intelligence",
    "description": "Performs phone OSINT: resolves country of origin, telecom provider/carrier, line type (Mobile/VoIP/Landline), and international validity.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "phone_number": {
          "type": "STRING",
          "description": "Phone number with international country code (e.g. +14155552671 or +919876543210)"
        }
      },
      "required": ["phone_number"]
    }
  },
  {
    "name": "osint_precision_geocoder",
    "description": "Precision Geocoding Engine (Phantom-IP): converts any physical street address, city, or landmark into exact GPS coordinates, bounding box, postal details, and interactive map links.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "address": {
          "type": "STRING",
          "description": "Physical street address, city, landmark, or location query"
        }
      },
      "required": ["address"]
    }
  },
  {
    "name": "osint_deep_holder_trace",
    "description": "Deep Holder & Ownership Tracer (Phantom-IP): analyzes website owner identity, server geography, HTML contact forensics (emails, phones, social links, copyright), and registrar WHOIS/RDAP records.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_domain_or_url": {
          "type": "STRING",
          "description": "Target domain or website URL to trace"
        }
      },
      "required": ["target_domain_or_url"]
    }
  },
  {
    "name": "security_vulnerability_and_fuzzer_scan",
    "description": "Phantom-IP Vulnerability & Endpoint Security Auditor: audits target for critical exposed files (.env, .git, config.json, backups), admin dashboards, API documentation, open service ports, and posture risk.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_domain_or_url": {
          "type": "STRING",
          "description": "Target domain or URL to audit for vulnerabilities and exposed endpoints"
        }
      },
      "required": ["target_domain_or_url"]
    }
  },
  {
    "name": "chess_tiger_analyze_fen",
    "description": "ULTRON Chess-Tiger: Deep tactical and positional FEN evaluator. Calculates material balance, center control, tactical motifs (pins/forks/skewers), hanging pieces, and strategic candidate moves with spoken TTS feedback.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "fen": {
          "type": "STRING",
          "description": "Standard FEN chess position string"
        },
        "speak": {
          "type": "BOOLEAN",
          "description": "Whether to vocalize key move evaluation via spoken TTS"
        }
      },
      "required": ["fen"]
    }
  },
  {
    "name": "chess_tiger_best_move",
    "description": "ULTRON Chess-Tiger: Returns the single best candidate move in algebraic notation (e.g. Nf3, Qh5, O-O) with tactical reasoning.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "fen": {
          "type": "STRING",
          "description": "Standard FEN chess position string"
        }
      },
      "required": ["fen"]
    }
  },
  {
    "name": "chess_tiger_opening_explorer",
    "description": "ULTRON Chess-Tiger: Grandmaster Opening Repertoire Coach. Returns opening lines, ECO classification, strategic plans, and tactical traps for any opening.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "opening_name_or_moves": {
          "type": "STRING",
          "description": "Opening name or move sequence (e.g. 'Sicilian Najdorf', 'Ruy Lopez', 'Queen\'s Gambit', 'London System')"
        }
      },
      "required": ["opening_name_or_moves"]
    }
  },
  {
    "name": "chess_tiger_game_review",
    "description": "ULTRON Chess-Tiger: PGN game reviewer. Analyzes game score, accuracy %, brilliant moves, inaccuracies, and blunders.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "pgn_or_moves": {
          "type": "STRING",
          "description": "Full PGN game notation or move list"
        }
      },
      "required": ["pgn_or_moves"]
    }
  },
  {
    "name": "chess_tiger_solve_puzzle",
    "description": "ULTRON Chess-Tiger: Tactical puzzle engine. Solves tactical positions (forks, pins, back-rank mate, deflection) step-by-step.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "puzzle_theme_or_fen": {
          "type": "STRING",
          "description": "Tactical theme or specific puzzle FEN"
        }
      },
      "required": []
    }
  },
  {
    "name": "chess_tiger_scan_screen",
    "description": "ULTRON Chess-Tiger Screen Vision: Captures screen, identifies active chessboard on Chess.com / Lichess, and calculates the winning move.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "forge_create_feature",
    "description": "ULTRON CODE-FORGE: Autonomous multi-file project and feature synthesizer. Generates full directory trees, modules, interfaces, and unit tests directly to disk.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": {
          "type": "STRING",
          "description": "Feature, module, or full system requirements specification"
        },
        "project_dir": {
          "type": "STRING",
          "description": "Target project directory path (default: current directory)"
        }
      },
      "required": ["prompt"]
    }
  },
  {
    "name": "forge_auto_debug",
    "description": "ULTRON CODE-FORGE: Autonomous self-healing execution loop. Runs scripts/commands in a sandbox, intercepts traceback errors, applies surgical AI code patches, and re-verifies until fixed.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_script_or_command": {
          "type": "STRING",
          "description": "Target Python script file path or command to execute and debug"
        },
        "max_rounds": {
          "type": "INTEGER",
          "description": "Maximum auto-repair iterations (default: 5)"
        }
      },
      "required": ["target_script_or_command"]
    }
  },
  {
    "name": "forge_test_suite",
    "description": "ULTRON CODE-FORGE: Automated test suite runner (pytest/unittest). Aggregates test passes, failures, durations, and diagnostics.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "project_path": {
          "type": "STRING",
          "description": "Project directory or test file path"
        },
        "runner": {
          "type": "STRING",
          "description": "Test runner: 'pytest' or 'unittest'"
        }
      },
      "required": []
    }
  },
  {
    "name": "forge_code_audit_and_refactor",
    "description": "ULTRON CODE-FORGE: Senior AST static auditor & clean refactor engine. Checks syntax, security vulnerabilities (eval/secrets), complexity, and outputs clean production code.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": {
          "type": "STRING",
          "description": "Target source code file path to audit and refactor"
        }
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "forge_git_smart_commit",
    "description": "ULTRON CODE-FORGE: Intelligent Git commit manager. Analyzes diffs, generates Conventional Commit messages (feat/fix/refactor), stages changes, and commits.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "repo_dir": {
          "type": "STRING",
          "description": "Target Git repository path"
        },
        "custom_message": {
          "type": "STRING",
          "description": "Optional custom commit message override"
        }
      },
      "required": []
    }
  },
  {
    "name": "chronos_schedule_agenda_block",
    "description": "ULTRON Chronos: Schedules a dynamic time block in the daily agenda matrix with category tags and overlap calculation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "title": { "type": "STRING", "description": "Title of the task or event" },
        "start_time": { "type": "STRING", "description": "Start time (e.g. '16:00', '4:30 PM')" },
        "duration_minutes": { "type": "INTEGER", "description": "Duration in minutes (default: 45)" },
        "category": { "type": "STRING", "description": "Category (Deep Work, Study, Chess, Meeting, Rest)" },
        "description": { "type": "STRING", "description": "Optional details or goals" }
      },
      "required": ["title", "start_time"]
    }
  },
  {
    "name": "chronos_get_daily_agenda",
    "description": "ULTRON Chronos: Returns full day's synthesized timeline matrix with actionable executive buffer advice.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_date": { "type": "STRING", "description": "Target date: 'today' or 'tomorrow'" }
      },
      "required": []
    }
  },
  {
    "name": "chronos_resolve_conflicts",
    "description": "ULTRON Chronos: Analyzes agenda for tight turnarounds, scheduling overlaps, and outputs optimal re-scheduled timeline.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "target_date": { "type": "STRING", "description": "Target date" }
      },
      "required": []
    }
  },
  {
    "name": "chronos_set_circadian_alarm",
    "description": "ULTRON Chronos: Arms a circadian wakeup alarm that triggers customized spoken morning briefings, weather, and audio escalation.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "wake_time": { "type": "STRING", "description": "Target alarm time (e.g. '07:00 AM')" },
        "wake_routine": { "type": "BOOLEAN", "description": "Whether to deliver spoken daily briefing upon waking" },
        "escalation_level": { "type": "STRING", "description": "Escalation style: 'gentle', 'medium', 'urgent'" }
      },
      "required": ["wake_time"]
    }
  },
  {
    "name": "chronos_start_focus_guardian",
    "description": "ULTRON Chronos: Activates deep flow-state guardian (adaptive Pomodoro) to log deep work velocity and shield focus.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration_minutes": { "type": "INTEGER", "description": "Focus block duration in minutes (default: 25)" },
        "block_distractions": { "type": "BOOLEAN", "description": "Whether to monitor and shield distraction" },
        "task_goal": { "type": "STRING", "description": "Specific focus objective" }
      },
      "required": []
    }
  },
  {
    "name": "chronos_daily_wrapup_briefing",
    "description": "ULTRON Chronos: Delivers spoken evening debriefing summarizing completed agenda blocks, focus hours, and tomorrow's prep.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "omni_memory_ingest",
    "description": "ULTRON Omni-Memory: Ingests text, code, URLs, or notes into the Second Brain vault with automatic secret sanitization.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "content": { "type": "STRING", "description": "Content to store in long-term semantic memory" },
        "category": { "type": "STRING", "description": "Category (Code Snippet, URL/Link, Document, Note)" },
        "metadata": { "type": "STRING", "description": "Optional metadata or source" },
        "tags": { "type": "STRING", "description": "Comma-separated search tags" }
      },
      "required": ["content"]
    }
  },
  {
    "name": "omni_memory_sync_clipboard",
    "description": "ULTRON Omni-Memory: Captures active system clipboard contents, sanitizes secrets, and indexes into memory vault.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "omni_memory_semantic_recall",
    "description": "ULTRON Omni-Memory: Performs semantic query retrieval across memory vault with spoken audio recall.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": { "type": "STRING", "description": "Natural language search query" },
        "top_k": { "type": "INTEGER", "description": "Number of top records to retrieve" },
        "category": { "type": "STRING", "description": "Optional category filter" }
      },
      "required": ["query"]
    }
  },
  {
    "name": "omni_memory_vault_summary",
    "description": "ULTRON Omni-Memory: Returns statistics, category distributions, and recent memory index records.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "omni_memory_purge_sensitive",
    "description": "ULTRON Omni-Memory: Audits memory records and scrubs any leaked API keys, tokens, or credentials.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "auto_scrub": { "type": "BOOLEAN", "description": "Whether to automatically mask detected secrets" }
      },
      "required": []
    }
  },
  {
    "name": "comms_whatsapp_send",
    "description": "ULTRON Omni-Comms: Prepares and dispatches WhatsApp messages with phone normalization and web/desktop launch.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "contact_or_number": { "type": "STRING", "description": "Phone number with country code or contact identifier" },
        "message_text": { "type": "STRING", "description": "Message content to send" },
        "auto_open": { "type": "BOOLEAN", "description": "Whether to open WhatsApp client immediately" }
      },
      "required": ["contact_or_number", "message_text"]
    }
  },
  {
    "name": "comms_whatsapp_quick_dictate",
    "description": "ULTRON Omni-Comms: Ghostwrites a polished, natural WhatsApp message based on bullet-point voice instructions.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "contact_name": { "type": "STRING", "description": "Name of contact to message" },
        "voice_note_topic": { "type": "STRING", "description": "Key points / thoughts to format" }
      },
      "required": ["contact_name", "voice_note_topic"]
    }
  },
  {
    "name": "comms_gmail_triage_unread",
    "description": "ULTRON Omni-Comms: IMAP triage scanner for Gmail. Pulls unread emails, categorizes into Urgent/Action/Updates, and provides spoken voice summary.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "max_count": { "type": "INTEGER", "description": "Maximum emails to inspect (default: 8)" },
        "account": { "type": "STRING", "description": "'primary' or 'secondary'" }
      },
      "required": []
    }
  },
  {
    "name": "comms_gmail_smart_reply",
    "description": "ULTRON Omni-Comms: Reads email context and drafts a high-standard response ready to send.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "email_index": { "type": "INTEGER", "description": "Index of email (1 = most recent)" },
        "instructions": { "type": "STRING", "description": "Custom instructions or tone for reply" },
        "account": { "type": "STRING", "description": "'primary' or 'secondary'" }
      },
      "required": []
    }
  },
  {
    "name": "comms_gmail_instant_send",
    "description": "ULTRON Omni-Comms: Sends emails instantly via Gmail SMTP SSL.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "to_email": { "type": "STRING", "description": "Recipient email address" },
        "subject": { "type": "STRING", "description": "Email subject line" },
        "body": { "type": "STRING", "description": "Email message body" },
        "account": { "type": "STRING", "description": "'primary' or 'secondary'" }
      },
      "required": ["to_email", "subject", "body"]
    }
  },
  {
    "name": "comms_gmail_extract_recent_otp",
    "description": "ULTRON Omni-Comms: Searches recent security emails for OTPs, 2FA pins, and verification codes, extracting and speaking the digits.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "account": { "type": "STRING", "description": "'primary' or 'secondary'" }
      },
      "required": []
    }
  },
  {
    "name": "get_chat_history",
    "description": "ULTRON Chat Interface: Retrieves recent messages from the right-side visual chat panel without needing screen capture or OCR.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "count": { "type": "INTEGER", "description": "Number of recent turns to retrieve (default: 10)" }
      },
      "required": []
    }
  },
  {
    "name": "get_latest_chat_message",
    "description": "ULTRON Chat Interface: Returns the single latest message sent by the user in the right-side chat panel.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "get_latest_chat_image",
    "description": "ULTRON Chat Interface: Directly inspects and analyzes the image attached or sent in the right-side chat panel with multi-modal neural vision. Fast, direct, zero screen lag.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": { "type": "STRING", "description": "Custom question or directive about the uploaded chat image" }
      },
      "required": []
    }
  },
  {
    "name": "send_chat_message",
    "description": "ULTRON Chat Interface: Dispatches a message directly into the right-side visual chat panel and vocalizes it aloud via TTS.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "message": { "type": "STRING", "description": "Message text to display in chat panel and speak aloud" }
      },
      "required": ["message"]
    }
  },
  {
    "name": "view_chat_context",
    "description": "ULTRON Chat Interface: Provides instant overview of the right-side chat panel, active messages, and any currently uploaded image or attachment.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  }
,
  {
    "name": "download_image",
    "description": "Headlessly search and download any image or picture from the web (e.g., NMIMS Shirpur, wallpaper, photo) or direct image URL to Downloads folder without opening any browser GUI.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query_or_url": { "type": "STRING", "description": "The search term or direct image URL to download" },
        "output_path": { "type": "STRING", "description": "Optional destination directory (defaults to user Downloads folder)" },
        "filename": { "type": "STRING", "description": "Optional custom filename without extension" }
      },
      "required": ["query_or_url"]
    }
  },
  {
    "name": "search_and_download_images",
    "description": "Headlessly searches and downloads multiple images for any topic/query into a dedicated Downloads folder without opening any browser GUI.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": { "type": "STRING", "description": "Search query for images" },
        "count": { "type": "INTEGER", "description": "Number of images to download (default: 3)" },
        "output_dir": { "type": "STRING", "description": "Optional target directory" }
      },
      "required": ["query"]
    }
  },
  {
    "name": "download_file",
    "description": "Headlessly downloads any file from a direct web URL with proper headers to user Downloads folder without opening any browser.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": { "type": "STRING", "description": "Direct URL of the file to download" },
        "output_path": { "type": "STRING", "description": "Optional output path or destination folder" }
      },
      "required": ["url"]
    }
  },
  {
    "name": "youtube_deep_summarize",
    "description": "ULTRON Video Intelligence: Deeply transcribes and summarizes any YouTube video by URL or topic, extracting timestamped chapter breakdowns, key takeaways, and core concepts.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url_or_topic": { "type": "STRING", "description": "YouTube video URL (or search query for the video)" },
        "focus": { "type": "STRING", "description": "Focus mode ('comprehensive', 'key_takeaways', 'technical')" }
      },
      "required": ["url_or_topic"]
    }
  },
  {
    "name": "summarize_local_video",
    "description": "ULTRON Video Intelligence: Analyzes and summarizes a local video or audio file on disk (MP4, MKV, MOV, MP3).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "file_path": { "type": "STRING", "description": "Path to the local media file" }
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "build_mermaid_diagram",
    "description": "ULTRON Visual Architecture: Generates clean Mermaid.js sequence diagrams, flowcharts, ER diagrams, class diagrams, and state charts from text prompts, automatically opening them in an interactive dark-mode HTML viewer.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": { "type": "STRING", "description": "What to diagram (e.g. 'sequence diagram of OAuth login', 'flowchart of data pipeline')" },
        "diagram_type": { "type": "STRING", "description": "Diagram type ('flowchart', 'sequenceDiagram', 'classDiagram', 'erDiagram', 'stateDiagram')" },
        "title": { "type": "STRING", "description": "Optional title for the diagram" }
      },
      "required": ["prompt"]
    }
  },
  {
    "name": "sync_drop_folder",
    "description": "ULTRON Document RAG: Scans and indexes all documents in the personal drop folder (~/Documents/ULTRON_Drop/) including PDFs, Word DOCX, Excel spreadsheets, PPTX, and code files.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "query_drop_documents",
    "description": "ULTRON Document RAG: Performs deep semantic Q&A and analysis across files dropped into ~/Documents/ULTRON_Drop/, answering queries with exact page numbers, tables, and citations.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": { "type": "STRING", "description": "Question or analysis query about your dropped files" }
      },
      "required": ["query"]
    }
  },
  {
    "name": "get_drop_folder_status",
    "description": "ULTRON Document RAG: Returns current status, file counts, and vector index summary of ~/Documents/ULTRON_Drop/.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "swarm_parallel_research",
    "description": "ULTRON Subagent Swarm: Spawns parallel background worker agents to research, evaluate, and compare multiple entities or options simultaneously across the live web, compiling a comparison matrix and exporting a styled Excel sheet (.xlsx).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "objective": { "type": "STRING", "description": "The research/comparison objective (e.g. 'Compare top 5 universities for MS in CS', 'Compare RTX 4090 vs 4080')" },
        "entities": { "type": "ARRAY", "items": { "type": "STRING" }, "description": "Optional list of specific entities to compare" },
        "export_to_excel": { "type": "BOOLEAN", "description": "Whether to generate and export an Excel (.xlsx) file (default: true)" }
      },
      "required": ["objective"]
    }
  },
  {
    "name": "phone_ring_finder",
    "description": "ULTRON Phone Bridge: Rings the connected Android phone at maximum alarm volume to find it in the room.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "phone_get_last_sms_otp",
    "description": "ULTRON Phone Bridge: Queries the connected Android phone's SMS inbox and extracts the latest 2FA verification code / OTP.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "phone_battery_status",
    "description": "ULTRON Phone Bridge: Reports battery level, temperature, and charging state of connected Android device.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "iot_smart_device_toggle",
    "description": "ULTRON Smart Home: Controls local smart home devices (WLED light strips, Tasmota smart plugs, Tuya relays).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "device_name": { "type": "STRING", "description": "Name of smart device (e.g. 'desk_lights', 'wled_strip', 'smart_plug')" },
        "action": { "type": "STRING", "description": "'on', 'off', or 'toggle'" }
      },
      "required": ["device_name"]
    }
  },
  {
    "name": "create_and_open_website",
    "description": "Generates a complete, modern, beautiful, responsive single-file HTML5/CSS3/JS website for any request, saves it, and immediately opens the live preview in your default browser and opens the code in VS Code.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "prompt": { "type": "STRING", "description": "Detailed description or theme of the website/webpage to create" },
        "title": { "type": "STRING", "description": "Optional title for the website/project" },
        "auto_open": { "type": "BOOLEAN", "description": "Automatically open the website in browser and VS Code (default true)" }
      },
      "required": ["prompt"]
    }
  },
  {
    "name": "start_mobile_satellite_server",
    "description": "Starts the ULTRON Mobile Satellite Host Server on your laptop for real-time phone-laptop neural pairing and mobile APK synchronization.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "port": { "type": "INTEGER", "description": "Local server port (default 8765)" }
      },
      "required": []
    }
  },
  {
    "name": "draft_patent_proposal",
    "description": "Drafts an official patent application document (Abstract, Claims 1-20, Field, Background, Detailed Description, Mermaid diagrams) and exports to PDF.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "title_or_idea": { "type": "STRING", "description": "Title, topic, or concept of the invention" },
        "field": { "type": "STRING", "description": "Technical field (e.g. 'AI/Computer Science', 'Biomedical', 'Hardware')" },
        "auto_pdf": { "type": "BOOLEAN", "description": "Automatically compile into PDF file" }
      },
      "required": ["title_or_idea"]
    }
  },
  {
    "name": "search_prior_art",
    "description": "Searches for prior art patents and academic publications related to an invention or idea.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "query": { "type": "STRING", "description": "Invention concept or query to search" },
        "count": { "type": "INTEGER", "description": "Number of results to retrieve" }
      },
      "required": ["query"]
    }
  },
  {
    "name": "draft_phd_proposal",
    "description": "Drafts an academic PhD Dissertation Proposal & Research Plan with auto-PDF export.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "topic": { "type": "STRING", "description": "PhD research topic or domain" },
        "methodology": { "type": "STRING", "description": "Methodology or approach" },
        "auto_pdf": { "type": "BOOLEAN", "description": "Auto compile into PDF file" }
      },
      "required": ["topic"]
    }
  },
  {
    "name": "run_code",
    "description": "Executes code snippets in Python, JavaScript/Node, PowerShell, or Batch and returns stdout/stderr.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code": { "type": "STRING", "description": "Code string to execute" },
        "language": { "type": "STRING", "description": "'python', 'javascript', 'powershell', or 'batch'" },
        "timeout": { "type": "INTEGER", "description": "Execution timeout in seconds" }
      },
      "required": ["code"]
    }
  },
  {
    "name": "execute_and_auto_debug",
    "description": "Autonomous Self-Healing Execution Loop: Runs code, inspects tracebacks, auto-fixes bugs with AI, and re-runs until successful.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "code": { "type": "STRING", "description": "Code to run and auto-fix" },
        "language": { "type": "STRING", "description": "Programming language" },
        "max_retries": { "type": "INTEGER", "description": "Maximum fix attempts" }
      },
      "required": ["code"]
    }
  },
  {
    "name": "youtube_summarize",
    "description": "Summarizes any YouTube video into an executive breakdown, key insights, and actionable timestamps.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": { "type": "STRING", "description": "YouTube video URL or Video ID" },
        "detail_level": { "type": "STRING", "description": "'concise', 'comprehensive', or 'bullet_points'" }
      },
      "required": ["url"]
    }
  },
  {
    "name": "youtube_ask_question",
    "description": "Answers specific questions regarding what was spoken in a YouTube video by querying its transcript.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": { "type": "STRING", "description": "YouTube video URL" },
        "question": { "type": "STRING", "description": "Question to ask about the video content" }
      },
      "required": ["url", "question"]
    }
  },
  {
    "name": "youtube_download_audio",
    "description": "Downloads high-quality audio (MP3) from a YouTube video.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "url": { "type": "STRING", "description": "YouTube video URL" },
        "filename": { "type": "STRING", "description": "Optional output filename" }
      },
      "required": ["url"]
    }
  },
  {
    "name": "screen_ocr_read",
    "description": "Instantly extracts non-selectable text, tables, or code from the current screen via Vision AI.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "focus": { "type": "STRING", "description": "What to focus on extracting (e.g. 'code', 'error message', 'all text')" }
      },
      "required": []
    }
  },
  {
    "name": "screen_detect_and_fix_error",
    "description": "Scans current screen for compiler errors or terminal failures, diagnoses root cause, and provides exact fix.",
    "parameters": {
      "type": "OBJECT",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "meeting_take_notes",
    "description": "Captures live audio from the microphone and compiles structured Meeting Minutes (Decisions, Action Items).",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "duration_seconds": { "type": "INTEGER", "description": "Duration in seconds to listen" },
        "topic": { "type": "STRING", "description": "Meeting topic or title" }
      },
      "required": []
    }
  },
  {
    "name": "whatsapp_schedule_message",
    "description": "Schedules a WhatsApp message to be sent after a specified delay in minutes.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "recipient": { "type": "STRING", "description": "Contact name or phone number" },
        "message": { "type": "STRING", "description": "Message text to send" },
        "delay_minutes": { "type": "INTEGER", "description": "Delay in minutes before sending" }
      },
      "required": ["recipient", "message"]
    }
  },
  {
    "name": "whatsapp_smart_reply",
    "description": "Reads the last message from a contact and drafts an AI smart reply.",
    "parameters": {
      "type": "OBJECT",
      "properties": {
        "contact": { "type": "STRING", "description": "Contact name in WhatsApp" },
        "tone": { "type": "STRING", "description": "Reply tone ('friendly', 'professional', 'concise')" }
      },
      "required": ["contact"]
    }
  }
]



