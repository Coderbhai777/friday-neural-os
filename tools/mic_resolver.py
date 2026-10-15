# -*- coding: utf-8 -*-
"""
JARVIS / ULTRON Intelligent Microphone Resolver
Automatically detects and selects the active physical microphone hardware
(e.g., Intel Smart Sound Microphone Array) without modifying the Windows system default microphone.
Protects against dead or unplugged 3.5mm headset ports.
"""

from typing import Optional, Tuple


def get_best_sounddevice_input() -> Optional[int]:
    """
    Returns the device index of the active physical microphone for sounddevice.
    Prioritizes 'Microphone Array' or 'Digital Microphones' over silent headset ports.
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        # 1. Search for built-in microphone array
        for idx, d in enumerate(devices):
            if d.get("max_input_channels", 0) > 0:
                name = d.get("name", "").lower()
                if "microphone array" in name or "smart sound" in name or "digital microphone" in name:
                    return idx

        # 2. Fall back to any active input device that is not an unplugged headset
        for idx, d in enumerate(devices):
            if d.get("max_input_channels", 0) > 0:
                name = d.get("name", "").lower()
                if "headset" not in name:
                    return idx

        # 3. Default device as last resort
        return sd.default.device[0]
    except Exception:
        return None


def get_best_sr_microphone():
    """
    Returns an initialized speech_recognition.Microphone bound to the active physical microphone.
    """
    import speech_recognition as sr
    try:
        mic_names = sr.Microphone.list_microphone_names()
        best_idx = None
        
        # 1. Search for built-in microphone array
        for idx, name in enumerate(mic_names):
            lower_name = name.lower()
            if "microphone array" in lower_name or "smart sound" in lower_name or "digital microphone" in lower_name:
                best_idx = idx
                break
                
        # 2. Fall back to non-headset input
        if best_idx is None:
            for idx, name in enumerate(mic_names):
                lower_name = name.lower()
                if "headset" not in lower_name:
                    best_idx = idx
                    break
                    
        if best_idx is not None:
            return sr.Microphone(device_index=best_idx)
    except Exception:
        pass
    return sr.Microphone()
