"""
DevOps, Docker & Cloud Infrastructure Management Toolkit for ULTRON.
Provides Docker container lifecycle control, Docker Compose orchestration, system service supervision,
Nginx reverse proxy generation, and Cloudflare DNS management.
"""

import asyncio
import json
import os
import shutil
import subprocess
import urllib.request
import urllib.parse


async def docker_container_manage(action: str = "list", container: str = "") -> str:
    """
    Manage Docker containers: list, start, stop, restart, pause, unpause, inspect, or logs.
    """
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return "[DOCKER ERROR] Docker CLI binary not found in PATH. Ensure Docker Desktop or Docker engine is running."

    action = action.lower().strip()
    container = container.strip()

    def _run_docker(cmd_args):
        try:
            res = subprocess.run([docker_bin] + cmd_args, capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                return res.stdout.strip()
            return f"[DOCKER CMD ERROR] {res.stderr.strip()}"
        except Exception as e:
            return f"[EXECUTION ERROR] {e}"

    loop = asyncio.get_event_loop()

    if action in ("list", "ps"):
        out = await loop.run_in_executor(None, lambda: _run_docker(["ps", "-a", "--format", "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"]))
        return f"🐳 Docker Container Overview:\n{out}"
    elif action in ("start", "stop", "restart", "pause", "unpause", "kill"):
        if not container:
            return f"[DOCKER ERROR] Container name or ID required for action '{action}'."
        out = await loop.run_in_executor(None, lambda: _run_docker([action, container]))
        return f"🐳 Docker '{action}' on '{container}': {out}"
    elif action in ("logs", "log"):
        if not container:
            return "[DOCKER ERROR] Container name or ID required for logs."
        out = await loop.run_in_executor(None, lambda: _run_docker(["logs", "--tail", "50", container]))
        return f"🐳 Logs for {container} (last 50 lines):\n{out}"
    elif action in ("inspect", "stats"):
        if not container:
            return f"[DOCKER ERROR] Container name or ID required for {action}."
        out = await loop.run_in_executor(None, lambda: _run_docker([action, "--no-stream" if action == "stats" else "", container]))
        return f"🐳 Container {action} ({container}):\n{out}"
    else:
        return f"[DOCKER ERROR] Unsupported action '{action}'. Options: list, start, stop, restart, pause, logs, inspect, stats."


async def docker_compose_up(compose_file: str = "docker-compose.yml", detach: bool = True) -> str:
    """
    Orchestrate microservices with Docker Compose up.
    """
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return "[DOCKER ERROR] Docker CLI binary not found in PATH."

    def _compose_up():
        cmd = [docker_bin, "compose"]
        if os.path.exists(compose_file):
            cmd.extend(["-f", compose_file])
        cmd.append("up")
        if detach:
            cmd.append("-d")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return res.stdout.strip() or res.stderr.strip()

    try:
        loop = asyncio.get_event_loop()
        out = await loop.run_in_executor(None, _compose_up)
        return f"🚀 Docker Compose Up:\n{out}"
    except Exception as exc:
        return f"[DOCKER COMPOSE ERROR] {exc}"


async def docker_compose_down(compose_file: str = "docker-compose.yml") -> str:
    """
    Teardown microservices with Docker Compose down.
    """
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return "[DOCKER ERROR] Docker CLI binary not found in PATH."

    def _compose_down():
        cmd = [docker_bin, "compose"]
        if os.path.exists(compose_file):
            cmd.extend(["-f", compose_file])
        cmd.append("down")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return res.stdout.strip() or res.stderr.strip()

    try:
        loop = asyncio.get_event_loop()
        out = await loop.run_in_executor(None, _compose_down)
        return f"🛑 Docker Compose Down:\n{out}"
    except Exception as exc:
        return f"[DOCKER COMPOSE ERROR] {exc}"


async def docker_prune_system(all_unused: bool = False) -> str:
    """
    Prune unused Docker containers, networks, images, and volumes to free up disk storage.
    """
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return "[DOCKER ERROR] Docker CLI binary not found in PATH."

    def _prune():
        cmd = [docker_bin, "system", "prune", "-f"]
        if all_unused:
            cmd.append("-a")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return res.stdout.strip() or res.stderr.strip()

    try:
        loop = asyncio.get_event_loop()
        out = await loop.run_in_executor(None, _prune)
        return f"🧹 Docker System Prune:\n{out}"
    except Exception as exc:
        return f"[DOCKER PRUNE ERROR] {exc}"


async def system_service_manager(service_name: str, action: str = "status") -> str:
    """
    Start, stop, restart, or query the status of Windows Services (via sc.exe / PowerShell).
    """
    service_name = service_name.strip()
    action = action.lower().strip()

    def _manage():
        if os.name == "nt":
            if action in ("status", "query"):
                res = subprocess.run(["sc.exe", "query", service_name], capture_output=True, text=True, timeout=5)
                return res.stdout.strip()
            elif action in ("start", "stop", "restart"):
                if action == "restart":
                    subprocess.run(["sc.exe", "stop", service_name], capture_output=True, text=True, timeout=5)
                    import time
                    time.sleep(1)
                    res = subprocess.run(["sc.exe", "start", service_name], capture_output=True, text=True, timeout=5)
                else:
                    res = subprocess.run(["sc.exe", action, service_name], capture_output=True, text=True, timeout=5)
                return res.stdout.strip() or res.stderr.strip()
        else:
            res = subprocess.run(["systemctl", action, service_name], capture_output=True, text=True, timeout=5)
            return res.stdout.strip() or res.stderr.strip()

    try:
        loop = asyncio.get_event_loop()
        out = await loop.run_in_executor(None, _manage)
        return f"⚙️ Service Manager [{action.upper()}] for '{service_name}':\n{out}"
    except Exception as exc:
        return f"[SERVICE MANAGER ERROR] {exc}"


async def nginx_config_generator(domain: str, proxy_target: str = "http://127.0.0.1:3000", enable_ssl: bool = True, websockets: bool = True) -> str:
    """
    Auto-generate production-ready Nginx reverse proxy configuration.
    """
    domain = domain.strip().lower()
    proxy_target = proxy_target.strip()

    ws_block = ""
    if websockets:
        ws_block = """
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";"""

    if enable_ssl:
        config = f"""# Nginx Configuration for {domain} (SSL + Reverse Proxy)
server {{
    listen 80;
    server_name {domain} www.{domain};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {domain} www.{domain};

    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    location / {{
        proxy_pass {proxy_target};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;{ws_block}
    }}
}}
"""
    else:
        config = f"""# Nginx Configuration for {domain} (HTTP Reverse Proxy)
server {{
    listen 80;
    server_name {domain} www.{domain};

    location / {{
        proxy_pass {proxy_target};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;{ws_block}
    }}
}}
"""
    return f"📄 Generated Nginx Configuration:\n\n{config}"


async def cloud_cloudflare_dns(zone_id: str = "", action: str = "list", record_name: str = "", ip: str = "", api_token: str = "") -> str:
    """
    Query or manage Cloudflare DNS records via the Cloudflare REST API v4.
    """
    api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN", "")
    zone_id = zone_id or os.getenv("CLOUDFLARE_ZONE_ID", "")

    if not api_token or not zone_id:
        return "[CLOUDFLARE ERROR] CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID required in environment or parameters."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"

    def _sync_cf():
        if action == "list":
            req = urllib.request.Request(base_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                records = data.get("result", [])
                report = [f"☁️ Cloudflare DNS Records ({len(records)} entries):"]
                for r in records[:20]:
                    report.append(f"  • {r.get('type')} {r.get('name')} -> {r.get('content')} (Proxied: {r.get('proxied')})")
                return "\n".join(report)
        elif action == "create":
            if not record_name or not ip:
                return "[CLOUDFLARE ERROR] record_name and ip required for create action."
            payload = json.dumps({"type": "A", "name": record_name, "content": ip, "ttl": 1, "proxied": True}).encode()
            req = urllib.request.Request(base_url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                return f"✅ Cloudflare DNS Record Created: {data.get('success')}"
        return f"[CLOUDFLARE ERROR] Unsupported action '{action}'."

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_cf)
    except Exception as exc:
        return f"[CLOUDFLARE API ERROR] {exc}"
