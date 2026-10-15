"""
ULTRON Security & Vulnerability Auditing Engine
Comprehensive defensive security assessment, host hardening, web configuration auditing,
and forensic integrity analysis.
"""

import os
import sys
import json
import time
import socket
import ssl
import hashlib
import subprocess
from typing import Dict, List, Any, Optional

try:
    import psutil
except ImportError:
    psutil = None

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass


async def audit_web_security_headers(url: str) -> str:
    """
    Audits HTTP security response headers for a given URL (HSTS, CSP, X-Frame-Options, etc.)
    and provides a security posture score.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers_to_check = {
        "Strict-Transport-Security": "Protects against SSL stripping / man-in-the-middle attacks.",
        "Content-Security-Policy": "Mitigates Cross-Site Scripting (XSS) and data injection.",
        "X-Frame-Options": "Prevents Clickjacking attacks (DENY / SAMEORIGIN).",
        "X-Content-Type-Options": "Prevents MIME-sniffing exploits (nosniff).",
        "Referrer-Policy": "Controls referrer information leakage.",
        "Permissions-Policy": "Restricts browser feature permissions (camera, mic, geolocation)."
    }

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ULTRON-SecurityAuditor/2.0"}
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            resp_headers = {k.title(): v for k, v in response.headers.items()}
            status_code = response.status

        present = {}
        missing = {}

        for h, desc in headers_to_check.items():
            found = False
            for resp_h, val in resp_headers.items():
                if resp_h.lower() == h.lower():
                    present[h] = val
                    found = True
                    break
            if not found:
                missing[h] = desc

        score = int((len(present) / len(headers_to_check)) * 100)

        report = [
            f"🛡️ Web Security Header Audit for: {url}",
            f"HTTP Status: {status_code} | Security Header Compliance Score: {score}%\n",
            "✅ Present Headers:"
        ]
        if present:
            for k, v in present.items():
                report.append(f"  • {k}: {v[:80]}..." if len(v) > 80 else f"  • {k}: {v}")
        else:
            report.append("  (None found)")

        report.append("\n⚠️ Missing Security Headers:")
        if missing:
            for k, desc in missing.items():
                report.append(f"  • {k} ➔ {desc}")
        else:
            report.append("  (All recommended security headers are implemented)")

        return "\n".join(report)

    except Exception as e:
        return f"❌ Security header audit failed for {url}: {e}"


async def audit_ssl_tls_certificate(domain: str) -> str:
    """
    Audits the SSL/TLS configuration, certificate expiration, cipher suite, and issuer for a domain.
    """
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()

        subject = dict(x[0] for x in cert.get('subject', ()))
        issuer = dict(x[0] for x in cert.get('issuer', ()))
        not_after = cert.get('notAfter', 'Unknown')
        not_before = cert.get('notBefore', 'Unknown')
        san = [x[1] for x in cert.get('subjectAltName', []) if x[0] == 'DNS']

        report = [
            f"🔒 SSL/TLS Certificate Audit: {domain}",
            f"• Protocol Version: {version}",
            f"• Negotiated Cipher: {cipher[0]} ({cipher[2]} bits)",
            f"• Common Name (CN): {subject.get('commonName', 'Unknown')}",
            f"• Organization: {subject.get('organizationName', 'N/A')}",
            f"• Issued By: {issuer.get('organizationName', issuer.get('commonName', 'Unknown'))}",
            f"• Valid From: {not_before}",
            f"• Valid Until: {not_after}",
            f"• SAN Alternate Domains ({len(san)}): {', '.join(san[:5])}{' ...' if len(san) > 5 else ''}"
        ]
        return "\n".join(report)

    except Exception as e:
        return f"❌ SSL/TLS audit failed for {domain}: {e}"


async def audit_windows_firewall_status() -> str:
    """
    Audits the current status of Windows Defender Firewall across Domain, Private, and Public profiles.
    """
    try:
        cmd = "netsh advfirewall show allprofiles state"
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        
        report = ["🛡️ Windows Defender Firewall Status Audit:"]
        for line in lines:
            if "Profile Settings:" in line or "State" in line:
                report.append(f"  {line}")
        
        return "\n".join(report)
    except Exception as e:
        return f"❌ Firewall audit failed: {e}"


async def audit_listening_services_and_ports() -> str:
    """
    Correlates all active listening TCP and UDP sockets with their host process names, PIDs, and binaries.
    """
    if not psutil:
        return "❌ psutil is required for port to process correlation."

    try:
        report = [
            "📡 Active Listening Sockets & Host Process Mapping:",
            f"{'Proto':<6} {'Local Address':<22} {'PID':<8} {'Process Name':<25} {'Status'}",
            "-" * 75
        ]

        connections = psutil.net_connections(kind='inet')
        listening = [c for c in connections if c.status == 'LISTEN' or c.type == socket.SOCK_DGRAM]

        seen = set()
        for conn in listening:
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
            proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            pid = conn.pid or 0
            
            key = (proto, laddr, pid)
            if key in seen:
                continue
            seen.add(key)

            pname = "Unknown"
            if pid > 0:
                try:
                    pname = psutil.Process(pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pname = "[System/Protected]"

            report.append(f"{proto:<6} {laddr:<22} {pid:<8} {pname:<25} {conn.status or 'OPEN'}")

        return "\n".join(report[:40]) + (f"\n... and {len(report) - 40} more sockets" if len(report) > 40 else "")

    except Exception as e:
        return f"❌ Listening port audit failed: {e}"


async def audit_file_integrity(directory_path: str, baseline_file: Optional[str] = None) -> str:
    """
    Computes cryptographic SHA-256 hashes of all files in a target directory
    and compares against a baseline to detect unauthorized changes, insertions, or deletions.
    """
    if not os.path.exists(directory_path):
        return f"❌ Target directory not found: {directory_path}"

    if not baseline_file:
        baseline_file = os.path.join(
            os.path.expanduser("~"), "Documents", "ULTRON_Data",
            f"fim_{hashlib.md5(directory_path.encode()).hexdigest()[:8]}.json"
        )

    current_hashes = {}
    for root, _, files in os.walk(directory_path):
        for f in files:
            fpath = os.path.join(root, f)
            try:
                h = hashlib.sha256()
                with open(fpath, "rb") as fp:
                    while chunk := fp.read(65536):
                        h.update(chunk)
                current_hashes[os.path.relpath(fpath, directory_path)] = h.hexdigest()
            except (PermissionError, OSError):
                continue

    if not os.path.exists(baseline_file):
        os.makedirs(os.path.dirname(baseline_file), exist_ok=True)
        with open(baseline_file, "w", encoding="utf-8") as fp:
            json.dump({"timestamp": time.time(), "directory": directory_path, "hashes": current_hashes}, fp, indent=2)
        return f"✅ Baseline created for '{directory_path}' ({len(current_hashes)} files hashed). Saved to: {baseline_file}"

    with open(baseline_file, "r", encoding="utf-8") as fp:
        baseline_data = json.load(fp)
    baseline_hashes = baseline_data.get("hashes", {})

    added = [f for f in current_hashes if f not in baseline_hashes]
    removed = [f for f in baseline_hashes if f not in current_hashes]
    modified = [f for f in current_hashes if f in baseline_hashes and current_hashes[f] != baseline_hashes[f]]

    report = [
        f"🔍 File Integrity Monitor (FIM) Report: {directory_path}",
        f"Total Scanned Files: {len(current_hashes)} | Baseline Records: {len(baseline_hashes)}",
    ]

    if not added and not removed and not modified:
        report.append("✅ 100% Integrity Match: No files modified, added, or deleted.")
    else:
        if modified:
            report.append(f"\n🚨 MODIFIED FILES ({len(modified)}):")
            for m in modified:
                report.append(f"  • {m}")
        if added:
            report.append(f"\n⚠️ NEW/ADDED FILES ({len(added)}):")
            for a in added:
                report.append(f"  • {a}")
        if removed:
            report.append(f"\n❌ REMOVED/DELETED FILES ({len(removed)}):")
            for r in removed:
                report.append(f"  • {r}")

    return "\n".join(report)


async def audit_dns_security_records(domain: str) -> str:
    """
    Queries DNS records (SPF, DMARC, MX, TXT) for email spoofing and domain authentication posture.
    """
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
    
    try:
        # Query TXT records for SPF and DMARC
        ps_script = f"""
        $txt = Resolve-DnsName -Name '{domain}' -Type TXT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Strings
        $dmarc = Resolve-DnsName -Name '_dmarc.{domain}' -Type TXT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Strings
        $mx = Resolve-DnsName -Name '{domain}' -Type MX -ErrorAction SilentlyContinue | Select-Object -ExpandProperty NameExchange
        [PSCustomObject]@{{
            TXT = $txt
            DMARC = $dmarc
            MX = $mx
        }} | ConvertTo-Json
        """
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=10)
        data = json.loads(res.stdout) if res.stdout.strip() else {}

        spf_record = "None"
        txt_records = data.get("TXT", [])
        if isinstance(txt_records, str):
            txt_records = [txt_records]
        for t in txt_records:
            if "v=spf1" in t:
                spf_record = t
                break

        dmarc_records = data.get("DMARC", [])
        if isinstance(dmarc_records, str):
            dmarc_records = [dmarc_records]

        mx_records = data.get("MX", [])
        if isinstance(mx_records, str):
            mx_records = [mx_records]

        report = [
            f"🌐 DNS Domain Security & Spoofing Audit: {domain}",
            f"• MX Records ({len(mx_records)}): {', '.join(mx_records[:3]) if mx_records else 'None'}",
            f"• SPF Configuration: {spf_record}",
            f"• DMARC Record: {dmarc_records[0] if dmarc_records else '❌ Missing (Domain vulnerable to email spoofing)'}",
        ]
        return "\n".join(report)

    except Exception as e:
        return f"❌ DNS security audit failed: {e}"
