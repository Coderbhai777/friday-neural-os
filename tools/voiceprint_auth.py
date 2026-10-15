"""
ULTRON Neural Voiceprint Biometric Authentication Engine
Provides acoustic speaker verification, pitch & MFCC fingerprint extraction,
and biometric anti-impersonation security gates using standard audio telemetry.
"""

import os
import io
import time
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

import numpy as np
import scipy.signal
import scipy.fftpack

VOICEPRINT_DIR = Path.home() / "Documents" / "ULTRON_Data" / "voiceprints"
VOICEPRINT_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = VOICEPRINT_DIR / "voice_security_config.json"

if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(json.dumps({"biometric_gate_enabled": False, "master_profile": "shivansh", "threshold": 0.76}, indent=2), encoding="utf-8")

_IS_RECORDING = False
_LAST_RECORD_TIME = 0.0


def _record_audio_clip(duration: float = 3.0, sample_rate: int = 16000) -> Optional[np.ndarray]:
    """Records raw microphone audio safely using sounddevice."""
    global _IS_RECORDING, _LAST_RECORD_TIME
    
    # Enforce minimum cooldown of 3 seconds to avoid device collision and infinite loops
    now = time.time()
    if _IS_RECORDING or (now - _LAST_RECORD_TIME < 3.0):
        print("[VOICEPRINT] Audio capture skipped (cooldown active).")
        return None

    _IS_RECORDING = True
    _LAST_RECORD_TIME = now
    
    # Cap duration to max 3 seconds to avoid blocking the voice loop
    dur = max(1.0, min(3.0, float(duration)))
    try:
        import sounddevice as sd
        try:
            from tools.mic_resolver import get_best_sounddevice_input
            dev = get_best_sounddevice_input()
        except Exception:
            dev = None
        audio = sd.rec(int(dur * sample_rate), samplerate=sample_rate, channels=1, dtype='float32', device=dev)
        sd.wait()
        if audio is None:
            return None
        flat = audio.flatten()
        if np.isnan(flat).any() or np.isinf(flat).any() or len(flat) == 0:
            return None
        return flat
    except Exception as e:
        print(f"[VOICEPRINT] Audio capture error: {e}")
        return None
    finally:
        _IS_RECORDING = False


def _extract_acoustic_fingerprint(audio: np.ndarray, sample_rate: int = 16000) -> Optional[Dict[str, Any]]:
    """
    Computes mathematical acoustic biometric features:
    1. Fundamental Frequency / Pitch (F0 estimation via autocorrelation)
    2. Spectral Centroid & Spectral Spread
    3. Spectral Rolloff (85% energy point)
    4. Zero-Crossing Rate (ZCR)
    5. 13-band Mel-Frequency Filterbank Cepstral Coefficients (MFCC)
    """
    if audio is None or len(audio) == 0:
        return None

    # Check for silence or near-zero signal
    max_amp = float(np.max(np.abs(audio)))
    if max_amp < 1e-4 or np.isnan(max_amp):
        return None

    # 1. Normalize audio & remove DC offset safely
    audio = audio - np.mean(audio)
    max_amp = float(np.max(np.abs(audio)))
    if max_amp > 1e-6:
        audio = audio / max_amp
    else:
        return None

    # 2. Zero-crossing rate
    zcr = float(np.mean(np.abs(np.diff(np.signbit(audio)))))

    # 3. Autocorrelation Pitch Estimation (F0)
    corr = np.correlate(audio, audio, mode='full')
    corr = corr[len(corr)//2:]
    
    # Restrict search between 70Hz and 350Hz (human vocal range)
    min_lag = int(sample_rate / 350)
    max_lag = int(sample_rate / 70)
    
    if len(corr) > max_lag:
        peak_lag = np.argmax(corr[min_lag:max_lag]) + min_lag
        pitch_f0 = float(sample_rate / peak_lag) if peak_lag > 0 else 120.0
    else:
        pitch_f0 = 120.0

    # 4. FFT Spectral Features
    fft_vals = np.abs(np.fft.rfft(audio * np.hanning(len(audio))))
    freqs = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)
    
    # Spectral Centroid
    total_fft = float(np.sum(fft_vals))
    if total_fft > 1e-9:
        norm_fft = fft_vals / total_fft
        spectral_centroid = float(np.sum(freqs * norm_fft))
    else:
        spectral_centroid = 1500.0
    
    # Spectral Rolloff
    cum_energy = np.cumsum(fft_vals)
    if len(cum_energy) > 0 and cum_energy[-1] > 1e-9:
        rolloff_idx = np.searchsorted(cum_energy, 0.85 * cum_energy[-1])
        spectral_rolloff = float(freqs[min(rolloff_idx, len(freqs)-1)])
    else:
        spectral_rolloff = 3000.0

    # 5. Pseudo-MFCC Filterbank Energy (13 Mel-spaced bands)
    mel_min = 1125 * np.log(1 + 50 / 700)
    mel_max = 1125 * np.log(1 + 8000 / 700)
    mel_points = np.linspace(mel_min, mel_max, 15)
    hz_points = 700 * (np.exp(mel_points / 1125) - 1)
    bin_points = np.floor((len(audio) + 1) * hz_points / sample_rate).astype(int)

    mfcc_energies = []
    for m in range(1, 14):
        f_m_minus = max(0, bin_points[m - 1])
        f_m = max(f_m_minus + 1, bin_points[m])
        f_m_plus = max(f_m + 1, bin_points[m + 1])
        
        band_energy = float(np.sum(fft_vals[min(f_m_minus, len(fft_vals)-1):min(f_m_plus, len(fft_vals))]))
        mfcc_energies.append(np.log(band_energy + 1e-6))

    # Discrete Cosine Transform (DCT) to decorrelate
    mfcc_coeffs = scipy.fftpack.dct(mfcc_energies, type=2, norm='ortho').tolist()

    return {
        "pitch_f0_hz": round(pitch_f0, 2),
        "spectral_centroid_hz": round(spectral_centroid, 2),
        "spectral_rolloff_hz": round(spectral_rolloff, 2),
        "zero_crossing_rate": round(zcr, 4),
        "mfcc_vector": [round(float(x), 4) for x in mfcc_coeffs]
    }


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two feature vectors."""
    a = np.array(v1)
    b = np.array(v2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


async def enroll_voiceprint(profile_name: str = "shivansh", duration_seconds: int = 3) -> str:
    """
    Enrolls a master biometric voiceprint profile by recording a spoken passphrase sample.
    
    Args:
        profile_name: Name of the voice profile (default: 'shivansh').
        duration_seconds: Recording length in seconds (default: 3s).
    """
    def _execute():
        print(f"[VOICEPRINT] Recording {duration_seconds}s voice biometric sample for '{profile_name}'...")
        audio = _record_audio_clip(duration=float(duration_seconds))
        if audio is None or len(audio) == 0:
            return "[VOICEPRINT] Microphone capture skipped or unavailable. Voice enrollment idle."

        features = _extract_acoustic_fingerprint(audio)
        if features is None:
            return "[VOICEPRINT] Audio level was too low or silent. Please speak into the mic."

        profile_path = VOICEPRINT_DIR / f"{profile_name.lower().strip()}.json"
        
        profile_data = {
            "profile_name": profile_name,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "features": features
        }
        profile_path.write_text(json.dumps(profile_data, indent=2), encoding="utf-8")

        return (
            f"[VOICEPRINT ENROLLED SUCCESSFULLY]\n"
            f"- Profile: {profile_name}\n"
            f"- Fundamental Pitch (F0): {features['pitch_f0_hz']} Hz\n"
            f"- Spectral Centroid: {features['spectral_centroid_hz']} Hz\n"
            f"- Spectral Rolloff: {features['spectral_rolloff_hz']} Hz\n"
            f"- 13-D MFCC Vector: Enrolled and secured at {profile_path.name}"
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def verify_speaker_voice(duration_seconds: int = 3, threshold: float = 0.75) -> str:
    """
    Listens to live microphone audio and verifies if the speaker matches Shivansh's master voiceprint.
    """
    def _execute():
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
        master_profile = config.get("master_profile", "shivansh")
        profile_path = VOICEPRINT_DIR / f"{master_profile.lower()}.json"
        
        if not profile_path.exists():
            return f"[WARN] No enrolled voiceprint found for '{master_profile}'. Run 'enroll_voiceprint()' first."

        master_data = json.loads(profile_path.read_text(encoding="utf-8"))
        master_mfcc = master_data["features"]["mfcc_vector"]
        master_pitch = master_data["features"]["pitch_f0_hz"]

        audio = _record_audio_clip(duration=float(duration_seconds))
        if audio is None or len(audio) == 0:
            return "[VOICEPRINT] Microphone capture unavailable."

        current_features = _extract_acoustic_fingerprint(audio)
        if current_features is None:
            return "[VOICEPRINT] Voice audio too quiet for verification."

        current_mfcc = current_features["mfcc_vector"]
        current_pitch = current_features["pitch_f0_hz"]

        # Calculate acoustic similarity
        mfcc_sim = _cosine_similarity(master_mfcc, current_mfcc)
        pitch_diff_pct = abs(current_pitch - master_pitch) / (master_pitch + 1e-6)
        pitch_score = max(0.0, 1.0 - (pitch_diff_pct * 0.8))
        
        composite_score = round((mfcc_sim * 0.7) + (pitch_score * 0.3), 3)
        confidence_pct = round(max(0.0, min(100.0, composite_score * 100)), 1)
        
        target_thresh = threshold or config.get("threshold", 0.75)
        is_match = composite_score >= target_thresh

        if is_match:
            return (
                f"[BIOMETRIC VOICE VERIFIED]\n"
                f"- Speaker: AUTHORIZED (Master: {master_profile.upper()})\n"
                f"- Acoustic Match Confidence: {confidence_pct}%\n"
                f"- Pitch Delta: {abs(current_pitch - master_pitch):.1f} Hz\n"
                f"- Security Status: ACCESS GRANTED"
            )
        else:
            return (
                f"[BIOMETRIC VOICE MISMATCH]\n"
                f"- Speaker: UNRECOGNIZED\n"
                f"- Match Score: {confidence_pct}% (Required: {target_thresh*100}%)\n"
                f"- Security Status: ACCESS DENIED"
            )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def toggle_voice_biometric_gate(enabled: bool = True) -> str:
    """
    Enables or disables the continuous voiceprint biometric security gate for ULTRON.
    """
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
        config["biometric_gate_enabled"] = bool(enabled)
        CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
        
        status_str = "ACTIVE (Commands gated by voice authentication)" if enabled else "DISABLED (Open access)"
        return f"[VOICEPRINT SECURITY GATE]: {status_str}"
    except Exception as e:
        return f"[ERROR] Failed to update security gate: {e}"


async def get_voiceprint_status() -> str:
    """
    Returns the status of enrolled voice profiles and biometric authentication parameters.
    """
    try:
        profiles = list(VOICEPRINT_DIR.glob("*.json"))
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
        
        names = [p.stem for p in profiles if p.name != "voice_security_config.json"]
        return (
            f"[BIOMETRIC VOICEPRINT STATUS]\n"
            f"- Biometric Gate: {'ENABLED' if config.get('biometric_gate_enabled') else 'DISABLED'}\n"
            f"- Master Profile: {config.get('master_profile', 'None')}\n"
            f"- Enrolled Profiles ({len(names)}): {', '.join(names) if names else 'None'}\n"
            f"- Verification Threshold: {config.get('threshold', 0.76) * 100}%"
        )
    except Exception as e:
        return f"[ERROR] Could not fetch voiceprint status: {e}"
