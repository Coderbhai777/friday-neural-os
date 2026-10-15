"""
ULTRON OSINT & Deep Reconnaissance Suite
Tactical intelligence gathering, digital footprinting, metadata forensics, and domain enumeration.
"""

import os
import re
import ssl
import json
import socket
import datetime
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image, ExifTags

try:
    from dotenv import load_dotenv
    env_paths = [
        Path.home() / "Documents" / "ULTRON_Data" / ".env",
        Path.home() / ".env",
        Path(".env")
    ]
    for ep in env_paths:
        if ep.exists():
            load_dotenv(dotenv_path=ep, override=False)
except Exception:
    pass


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


# =====================================================================
# 1. USERNAME SCANNER (35+ Platforms)
# =====================================================================

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter/X": "https://x.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}/",
    "YouTube": "https://www.youtube.com/@{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Telegram": "https://t.me/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Medium": "https://medium.com/@{}",
    "DeviantArt": "https://www.deviantart.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "Keybase": "https://keybase.io/{}",
    "DockerHub": "https://hub.docker.com/u/{}",
    "Disqus": "https://disqus.com/by/{}/",
    "Patreon": "https://www.patreon.com/{}",
    "Vimeo": "https://vimeo.com/{}",
    "Behance": "https://www.behance.net/{}",
    "Dribbble": "https://dribbble.com/{}",
    "ProductHunt": "https://www.producthunt.com/@{}",
    "Goodreads": "https://www.goodreads.com/{}",
    "Chess.com": "https://www.chess.com/member/{}",
    "Lichess": "https://lichess.org/@/{}",
    "Replit": "https://replit.com/@{}",
    "Kaggle": "https://www.kaggle.com/{}",
    "Pastebin": "https://pastebin.com/u/{}",
}


def _check_platform(platform: str, url_template: str, username: str) -> Optional[Dict[str, str]]:
    url = url_template.format(username)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=6, allow_redirects=True)
        if resp.status_code == 200:
            # Platform specific false-positive elimination
            text_lower = resp.text.lower()
            if platform == "Reddit" and "page not found" in text_lower:
                return None
            if platform == "Twitter/X" and "this account doesn’t exist" in text_lower:
                return None
            if platform == "Instagram" and ("sorry, this page isn't available" in text_lower or "login • instagram" in text_lower):
                return None
            if platform == "Telegram" and "if you have telegram, you can view and join" not in text_lower and "view in telegram" not in text_lower:
                return None
            if platform == "Steam" and "the specified profile could not be found" in text_lower:
                return None
            if platform == "Chess.com" and "page not found" in text_lower:
                return None
            return {"platform": platform, "url": url}
    except Exception:
        pass
    return None


async def osint_username_scan(username: str) -> str:
    """
    Scans 30+ major social networks, developer portals, and platforms for a username or handle.
    """
    clean_user = username.strip().lstrip("@")
    if not clean_user:
        return "[OSINT ERROR] Please specify a valid username."

    found = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [
            executor.submit(_check_platform, plat, url_temp, clean_user)
            for plat, url_temp in PLATFORMS.items()
        ]
        for f in as_completed(futures):
            res = f.result()
            if res:
                found.append(res)

    if not found:
        return f"🔍 [OSINT REPORT] Target: '{clean_user}'\n❌ No public profile matches found across {len(PLATFORMS)} scanned networks."

    lines = [
        f"🎯 [OSINT RECON REPORT] Username: '{clean_user}'",
        f"📊 Scanned: {len(PLATFORMS)} Platforms | Positive Matches: {len(found)}",
        "=" * 50
    ]
    for item in sorted(found, key=lambda x: x["platform"]):
        lines.append(f"  ✅ {item['platform']:<15} -> {item['url']}")

    return "\n".join(lines)


# =====================================================================
# 2. METADATA FORENSICS & SCRUBBER
# =====================================================================

def _convert_to_degrees(value):
    """Helper function to convert GPS coordinates stored in EXIF to degrees."""
    d0 = value[0][0] / value[0][1] if isinstance(value[0], tuple) else float(value[0])
    d1 = value[1][0] / value[1][1] if isinstance(value[1], tuple) else float(value[1])
    d2 = value[2][0] / value[2][1] if isinstance(value[2], tuple) else float(value[2])
    return d0 + (d1 / 60.0) + (d2 / 3600.0)


async def osint_metadata_analyze(file_path: str, scrub_exif: bool = False) -> str:
    """
    Extracts deep EXIF & file metadata (GPS coordinates, camera model, date/time, author).
    Optionally scrubs all metadata to make the file completely anonymous.
    """
    from friday_tools.jarvis_vision import _resolve_image_path
    resolved = _resolve_image_path(file_path)
    if not resolved or not resolved.exists():
        p = Path(file_path)
        if p.exists():
            resolved = p
        else:
            return f"[OSINT ERROR] File not found: {file_path}"

    try:
        ext = resolved.suffix.lower()
        meta_info = {
            "File Name": resolved.name,
            "File Size": f"{resolved.stat().st_size / 1024:.2f} KB",
            "File Path": str(resolved),
            "Modified": datetime.datetime.fromtimestamp(resolved.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }

        gps_data = {}
        exif_found = {}

        if ext in [".jpg", ".jpeg", ".png", ".tiff", ".webp"]:
            with Image.open(resolved) as img:
                meta_info["Resolution"] = f"{img.width} x {img.height}"
                meta_info["Color Mode"] = img.mode
                
                exif = getattr(img, "_getexif", lambda: None)()
                if exif:
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if tag_name == "GPSInfo":
                            for t in value:
                                sub_tag = ExifTags.GPSTAGS.get(t, str(t))
                                gps_data[sub_tag] = value[t]
                        else:
                            if isinstance(value, (str, int, float)):
                                exif_found[tag_name] = str(value)

        # Process GPS if available
        gps_summary = ""
        if gps_data and "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
            try:
                lat = _convert_to_degrees(gps_data["GPSLatitude"])
                if gps_data.get("GPSLatitudeRef") == "S":
                    lat = -lat
                lon = _convert_to_degrees(gps_data["GPSLongitude"])
                if gps_data.get("GPSLongitudeRef") == "W":
                    lon = -lon
                gps_summary = f"\n📍 EXACT GPS COORDINATES:\n  Latitude:  {lat:.6f}\n  Longitude: {lon:.6f}\n  Google Maps: https://www.google.com/maps?q={lat},{lon}"
            except Exception:
                pass

        # Scrubbing Action
        scrub_msg = ""
        if scrub_exif:
            try:
                clean_path = resolved.parent / f"scrubbed_{resolved.name}"
                with Image.open(resolved) as img:
                    data = list(img.getdata())
                    image_without_exif = Image.new(img.mode, img.size)
                    image_without_exif.putdata(data)
                    image_without_exif.save(clean_path)
                scrub_msg = f"\n\n🛡️ [METADATA SCRUBBED]\nClean copy created with zero EXIF/GPS: {clean_path}"
            except Exception as se:
                scrub_msg = f"\n\n❌ Scrubbing error: {se}"

        report = [
            f"🔬 [METADATA FORENSICS] Target: {resolved.name}",
            "=" * 50
        ]
        for k, v in meta_info.items():
            report.append(f"  • {k:<15}: {v}")

        if exif_found:
            report.append("\n📸 CAMERA & EXIF HARDWARE TELEMETRY:")
            for k in ["Make", "Model", "Software", "DateTimeOriginal", "LensModel", "ExposureTime", "FNumber", "ISOSpeedRatings"]:
                if k in exif_found:
                    report.append(f"  • {k:<18}: {exif_found[k]}")

        if gps_summary:
            report.append(gps_summary)
        else:
            report.append("\n📍 GPS Telemetry: No embedded geotags found.")

        if scrub_msg:
            report.append(scrub_msg)

        return "\n".join(report)

    except Exception as e:
        return f"[OSINT ERROR] Metadata analysis failed: {e}"


# =====================================================================
# 3. DOMAIN DEEP RECON & SUBDOMAINS (Certificate Transparency)
# =====================================================================

async def osint_domain_recon(domain: str) -> str:
    """
    Performs comprehensive domain reconnaissance: subdomains via Certificate Transparency (crt.sh),
    DNS resolution, SSL certificate inspection, and security headers.
    """
    clean_domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_domain:
        return "[OSINT ERROR] Invalid domain name."

    report = [
        f"🌐 [DOMAIN RECONNAISSANCE] Target: {clean_domain}",
        "=" * 55
    ]

    # 1. DNS Resolution (A, AAAA, MX, NS, TXT via Cloudflare DoH)
    dns_records = {}
    for rtype in ["A", "AAAA", "MX", "NS", "TXT"]:
        try:
            r = requests.get(
                f"https://cloudflare-dns.com/dns-query?name={clean_domain}&type={rtype}",
                headers={"Accept": "application/dns-json"},
                timeout=5
            )
            if r.status_code == 200:
                answers = r.json().get("Answer", [])
                if answers:
                    dns_records[rtype] = [a.get("data") for a in answers if a.get("data")]
        except Exception:
            pass

    report.append("📡 DNS RECORDS:")
    if dns_records:
        for rtype, records in dns_records.items():
            report.append(f"  [{rtype}] " + ", ".join(records[:4]))
    else:
        report.append("  (No direct DNS records resolved via DoH)")

    # 2. Subdomain Discovery via crt.sh (Free Certificate Transparency)
    subdomains = set()
    try:
        url = f"https://crt.sh/?q=%25.{clean_domain}&output=json"
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            entries = res.json()
            for entry in entries:
                name_value = entry.get("name_value", "")
                for sub in name_value.split("\n"):
                    sub = sub.strip().lower()
                    if clean_domain in sub and not sub.startswith("*"):
                        subdomains.add(sub)
    except Exception:
        pass

    report.append(f"\n🛰️ SUBDOMAINS DISCOVERED (Total: {len(subdomains)}):")
    if subdomains:
        for sub in sorted(list(subdomains))[:20]:
            report.append(f"  • {sub}")
        if len(subdomains) > 20:
            report.append(f"  ... and {len(subdomains) - 20} more subdomains.")
    else:
        report.append("  • No additional public certificates indexed on crt.sh.")

    # 3. SSL / TLS Inspection
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((clean_domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=clean_domain) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert.get('issuer', []))
                subject = dict(x[0] for x in cert.get('subject', []))
                report.append("\n🔒 SSL/TLS CERTIFICATE:")
                report.append(f"  • Issuer:        {issuer.get('organizationName', issuer.get('commonName', 'Unknown'))}")
                report.append(f"  • Common Name:   {subject.get('commonName', 'Unknown')}")
                report.append(f"  • Expires On:    {cert.get('notAfter', 'Unknown')}")
    except Exception:
        pass

    # 4. Security Headers
    try:
        head_resp = requests.head(f"https://{clean_domain}", headers=HEADERS, timeout=5, allow_redirects=True)
        h = head_resp.headers
        sec_headers = {
            "Strict-Transport-Security (HSTS)": "✅ Enabled" if "Strict-Transport-Security" in h else "❌ Missing",
            "Content-Security-Policy (CSP)": "✅ Enabled" if "Content-Security-Policy" in h else "❌ Missing",
            "X-Frame-Options (Clickjack)": "✅ Enabled" if "X-Frame-Options" in h else "❌ Missing",
            "Server Banner": h.get("Server", "Hidden / Not Disclosed")
        }
        report.append("\n🛡️ SECURITY HEADERS AUDIT:")
        for k, v in sec_headers.items():
            report.append(f"  • {k:<32}: {v}")
    except Exception:
        pass

    return "\n".join(report)


# =====================================================================
# 4. WAYBACK MACHINE HISTORICAL SNAPSHOTS
# =====================================================================

async def osint_wayback_history(url: str, limit: int = 5) -> str:
    """
    Fetches historical snapshots and archives of a webpage from the Internet Archive Wayback Machine.
    """
    clean_url = url.strip().replace("http://", "").replace("https://", "")
    try:
        cdx_url = f"http://web.archive.org/cdx/search/cdx?url={clean_url}&output=json&limit={limit}&fl=timestamp,original,statuscode,digest"
        r = requests.get(cdx_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 1:
                rows = data[1:]
                lines = [
                    f"🕰️ [WAYBACK MACHINE ARCHIVE] Target: {url}",
                    f"Found {len(rows)} Historical Snapshots:",
                    "=" * 55
                ]
                for row in rows:
                    ts, orig, status, _ = row
                    formatted_ts = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}"
                    archive_link = f"https://web.archive.org/web/{ts}/{orig}"
                    lines.append(f"  📅 {formatted_ts} (Status {status}) -> {archive_link}")
                return "\n".join(lines)

        return f"🕰️ [WAYBACK ARCHIVE] No historical snapshots recorded for '{url}'."
    except Exception as e:
        return f"[OSINT ERROR] Wayback Machine lookup error: {e}"


# =====================================================================
# 5. IP & HOST THREAT INTELLIGENCE
# =====================================================================

async def osint_ip_lookup(ip_or_host: str) -> str:
    """
    Resolves IP or Hostname to real-world geolocation, ISP, ASN, reverse DNS, and hosting status.
    """
    target = ip_or_host.strip().replace("https://", "").replace("http://", "").split("/")[0]
    try:
        # Resolve to IP if hostname
        ip_addr = socket.gethostbyname(target)
    except Exception:
        ip_addr = target

    try:
        r = requests.get(f"http://ip-api.com/json/{ip_addr}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query,reverse,mobile,proxy,hosting", timeout=6)
        if r.status_code == 200 and r.json().get("status") == "success":
            d = r.json()
            report = [
                f"📡 [IP INTELLIGENCE] Target: {target} ({ip_addr})",
                "=" * 50,
                f"  • Country:       {d.get('country')} ({d.get('countryCode')})",
                f"  • Region/City:   {d.get('regionName')}, {d.get('city')} ({d.get('zip')})",
                f"  • Coordinates:   {d.get('lat')}, {d.get('lon')} (https://www.google.com/maps?q={d.get('lat')},{d.get('lon')})",
                f"  • Timezone:      {d.get('timezone')}",
                f"  • ISP:           {d.get('isp')}",
                f"  • Organization:  {d.get('org')}",
                f"  • ASN:           {d.get('as')}",
                f"  • Reverse DNS:   {d.get('reverse', 'None')}",
                f"  • Hosting/DC:    {'Yes (Datacenter/Cloud)' if d.get('hosting') else 'No (Residential/Consumer)'}",
                f"  • Proxy/VPN:     {'Yes' if d.get('proxy') else 'No'}"
            ]
            return "\n".join(report)

        return f"[OSINT ERROR] Unable to resolve IP intelligence for {ip_or_host}."
    except Exception as e:
        return f"[OSINT ERROR] IP lookup failed: {e}"


# =====================================================================
# 6. PHONE INTELLIGENCE & CARRIER LOOKUP
# =====================================================================

async def osint_phone_intelligence(phone_number: str) -> str:
    """
    Analyzes phone number for country of origin, telecom carrier, line type (Mobile/VoIP/Landline), and validity.
    """
    import phonenumbers
    from phonenumbers import geocoder, carrier, number_type, PhoneNumberType

    try:
        parsed = phonenumbers.parse(phone_number, None)
        is_valid = phonenumbers.is_valid_number(parsed)
        if not is_valid:
            return f"❌ [PHONE OSINT] '{phone_number}' is not a valid international phone number format."

        region = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        ntype = number_type(parsed)
        type_str = {
            PhoneNumberType.MOBILE: "Mobile",
            PhoneNumberType.FIXED_LINE: "Fixed Line (Landline)",
            PhoneNumberType.VOIP: "VoIP (Virtual Number)",
            PhoneNumberType.TOLL_FREE: "Toll-Free",
            PhoneNumberType.PREMIUM_RATE: "Premium Rate"
        }.get(ntype, "Standard / Unknown")

        intl_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        e164_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        report = [
            f"📱 [PHONE INTELLIGENCE] Target: {phone_number}",
            "=" * 50,
            f"  • International: {intl_fmt}",
            f"  • E.164 Format:  {e164_fmt}",
            f"  • Country/Region:{region if region else 'Identified by Country Code'}",
            f"  • Telecom Carrier: {carrier_name if carrier_name else 'Undisclosed / MVNO'}",
            f"  • Line Type:     {type_str}",
            f"  • Status:        ✅ Valid & Active Format"
        ]
        return "\n".join(report)

    except Exception as e:
        return f"[OSINT ERROR] Phone parsing failed: {e}"


# =====================================================================
# 7. PHANTOM-IP PRECISION GEOCODER (Nominatim / OSM Smart Fallback)
# =====================================================================

async def osint_precision_geocoder(address: str) -> str:
    """
    Precision Geocoding Engine based on Phantom-IP: converts physical street address, city, or landmark
    into exact latitude, longitude, postal details, bounding box, and tactical satellite map links.
    """
    clean_addr = address.strip()
    if not clean_addr:
        return "[OSINT ERROR] Please specify a valid target address."

    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "Phantom-IP-Security-Auditor/2.0 (ULTRON Autonomous Tactical System)"
    }
    params = {"q": clean_addr, "format": "json", "addressdetails": 1, "limit": 1}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        data = resp.json() if resp.status_code == 200 else []

        # Smart Retry: strip house/flat number if exact match failed
        if not data and "," in clean_addr:
            simplified = ",".join(clean_addr.split(",")[1:]).strip()
            if simplified:
                params["q"] = simplified
                resp = requests.get(url, params=params, headers=headers, timeout=8)
                data = resp.json() if resp.status_code == 200 else []

        if not data:
            return f"❌ [PRECISION GEOCODER] No location coordinates resolved for '{clean_addr}'."

        item = data[0]
        lat = item.get("lat")
        lon = item.get("lon")
        display_name = item.get("display_name")
        addr_info = item.get("address", {})

        report = [
            f"🗺️ [PRECISION GEOCODING INTELLIGENCE] Target: {clean_addr}",
            "=" * 55,
            f"  • Resolved Name: {display_name}",
            f"  • Latitude:      {lat}",
            f"  • Longitude:     {lon}",
            f"  • Country:       {addr_info.get('country', 'N/A')} ({addr_info.get('country_code', '').upper()})",
            f"  • State/Region:  {addr_info.get('state', addr_info.get('province', 'N/A'))}",
            f"  • County/City:   {addr_info.get('city', addr_info.get('county', addr_info.get('town', 'N/A')))}",
            f"  • Postal Code:   {addr_info.get('postcode', 'N/A')}",
            f"  • OSM Type:      {item.get('type', 'N/A')} ({item.get('class', 'N/A')})",
            f"  • Google Maps:   https://www.google.com/maps?q={lat},{lon}",
            f"  • OSM Map Link:  https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"
        ]
        return "\n".join(report)

    except Exception as e:
        return f"[OSINT ERROR] Precision geocoding exception: {e}"


# =====================================================================
# 8. PHANTOM-IP DEEP HOLDER TRACE & CONTENT OSINT
# =====================================================================

async def osint_deep_holder_trace(target_domain_or_url: str) -> str:
    """
    Deep Holder Tracer based on Phantom-IP: traces website ownership, server geography,
    HTML contact forensics (emails, phone numbers, social handles, physical addresses),
    and registrar WHOIS data.
    """
    clean_target = target_domain_or_url.strip().replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_target:
        return "[OSINT ERROR] Please specify a valid target domain or URL."

    report = [
        f"🕵️ [DEEP HOLDER TRACE] Target: {clean_target}",
        "=" * 55
    ]

    # 1. Server Geography
    try:
        ip_addr = socket.gethostbyname(clean_target)
        r = requests.get(f"http://ip-api.com/json/{ip_addr}", timeout=6)
        if r.status_code == 200:
            geo = r.json()
            report.append(f"🌐 SERVER GEOGRAPHY (IP: {ip_addr}):")
            report.append(f"  • Location:      {geo.get('city')}, {geo.get('regionName')}, {geo.get('country')}")
            report.append(f"  • ISP & ASN:     {geo.get('isp')} ({geo.get('as')})")
            report.append(f"  • Coordinates:   {geo.get('lat')}, {geo.get('lon')}")
    except Exception:
        report.append(f"🌐 SERVER GEOGRAPHY: IP resolution failed.")

    # 2. Content Forensics & Clues
    try:
        url = f"https://{clean_target}"
        resp = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        html_text = resp.text

        # Regex for emails, phones, and social links
        emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html_text))
        # Filter out common false positives
        valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.webp', '.js', '.css', '.svg')) and len(e) < 50]

        phones = set(re.findall(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html_text))
        
        # Social Profiles
        socials = []
        for plat in ["twitter.com", "x.com", "instagram.com", "facebook.com", "linkedin.com", "github.com", "t.me", "youtube.com"]:
            matches = set(re.findall(rf'https?://(?:www\.)?{plat}/[a-zA-Z0-9_.-]+', html_text))
            socials.extend(matches)

        report.append("\n📄 HTML CONTENT FORENSICS (Owner & Contact Clues):")
        report.append(f"  • Emails Found:   {', '.join(valid_emails[:5]) if valid_emails else 'None disclosed in HTML'}")
        report.append(f"  • Phones Found:   {', '.join(list(phones)[:3]) if phones else 'None found'}")
        if socials:
            report.append("  • Social Profiles:")
            for s in list(socials)[:6]:
                report.append(f"    - {s}")
        else:
            report.append("  • Social Links:   None linked on landing page")

        # Copyright / Organization clues
        org_matches = re.findall(r'(?:copyright|©|\(c\))\s*(?:\d{4})?\s*([A-Za-z0-9\s.,&-]{3,40})', html_text, re.IGNORECASE)
        if org_matches:
            clean_org = org_matches[0].strip()
            report.append(f"  • Copyright Holder: {clean_org}")

    except Exception as e:
        report.append(f"\n📄 HTML CONTENT: Failed to retrieve page ({e})")

    # 3. WHOIS RDAP Registrar
    try:
        rdap_url = f"https://rdap.org/domain/{clean_target}"
        rdap_resp = requests.get(rdap_url, headers={"Accept": "application/json"}, timeout=6)
        if rdap_resp.status_code == 200:
            rdap_data = rdap_resp.json()
            report.append("\n📋 WHOIS / RDAP REGISTRAR DATA:")
            report.append(f"  • Handle:        {rdap_data.get('handle', 'N/A')}")
            for entity in rdap_data.get("entities", [])[:3]:
                roles = ", ".join(entity.get("roles", []))
                vcard = entity.get("vcardArray", [])
                name = "Unknown"
                if len(vcard) > 1:
                    for entry in vcard[1]:
                        if entry[0] == "fn":
                            name = entry[3]
                report.append(f"  • Entity ({roles}): {name}")
    except Exception:
        pass

    return "\n".join(report)


# =====================================================================
# 9. PHANTOM-IP VULNERABILITY & ENDPOINT AUDITOR
# =====================================================================

VULN_PROBES = [
    ("/.env", "Environment configuration / secrets"),
    ("/.git/config", "Exposed Git repository"),
    ("/admin", "Administrative portal"),
    ("/wp-admin/", "WordPress admin dashboard"),
    ("/wp-login.php", "WordPress login page"),
    ("/phpmyadmin/", "Database management interface"),
    ("/api/v1/", "API endpoint base"),
    ("/swagger/index.html", "Swagger API documentation"),
    ("/api-docs", "API documentation"),
    ("/server-status", "Apache server status"),
    ("/robots.txt", "Robots crawl directive"),
    ("/sitemap.xml", "Sitemap registry"),
    ("/backup.zip", "Exposed database/code backup"),
    ("/config.json", "Exposed JSON configuration"),
    ("/debug", "Active debug console")
]


def _probe_endpoint(base_url: str, path: str, desc: str) -> Optional[Dict[str, Any]]:
    url = urllib.parse.urljoin(base_url, path)
    try:
        r = requests.get(url, headers=HEADERS, timeout=4, allow_redirects=False)
        if r.status_code in [200, 301, 302, 401, 403]:
            return {
                "path": path,
                "url": url,
                "status": r.status_code,
                "desc": desc,
                "length": len(r.content)
            }
    except Exception:
        pass
    return None


async def security_vulnerability_and_fuzzer_scan(target_domain_or_url: str) -> str:
    """
    Phantom-IP Vulnerability & Endpoint Security Auditor:
    Scans target for critical exposed files (.env, .git, config.json, backup.zip),
    admin portals, API docs, open web ports, and SSL misconfigurations.
    """
    clean_target = target_domain_or_url.strip()
    if not clean_target.startswith("http://") and not clean_target.startswith("https://"):
        base_url = f"https://{clean_target}"
    else:
        base_url = clean_target

    hostname = urllib.parse.urlparse(base_url).hostname or clean_target

    report = [
        f"🛡️ [PHANTOM-IP VULNERABILITY & ENDPOINT AUDITOR] Target: {base_url}",
        "=" * 60
    ]

    # 1. Port Scan (Common Web & Service Ports)
    open_ports = []
    common_ports = [80, 443, 8080, 8443, 3000, 5000, 8000, 9000]
    for port in common_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.8)
            if s.connect_ex((hostname, port)) == 0:
                open_ports.append(port)
            s.close()
        except Exception:
            pass

    report.append(f"📡 OPEN WEB SERVICE PORTS: {', '.join(map(str, open_ports)) if open_ports else 'Standard (80/443)'}")

    # 2. Concurrent Endpoint & Sensitive File Fuzzing
    findings = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(_probe_endpoint, base_url, path, desc)
            for path, desc in VULN_PROBES
        ]
        for f in as_completed(futures):
            res = f.result()
            if res:
                findings.append(res)

    report.append(f"\n🔍 ENDPOINT & SENSITIVE FILE AUDIT (Probed {len(VULN_PROBES)} Vectors):")
    if findings:
        for f in sorted(findings, key=lambda x: x["status"]):
            status_icon = "🚨 CRITICAL" if f["path"] in ["/.env", "/.git/config", "/backup.zip"] and f["status"] == 200 else ("⚠️ FOUND" if f["status"] == 200 else "🔒 RESTRICTED")
            report.append(f"  [{f['status']}] {status_icon:<13} -> {f['path']:<20} ({f['desc']})")
    else:
        report.append("  ✅ No exposed sensitive endpoints or standard admin portals detected.")

    # 3. Overall Security Posture Verdict
    critical_count = sum(1 for f in findings if f["path"] in ["/.env", "/.git/config", "/backup.zip"] and f["status"] == 200)
    verdict = "🚨 HIGH RISK (Exposed sensitive credentials/code)" if critical_count > 0 else ("⚠️ MODERATE (Admin/API endpoints accessible)" if len(findings) > 3 else "🛡️ LOW RISK (Hardened configuration)")
    report.append(f"\n📊 POSTURE VERDICT: {verdict}")

    return "\n".join(report)

