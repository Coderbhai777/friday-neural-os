"""
ULTRON Autonomous Headless Universal Image & Media Downloader Engine
Downloads any high-resolution image, wallpaper, logo, artwork, or photo across the entire internet headlessly with zero browser GUI.
"""

import os
import re
import io
import asyncio
import urllib.parse
import requests
from pathlib import Path
from PIL import Image
from typing import Optional, List, Tuple

Image.MAX_IMAGE_PIXELS = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}


def _search_universal_images(query: str, max_candidates: int = 25) -> List[str]:
    """
    Universal multi-engine headless scraper aggregating Yandex Visual Index, Bing Images,
    Google Images, and Wikimedia Commons. Covers all subjects, entities, wallpapers, and products globally.
    """
    candidates: List[Tuple[str, int]] = []
    q_enc = urllib.parse.quote(query)
    q_terms = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]

    # --- 1. Wikimedia Commons (Supreme accuracy for flags, logos, landmarks, universities, official symbols) ---
    search_variants = [query, f"Flag of {query.replace('flag', '').strip()}" if "flag" in query.lower() else query]
    if len(query.split()) > 1:
        search_variants.append(query.split()[0])

    for s_term in search_variants:
        try:
            w_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(s_term)}&gsrnamespace=6&prop=imageinfo&iiprop=url|size&iiurlwidth=2560&format=json"
            wr = requests.get(w_url, headers=HEADERS, timeout=6)
            if wr.status_code == 200:
                pages = wr.json().get("query", {}).get("pages", {})
                for pid, pdata in pages.items():
                    title = pdata.get("title", "").lower()
                    ii = pdata.get("imageinfo", [])
                    if ii:
                        u = ii[0].get("thumburl") or ii[0].get("url")
                        if u:
                            # Exact match scoring
                            matches = sum(1 for t in q_terms if t in title)
                            if len(q_terms) > 0 and matches == len(q_terms):
                                # Top-tier exact match (e.g. 'Flag of India')
                                score = 250
                            elif any(k in title for k in ["flag", "logo", "campus", "building", "emblem", "insignia"]):
                                score = 150 + (matches * 20)
                            elif matches > 0:
                                score = 100 + (matches * 15)
                            else:
                                score = 50
                            candidates.append((u, score))
        except Exception:
            pass

    # --- 2. Bing Images Direct Endpoint ---
    try:
        b_url = f"https://www.bing.com/images/search?q={q_enc}&form=HDRSC2&first=1"
        br = requests.get(b_url, headers=HEADERS, timeout=8)
        if br.status_code == 200:
            b_matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', br.text)
            if not b_matches:
                b_matches = re.findall(r'"murl":"(https?://[^"]+)"', br.text)
            for idx, m in enumerate(b_matches[:25]):
                score = 80 - idx
                if any(t in m.lower() for t in q_terms):
                    score += 25
                candidates.append((m, score))
    except Exception:
        pass

    # --- 3. Google Images Direct Scraper ---
    try:
        g_url = f"https://www.google.com/search?q={q_enc}&tbm=isch&gl=us&hl=en"
        gr = requests.get(g_url, headers=HEADERS, timeout=8)
        if gr.status_code == 200:
            g_full = re.findall(r'\["(https://[^"]+?\.(?:jpg|jpeg|png|webp))",\s*\d+,\s*\d+\]', gr.text)
            for idx, u in enumerate(g_full[:15]):
                if "gstatic.com" not in u:
                    score = 85 - idx
                    if any(t in u.lower() for t in q_terms):
                        score += 20
                    candidates.append((u, score))
            g_thumbs = re.findall(r'src="(https://encrypted-tbn0\.gstatic\.com/images\?q=[^"]+)"', gr.text)
            for u in g_thumbs[:5]:
                candidates.append((u, 40))
    except Exception:
        pass

    # --- 4. Yandex Visual Search (Depth for wallpapers, cars, products, art) ---
    try:
        y_url = f"https://yandex.com/images/search?text={q_enc}"
        yr = requests.get(y_url, headers=HEADERS, timeout=8)
        if yr.status_code == 200:
            y_matches = re.findall(r'img_url=([^&"\']+)', yr.text)
            for idx, m in enumerate(y_matches[:25]):
                url = urllib.parse.unquote(m)
                if url.startswith("http") and "yandex.net" not in url and "avatars.mds" not in url:
                    score = 75 - idx
                    if any(t in url.lower() for t in q_terms):
                        score += 20
                    candidates.append((url, score))
    except Exception:
        pass

    # Sort all candidates by relevance score descending
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Deduplicate preserving order
    seen = set()
    deduped = []
    for u, score in candidates:
        clean = u.split("?utm_")[0].strip()
        if clean not in seen and (clean.startswith("http://") or clean.startswith("https://")):
            seen.add(clean)
            deduped.append(clean)

    return deduped[:max_candidates]


def _download_and_validate(url: str, dest_path_without_ext: Path, min_dimension: int = 180) -> Optional[Path]:
    """Downloads an image from URL and validates it with Pillow to ensure quality and format integrity."""
    try:
        req_headers = {
            "User-Agent": HEADERS["User-Agent"],
            "Referer": url,
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }
        resp = requests.get(url, headers=req_headers, timeout=12, stream=True)
        if resp.status_code == 200:
            img_data = resp.content
            if len(img_data) > 1024:
                img = Image.open(io.BytesIO(img_data))
                width, height = img.size
                if width >= min_dimension and height >= min_dimension:
                    fmt = (img.format or "JPEG").lower()
                    ext = f".{fmt}" if fmt in ["jpg", "jpeg", "png", "webp", "gif"] else ".jpg"
                    final_path = dest_path_without_ext.with_suffix(ext)
                    with open(final_path, "wb") as f:
                        f.write(img_data)
                    return final_path
    except Exception:
        pass
    return None


async def download_image(query_or_url: str, output_path: str = "", filename: str = "") -> str:
    """
    Headlessly searches and downloads ANY image from the web (or direct URL) to Downloads/Desktop with 0 browser GUI.
    Works universally for wallpapers, cars, celebrities, anime, nature, products, logos, architecture, art, and more.
    """
    def _execute():
        out_dir = Path.home() / "Downloads"
        if output_path and os.path.isdir(output_path):
            out_dir = Path(output_path)
        out_dir.mkdir(parents=True, exist_ok=True)

        is_direct = query_or_url.startswith("http://") or query_or_url.startswith("https://")
        candidates = [query_or_url] if is_direct else _search_universal_images(query_or_url, max_candidates=25)

        if not candidates:
            return f"[ERROR] No image results found for query: '{query_or_url}'."

        safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", filename or (Path(query_or_url).stem if is_direct else query_or_url))
        safe_name = safe_name.strip("_")[:50] or "web_image"
        base_dest = out_dir / safe_name

        for target_url in candidates:
            saved_file = _download_and_validate(target_url, base_dest)
            if saved_file and saved_file.exists():
                size_kb = saved_file.stat().st_size // 1024
                try:
                    with Image.open(saved_file) as img:
                        res_str = f"{img.size[0]}x{img.size[1]}"
                except Exception:
                    res_str = "High-Res"
                return f"[SUCCESS] Downloaded image ({res_str}, {size_kb} KB) headlessly to:\n{saved_file}"

        return f"[ERROR] Could not download a valid image for '{query_or_url}' from available candidate sources."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def search_and_download_images(query: str, count: int = 3, output_dir: str = "") -> str:
    """
    Headlessly downloads multiple images for any topic/query into a designated folder.
    """
    def _execute():
        target_dir = Path(output_dir) if output_dir else Path.home() / "Downloads" / re.sub(r"[^a-zA-Z0-9_]", "_", query)
        target_dir.mkdir(parents=True, exist_ok=True)

        candidates = _search_universal_images(query, max_candidates=count * 5)
        downloaded = []
        safe_q = re.sub(r"[^a-zA-Z0-9_]", "_", query)[:30]

        for i, url in enumerate(candidates):
            if len(downloaded) >= count:
                break
            base_dest = target_dir / f"{safe_q}_{len(downloaded)+1}"
            saved = _download_and_validate(url, base_dest)
            if saved:
                downloaded.append(str(saved))

        if downloaded:
            return f"[SUCCESS] Downloaded {len(downloaded)} images to {target_dir}:\n" + "\n".join(downloaded)
        return f"[ERROR] Failed to download images for query '{query}'."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def download_file(url: str, output_path: str = "") -> str:
    """
    Headlessly downloads any file from a direct URL with proper desktop browser headers.
    """
    def _execute():
        out_dir = Path.home() / "Downloads"
        if output_path and os.path.isdir(output_path):
            out_dir = Path(output_path)
            dest_file = out_dir / Path(url.split("?")[0]).name
        elif output_path:
            dest_file = Path(output_path)
        else:
            fname = Path(url.split("?")[0]).name or "downloaded_file"
            dest_file = out_dir / fname

        dest_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            req_headers = {"User-Agent": HEADERS["User-Agent"], "Referer": url}
            resp = requests.get(url, headers=req_headers, timeout=30, stream=True)
            if resp.status_code == 200:
                with open(dest_file, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                size_mb = dest_file.stat().st_size / (1024 * 1024)
                return f"[SUCCESS] File downloaded ({size_mb:.2f} MB):\n{dest_file}"
            return f"[ERROR] HTTP {resp.status_code} while downloading {url}"
        except Exception as e:
            return f"[ERROR] Download failed: {e}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


WALLPAPER_DIR = Path.home() / "Pictures" / "ULTRONWallpapers"
WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)

CURATED_WALLPAPERS = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=2560&q=85",
    "https://images.unsplash.com/photo-1534972195531-a756b1126f24?w=2560&q=85",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=2560&q=85",
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=2560&q=85",
    "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=2560&q=85",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=2560&q=85"
]

def _apply_windows_wallpaper(img_path: str) -> bool:
    """Sets the desktop wallpaper on Windows and notifies the shell."""
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    try:
        abs_p = str(Path(img_path).resolve())
        ext = Path(abs_p).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".bmp", ".png"]:
            with Image.open(abs_p) as im:
                converted_p = str(Path(abs_p).with_suffix(".png"))
                im.save(converted_p, "PNG")
                abs_p = converted_p
        
        import ctypes
        res = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            abs_p,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        return bool(res)
    except Exception:
        return False


async def change_wallpaper(query_or_path: str = "", image_path: str = "") -> str:
    """
    Instantly changes the desktop wallpaper on Windows.
    Accepts:
    1. A topic / theme (e.g. 'Iron Man 4k', 'cyberpunk city', 'minimalist space', 'mountains sunset')
    2. A direct image URL (https://...)
    3. A local image file path (C:/Users/.../photo.jpg)
    4. Blank / empty (downloads a stunning curated 4K aesthetic wallpaper)
    """
    def _execute():
        import time
        target = query_or_path.strip() or image_path.strip()
        
        # 1. Local file path provided
        if target and os.path.exists(target) and os.path.isfile(target):
            if _apply_windows_wallpaper(target):
                return f"[SUCCESS] Changed desktop wallpaper to local image:\n{target}"
            return f"[ERROR] Failed to set wallpaper from local path: {target}"

        # 2. Direct Image URL
        if target.startswith("http://") or target.startswith("https://"):
            try:
                safe_name = f"wallpaper_{int(time.time())}"
                dest = WALLPAPER_DIR / safe_name
                saved = _download_and_validate(target, dest, min_dimension=300)
                if saved and saved.exists():
                    if _apply_windows_wallpaper(str(saved)):
                        return f"[SUCCESS] Downloaded and applied wallpaper to desktop:\n{saved}"
            except Exception as e:
                return f"[ERROR] Could not download and set wallpaper: {e}"

        # 3. Topic Query or Curated
        search_q = target if target else "4k futuristic aesthetic dark wallpaper"
        try:
            import random
            candidates = _search_universal_images(f"{search_q} 4k wallpaper", max_candidates=15)
            if not candidates:
                candidates = random.sample(CURATED_WALLPAPERS, len(CURATED_WALLPAPERS))

            safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", search_q)[:30].strip("_")
            dest_base = WALLPAPER_DIR / f"{safe_name}_{int(time.time())}"

            for url in candidates:
                saved = _download_and_validate(url, dest_base, min_dimension=500)
                if saved and saved.exists():
                    if _apply_windows_wallpaper(str(saved)):
                        return f"[SUCCESS] Downloaded and applied '{search_q}' wallpaper to your desktop:\n{saved}"
        except Exception as e:
            return f"[ERROR] Failed searching wallpaper: {e}"

        return "[ERROR] Unable to find and apply a valid wallpaper."

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)


async def set_desktop_wallpaper(query_or_path: str = "") -> str:
    """Alias for change_wallpaper."""
    return await change_wallpaper(query_or_path)

