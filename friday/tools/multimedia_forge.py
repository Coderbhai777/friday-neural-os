"""
Multimedia Forge & Video/Audio Synthesis Studio for ULTRON.
Provides automated video transcode & compression (FFmpeg), audio track extraction,
spectral noise filtering, subtitle generator, EXIF metadata scrubber, and QR generator.
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


async def video_transcode_and_compress(input_path: str, output_path: str = "", target_size_mb: float = 25.0) -> str:
    """
    Compress video to an exact target file size (e.g. 25MB for Discord/Email or 16MB for WhatsApp) using FFmpeg.
    """
    ffmpeg = shutil.which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"
    ffprobe = shutil.which("ffprobe") or r"C:\ffmpeg\bin\ffprobe.exe"

    if not os.path.exists(ffmpeg):
        return "[FFMPEG ERROR] FFmpeg binary not found. Please ensure FFmpeg is installed or in PATH."

    input_file = Path(input_path).resolve()
    if not input_file.exists():
        return f"[FILE ERROR] Input video file '{input_path}' does not exist."

    if not output_path:
        output_file = input_file.parent / f"{input_file.stem}_compressed.mp4"
    else:
        output_file = Path(output_path).resolve()

    def _compress():
        # Get video duration in seconds via ffprobe
        duration_cmd = [
            ffprobe, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(input_file)
        ]
        res = subprocess.run(duration_cmd, capture_output=True, text=True)
        try:
            duration = float(res.stdout.strip())
        except Exception:
            duration = 60.0  # fallback

        # Calculate optimal bitrate: Target size (bits) / duration
        total_bitrate_kbps = (target_size_mb * 8192) / duration
        audio_bitrate_kbps = 128
        video_bitrate_kbps = max(100, int(total_bitrate_kbps - audio_bitrate_kbps))

        cmd = [
            ffmpeg, "-y", "-i", str(input_file),
            "-c:v", "libx264", "-b:v", f"{video_bitrate_kbps}k",
            "-preset", "medium", "-c:a", "aac", "-b:a", f"{audio_bitrate_kbps}k",
            "-movflags", "+faststart", str(output_file)
        ]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if p.returncode == 0 and output_file.exists():
            final_size_mb = output_file.stat().st_size / (1024 * 1024)
            return f"🎬 Video Successfully Compressed!\n  • Output: {output_file}\n  • Final File Size: {final_size_mb:.2f} MB (Target: {target_size_mb} MB)\n  • Video Bitrate: {video_bitrate_kbps} kbps"
        return f"[COMPRESSION ERROR] FFmpeg returned code {p.returncode}: {p.stderr[:300]}"

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _compress)
    except Exception as exc:
        return f"[TRANSCODE ERROR] {exc}"


async def video_extract_audio(video_path: str, output_format: str = "mp3") -> str:
    """
    Extract audio track from video file into MP3, WAV, or AAC format.
    """
    ffmpeg = shutil.which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"
    if not os.path.exists(ffmpeg):
        return "[FFMPEG ERROR] FFmpeg binary not found in PATH."

    input_file = Path(video_path).resolve()
    if not input_file.exists():
        return f"[FILE ERROR] Video file not found: {video_path}"

    out_file = input_file.parent / f"{input_file.stem}.{output_format}"

    def _extract():
        cmd = [ffmpeg, "-y", "-i", str(input_file), "-vn", "-q:a", "0", str(out_file)]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0 and out_file.exists():
            size_mb = out_file.stat().st_size / (1024 * 1024)
            return f"🎵 Audio Extracted Successfully!\n  • Audio File: {out_file}\n  • Size: {size_mb:.2f} MB\n  • Format: {output_format.upper()}"
        return f"[EXTRACTION ERROR] {res.stderr[:300]}"

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _extract)
    except Exception as exc:
        return f"[AUDIO EXTRACT ERROR] {exc}"


async def audio_noise_reducer(audio_path: str, output_path: str = "") -> str:
    """
    Apply advanced spectral gating and noise reduction filters to clean microphone hiss, hum, and room noise.
    """
    ffmpeg = shutil.which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"
    if not os.path.exists(ffmpeg):
        return "[FFMPEG ERROR] FFmpeg binary not found in PATH."

    input_file = Path(audio_path).resolve()
    if not input_file.exists():
        return f"[FILE ERROR] Audio file not found: {audio_path}"

    out_file = Path(output_path).resolve() if output_path else input_file.parent / f"{input_file.stem}_denoised{input_file.suffix}"

    def _denoise():
        # Highpass 80Hz (remove AC hum/sub-rumble), afftdn (spectral noise reduction), lowpass 14kHz
        af_filter = "highpass=f=80,afftdn=nf=-25:tn=1,lowpass=f=14000,dynaudnorm=f=150:g=15"
        cmd = [ffmpeg, "-y", "-i", str(input_file), "-af", af_filter, str(out_file)]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0 and out_file.exists():
            return f"🎙️ Spectral Noise Reduction Complete!\n  • Clean Audio File: {out_file}\n  • Filters Applied: Highpass 80Hz + Fast Fourier Denoise + Dynamic Normalization"
        return f"[DENOISE ERROR] {res.stderr[:300]}"

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _denoise)
    except Exception as exc:
        return f"[NOISE REDUCER ERROR] {exc}"


async def video_generate_subtitles(video_path: str, output_srt: str = "") -> str:
    """
    Transcribe audio from video and generate timed .srt subtitle file using Gemini Multimodal Speech Intelligence.
    """
    video_file = Path(video_path).resolve()
    if not video_file.exists():
        return f"[FILE ERROR] Video file '{video_path}' not found."

    srt_path = Path(output_srt).resolve() if output_srt else video_file.parent / f"{video_file.stem}.srt"

    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "[API ERROR] GEMINI_API_KEY is required for speech-to-subtitles transcription."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Upload audio to Gemini file API
        audio_res = await video_extract_audio(str(video_file), "mp3")
        mp3_path = video_file.parent / f"{video_file.stem}.mp3"
        if not mp3_path.exists():
            return f"[SUBTITLE ERROR] Failed to extract audio track: {audio_res}"

        def _sync_transcribe():
            uploaded = genai.upload_file(str(mp3_path))
            prompt = "Listen to this audio track and generate a standard .SRT subtitle file with precise timestamps (00:00:00,000 --> 00:00:00,000). Return ONLY the valid .srt content."
            resp = model.generate_content([uploaded, prompt])
            srt_content = resp.text
            srt_content = re.sub(r"^```[a-zA-Z]*\n", "", srt_content)
            srt_content = re.sub(r"```$", "", srt_content).strip()
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            return srt_path

        loop = asyncio.get_event_loop()
        final_srt = await loop.run_in_executor(None, _sync_transcribe)
        return f"📝 Subtitles Generated Successfully!\n  • SRT File: {final_srt}\n  • Ready to be embedded into player or video."
    except Exception as exc:
        return f"[SUBTITLE GENERATION ERROR] {exc}"


async def image_metadata_exif(image_path: str, action: str = "read") -> str:
    """
    Read or strip privacy-sensitive EXIF metadata (GPS coordinates, camera serial, capture timestamp) from images.
    """
    img_file = Path(image_path).resolve()
    if not img_file.exists():
        return f"[FILE ERROR] Image '{image_path}' not found."

    try:
        from PIL import Image, ExifTags

        if action == "read":
            img = Image.open(img_file)
            exif_data = img._getexif()
            if not exif_data:
                return f"📷 EXIF Metadata: No EXIF tags found in '{img_file.name}' (Clean)."

            tags = {}
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                tags[str(tag_name)] = str(value)

            report = [f"📷 EXIF Metadata for {img_file.name} ({len(tags)} tags):"]
            for k in ["Make", "Model", "DateTime", "Software", "GPSInfo", "LensModel", "ExposureTime"]:
                if k in tags:
                    report.append(f"  • {k}: {tags[k]}")
            return "\n".join(report)
        elif action in ("strip", "clean", "remove"):
            img = Image.open(img_file)
            data = list(img.getdata())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)
            clean_path = img_file.parent / f"{img_file.stem}_scrubbed{img_file.suffix}"
            clean_img.save(clean_path)
            return f"🛡️ Privacy EXIF Scrubber: Stripped all camera & GPS metadata!\n  • Clean Image Saved: {clean_path}"
        else:
            return f"[EXIF ERROR] Unsupported action '{action}'. Options: read, strip."
    except Exception as exc:
        return f"[EXIF ERROR] {exc}"


async def qr_code_custom_generator(data: str, output_path: str = "qr.png", color: str = "#00FFCC", bg_color: str = "#000000") -> str:
    """
    Generate high-resolution custom-styled QR codes with hex color styling.
    """
    try:
        import qrcode
        from PIL import Image

        out_file = Path(output_path).resolve()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=color, back_color=bg_color)
        img.save(str(out_file))
        return f"📱 QR Code Generated Successfully!\n  • Payload: '{data}'\n  • File Saved: {out_file}\n  • Theme: Fill {color} / Bg {bg_color}"
    except ImportError:
        return "[QR ERROR] 'qrcode' or 'Pillow' library missing."
    except Exception as exc:
        return f"[QR CODE ERROR] {exc}"
