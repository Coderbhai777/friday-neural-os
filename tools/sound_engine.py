"""
ULTRON Sound & Cyber Audio Synthesizer Engine
Generates and plays sci-fi JARVIS interface audio feedback, confirmation chimes, alert klaxons, and processing whooshes.
"""

import sys
import time
import math
import wave
import struct
import tempfile
import threading
import os
from typing import Optional

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


def _generate_tone_wav(frequencies: list, durations: list, sample_rate: int = 44100, volume: float = 0.5) -> str:
    """Generates a multi-tone harmonic WAV in memory/tempfile."""
    temp_wav = os.path.join(tempfile.gettempdir(), f"ultron_tone_{int(time.time()*1000)}.wav")
    
    total_frames = []
    for freq, dur in zip(frequencies, durations):
        num_samples = int(sample_rate * dur)
        for i in range(num_samples):
            # Smooth attack and decay envelope
            envelope = 1.0
            attack = int(sample_rate * 0.01)
            decay = int(sample_rate * 0.02)
            if i < attack:
                envelope = i / attack
            elif i > num_samples - decay:
                envelope = (num_samples - i) / decay
                
            if freq > 0:
                val = math.sin(2.0 * math.pi * freq * (i / sample_rate)) * volume * envelope
            else:
                val = 0.0
            sample_val = int(val * 32767.0)
            total_frames.append(struct.pack('<h', max(-32767, min(32767, sample_val))))
            
    with wave.open(temp_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(total_frames))
        
    return temp_wav


def play_sound_async(sound_type: str = "chime"):
    """Plays synthetic JARVIS sound effect in background thread."""
    def _run():
        try:
            if not HAS_WINSOUND:
                return
            st = sound_type.lower()
            if st in ("chime", "success", "ok", "done"):
                # Elegant Iron Man interface chime (High C -> E -> G ascending)
                wav_path = _generate_tone_wav([523.25, 659.25, 783.99, 1046.50], [0.06, 0.06, 0.08, 0.15], volume=0.45)
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                try: os.remove(wav_path)
                except Exception: pass
            elif st in ("alert", "warning", "sentry", "alarm"):
                # Threat alert klaxon
                wav_path = _generate_tone_wav([880, 440, 880, 440], [0.12, 0.12, 0.12, 0.18], volume=0.7)
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                try: os.remove(wav_path)
                except Exception: pass
            elif st in ("whoosh", "process", "scan"):
                # Fast futuristic sweep
                freqs = [300 + i * 40 for i in range(15)]
                durs = [0.012] * 15
                wav_path = _generate_tone_wav(freqs, durs, volume=0.35)
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                try: os.remove(wav_path)
                except Exception: pass
            elif st in ("lock", "secure", "shield"):
                # Power-down / lock tone
                wav_path = _generate_tone_wav([1046.50, 783.99, 523.25, 261.63], [0.07, 0.07, 0.08, 0.2], volume=0.5)
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                try: os.remove(wav_path)
                except Exception: pass
            else:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


async def trigger_jarvis_sfx(sound_effect: str = "chime") -> str:
    """
    Plays high-tech JARVIS UI sound effect.
    
    Args:
        sound_effect: 'chime', 'success', 'alert', 'whoosh', 'lock', 'scan'
    """
    play_sound_async(sound_effect)
    return f"[OK] JARVIS Audio Effect '{sound_effect}' triggered."
