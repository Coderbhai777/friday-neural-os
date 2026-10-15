"""
Cybersecurity Reconnaissance & Defensive Security Auditing Toolkit for ULTRON.
Provides passive recon, SSL auditing, HTTP security header verification, JWT inspection,
hash identification, CVE vulnerability search, and banner grabbing.
"""

import asyncio
import json
import os
import re
import socket
import ssl
import time
import urllib.request
import urllib.parse
from datetime import datetime


async def security_recon_domain(domain: str) -> str:
    """
    Enumerate passive DNS records (A, AAAA, MX, TXT, NS, CNAME), IP addresses,
    and ASN info for a domain.
    """
    domain = domain.strip().lower()
    if domain.startswith("http://") or domain.startswith("https://"):
        domain = urllib.parse.urlparse(domain).netloc

    results = {"domain": domain, "records": {}, "ips": [], "timestamp": datetime.now().isoformat()}

    def _sync_dns_recon():
        try:
            # Resolve IPv4
            try:
                addr_info = socket.getaddrinfo(domain, None, socket.AF_INET)
                results["ips"] = list(set([item[4][0] for item in addr_info]))
            except Exception as e:
                results["ips_error"] = str(e)

            # Query public DNS-over-HTTPS (Cloudflare / Google)
            doh_url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(domain)}&type=ANY"
            req = urllib.request.Request(doh_url, headers={"Accept": "application/dns-json", "User-Agent": "ULTRON-Agent/2.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                answers = data.get("Answer", [])
                results["records"]["raw_dns_count"] = len(answers)
                records_list = []
                for a in answers:
                    records_list.append({"name": a.get("name"), "type": a.get("type"), "data": a.get("data"), "TTL": a.get("TTL")})
                results["records"]["entries"] = records_list
        except Exception as e:
            results["doh_error"] = str(e)
        return results

    try:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, _sync_dns_recon)
        output = [f"🌐 DNS & Reconnaissance Report: {domain}"]
        output.append(f"  • Resolved IPs: {', '.join(res.get('ips', [])) or 'None'}")
        entries = res.get("records", {}).get("entries", [])
        if entries:
            output.append("  • DNS Records:")
            for e in entries[:15]:
                output.append(f"    - Type {e.get('type')}: {e.get('data')} (TTL: {e.get('TTL')}s)")
        else:
            output.append("  • No additional DNS records returned or Doh query timed out.")
        return "\n".join(output)
    except Exception as exc:
        return f"[SECURITY RECON ERROR] {exc}"


async def security_header_audit(url: str) -> str:
    """
    Audit HTTP response headers for missing security controls (CSP, HSTS, X-Frame-Options,
    X-Content-Type-Options, Referrer-Policy, Permissions-Policy).
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    def _sync_header_audit():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ULTRON-Audit/2.0"})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, context=ctx, timeout=6) as response:
            headers = {k.lower(): v for k, v in response.headers.items()}
            status = response.getcode()
            return status, headers

    try:
        loop = asyncio.get_event_loop()
        status, headers = await loop.run_in_executor(None, _sync_header_audit)

        checks = {
            "strict-transport-security": ("HSTS (Strict-Transport-Security)", "Enforces HTTPS connections"),
            "content-security-policy": ("CSP (Content-Security-Policy)", "Mitigates XSS and data injection"),
            "x-frame-options": ("X-Frame-Options", "Prevents clickjacking attacks"),
            "x-content-type-options": ("X-Content-Type-Options", "Prevents MIME-sniffing vulnerabilities"),
            "referrer-policy": ("Referrer-Policy", "Controls referrer information in requests"),
            "permissions-policy": ("Permissions-Policy", "Restricts browser feature access (mic, cam, geo)")
        }

        report = [f"🛡️ HTTP Security Header Audit: {url} (HTTP {status})"]
        present_count = 0
        for header_key, (name, purpose) in checks.items():
            if header_key in headers:
                present_count += 1
                val = headers[header_key]
                if len(val) > 70:
                    val = val[:67] + "..."
                report.append(f"  ✅ {name}: Present -> {val}")
            else:
                report.append(f"  ❌ {name}: MISSING -> {purpose}")

        score = int((present_count / len(checks)) * 100)
        report.insert(1, f"  📊 Security Score: {score}/100 ({present_count}/{len(checks)} controls configured)")
        return "\n".join(report)
    except Exception as exc:
        return f"[HEADER AUDIT ERROR] Failed to audit headers for {url}: {exc}"


async def ssl_cert_inspector(hostname: str, port: int = 443) -> str:
    """
    Inspect SSL/TLS certificate validity, issuer, SAN names, expiry date, and cipher suite.
    """
    hostname = hostname.strip().lower()
    if "://" in hostname:
        parsed = urllib.parse.urlparse(hostname)
        hostname = parsed.hostname or hostname

    def _sync_ssl():
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                return cert, cipher, version

    try:
        loop = asyncio.get_event_loop()
        cert, cipher, version = await loop.run_in_executor(None, _sync_ssl)

        not_after = cert.get("notAfter", "")
        not_before = cert.get("notBefore", "")
        subject = dict(x[0] for x in cert.get("subject", ()))
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        san = [x[1] for x in cert.get("subjectAltName", ()) if x[0] == "DNS"]

        expiry_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z") if not_after else None
        days_left = (expiry_dt - datetime.utcnow()).days if expiry_dt else "Unknown"

        status_emoji = "🟢" if (isinstance(days_left, int) and days_left > 14) else "🔴"

        report = [
            f"🔒 SSL/TLS Certificate Report for {hostname}:{port}",
            f"  {status_emoji} Status: Active (Expires in {days_left} days)",
            f"  • Common Name (CN): {subject.get('commonName', 'N/A')}",
            f"  • Organization (O): {subject.get('organizationName', 'N/A')}",
            f"  • Issuer: {issuer.get('organizationName', issuer.get('commonName', 'N/A'))}",
            f"  • Valid From: {not_before}",
            f"  • Valid Until: {not_after}",
            f"  • Protocol Version: {version}",
            f"  • Active Cipher: {cipher[0]} ({cipher[2]} bits)",
            f"  • SAN Domains: {', '.join(san[:6]) if san else 'None'}"
        ]
        return "\n".join(report)
    except Exception as exc:
        return f"[SSL INSPECT ERROR] Could not retrieve SSL certificate for {hostname}: {exc}"


async def jwt_token_analyzer(token: str) -> str:
    """
    Decode, inspect claims, algorithm, and validity periods of a JWT token.
    """
    token = token.strip()
    parts = token.split(".")
    if len(parts) != 3:
        return "[JWT ERROR] Invalid JWT format. Expected 3 base64url segments separated by dots."

    import base64

    def _b64_decode(seg: str) -> dict:
        seg += "=" * (-len(seg) % 4)
        raw = base64.urlsafe_b64decode(seg)
        return json.loads(raw.decode("utf-8", errors="ignore"))

    try:
        header = _b64_decode(parts[0])
        payload = _b64_decode(parts[1])

        alg = header.get("alg", "None")
        typ = header.get("typ", "JWT")
        exp = payload.get("exp")
        iat = payload.get("iat")
        nbf = payload.get("nbf")
        sub = payload.get("sub", "N/A")
        iss = payload.get("iss", "N/A")

        now = time.time()
        exp_status = "No Expiry Claim"
        if exp:
            exp_dt = datetime.fromtimestamp(exp)
            if now > exp:
                exp_status = f"🔴 EXPIRED on {exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            else:
                exp_status = f"🟢 VALID until {exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}"

        warnings = []
        if alg.lower() == "none":
            warnings.append("CRITICAL: Token uses insecure algorithm 'none' (signature bypass vulnerability).")
        if alg.upper() == "HS256":
            warnings.append("INFO: Symmetric HMAC-SHA256 signature (ensure secret is >= 256 bits).")

        report = [
            f"🔑 JWT Token Analysis",
            f"  • Algorithm: {alg} (Type: {typ})",
            f"  • Expiration: {exp_status}",
            f"  • Subject (sub): {sub}",
            f"  • Issuer (iss): {iss}",
            f"  • Header: {json.dumps(header)}",
            f"  • Claims Count: {len(payload)} keys",
            f"  • Payload Keys: {', '.join(payload.keys())}"
        ]
        if warnings:
            report.append("  ⚠️ Security Notes:")
            for w in warnings:
                report.append(f"    - {w}")
        return "\n".join(report)
    except Exception as exc:
        return f"[JWT ANALYZE ERROR] Failed to parse JWT token: {exc}"


async def hash_identifier(hash_str: str) -> str:
    """
    Identify potential cryptographic hash algorithms by length, charset, and format.
    """
    h = hash_str.strip()
    length = len(h)
    hex_chars = bool(re.match(r"^[a-fA-F0-9]+$", h))

    possibilities = []
    if length == 32 and hex_chars:
        possibilities = ["MD5", "NTLM", "MD4", "Domain Cached Credentials (DCC)"]
    elif length == 40 and hex_chars:
        possibilities = ["SHA-1", "RIPEMD-160", "MySQL 4.1+"]
    elif length == 64 and hex_chars:
        possibilities = ["SHA-256", "HMAC-SHA256", "Keccak-256", "BLAKE2s"]
    elif length == 128 and hex_chars:
        possibilities = ["SHA-512", "Whirlpool", "BLAKE2b"]
    elif h.startswith("$2a$") or h.startswith("$2b$") or h.startswith("$2y$"):
        possibilities = ["bcrypt (Blowfish Password Hash)"]
    elif h.startswith("$argon2"):
        possibilities = ["Argon2 Password Hash"]
    elif h.startswith("$6$"):
        possibilities = ["SHA-512 Crypt Unix"]
    elif h.startswith("$5$"):
        possibilities = ["SHA-256 Crypt Unix"]
    elif h.startswith("$1$"):
        possibilities = ["MD5 Crypt Unix"]
    else:
        possibilities = ["Unknown / Custom Format / Non-standard salt"]

    return f"🔍 Hash Identifier for '{h[:20]}...' (Length: {length} chars):\n  • Most Probable Types: {', '.join(possibilities)}"


async def cve_vulnerability_search(product: str, version: str = "") -> str:
    """
    Search National Vulnerability Database (NVD) / CVE feeds for known vulnerabilities.
    """
    product = product.strip()
    query = f"{product} {version}".strip()
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={urllib.parse.quote(query)}&resultsPerPage=5"

    def _sync_cve():
        req = urllib.request.Request(url, headers={"User-Agent": "ULTRON-CVE-Agent/2.0"})
        with urllib.request.urlopen(req, timeout=7) as resp:
            return json.loads(resp.read().decode())

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _sync_cve)
        vulns = data.get("vulnerabilities", [])
        if not vulns:
            return f"✅ No high-profile CVE records found for '{query}' in NVD top results."

        report = [f"🚨 CVE Vulnerability Intelligence for '{query}' ({len(vulns)} results):"]
        for item in vulns:
            cve_obj = item.get("cve", {})
            cve_id = cve_obj.get("id", "Unknown")
            desc_list = cve_obj.get("descriptions", [])
            desc = desc_list[0].get("value", "No description") if desc_list else "No description"
            metrics = cve_obj.get("metrics", {})
            cvss_score = "N/A"
            for cvss_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                if cvss_key in metrics and metrics[cvss_key]:
                    cvss_score = metrics[cvss_key][0].get("cvssData", {}).get("baseScore", "N/A")
                    break

            if len(desc) > 130:
                desc = desc[:127] + "..."
            report.append(f"  • {cve_id} (CVSS: {cvss_score}): {desc}")

        return "\n".join(report)
    except Exception as exc:
        return f"[CVE SEARCH ERROR] Unable to query NVD database: {exc}"


async def port_banner_grabber(host: str, ports: str = "21,22,25,80,443,3306,5432,6379,8080") -> str:
    """
    Asynchronously probe open ports and grab initial service banners.
    """
    host = host.strip()
    if "://" in host:
        host = urllib.parse.urlparse(host).netloc

    port_list = []
    for p in ports.split(","):
        p = p.strip()
        if p.isdigit():
            port_list.append(int(p))

    async def _probe(p):
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, p), timeout=1.8)
            banner = ""
            try:
                # Send minimal probe if port is HTTP
                if p in (80, 8080):
                    writer.write(b"HEAD / HTTP/1.0\r\n\r\n")
                    await writer.drain()
                data = await asyncio.wait_for(reader.read(256), timeout=1.2)
                banner = data.decode(errors="ignore").strip().replace("\r", " ").replace("\n", " ")
            except Exception:
                pass
            finally:
                writer.close()
                await writer.wait_closed()
            return p, True, banner[:60]
        except Exception:
            return p, False, ""

    results = await asyncio.gather(*[_probe(p) for p in port_list])
    open_ports = [r for r in results if r[1]]

    if not open_ports:
        return f"📡 Port Scan for {host}: Probed {len(port_list)} ports. All filtered or closed."

    report = [f"📡 Port Scan & Service Banners for {host}:"]
    for p, _, banner in open_ports:
        b_str = f" -> Banner: '{banner}'" if banner else ""
        report.append(f"  🟢 Port {p}/TCP OPEN{b_str}")
    return "\n".join(report)
