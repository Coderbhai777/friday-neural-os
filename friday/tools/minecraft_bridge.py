"""
ULTRON Minecraft Server Integration Bridge
Enables ULTRON to query status, monitor online players, execute RCON commands,
broadcast alerts, and control game environments in real-time.
"""

import os
import asyncio
from typing import Optional

try:
    from mcstatus import JavaServer
except ImportError:
    JavaServer = None

try:
    from mcrcon import MCRcon
except ImportError:
    MCRcon = None


def _get_default_rcon_creds():
    host = os.getenv("MINECRAFT_HOST", "localhost")
    port = int(os.getenv("MINECRAFT_RCON_PORT", "25575"))
    pwd = os.getenv("MINECRAFT_RCON_PASSWORD", "")
    return host, port, pwd


async def minecraft_server_status(host: str = "localhost", port: int = 25565) -> str:
    """
    Queries a Minecraft Java server for online status, player count, player names, MOTD, and latency.
    """
    if not JavaServer:
        return "❌ mcstatus module not loaded."

    def _query():
        try:
            server = JavaServer.lookup(f"{host}:{port}")
            status = server.status()
            return {
                "online": True,
                "version": status.version.name,
                "latency_ms": round(status.latency, 2),
                "players_online": status.players.online,
                "players_max": status.players.max,
                "player_sample": [p.name for p in status.players.sample] if status.players.sample else [],
                "motd": status.description if isinstance(status.description, str) else status.description.get('text', str(status.description))
            }
        except Exception as e:
            return {"online": False, "error": str(e)}

    data = await asyncio.to_thread(_query)
    if not data.get("online"):
        return f"❌ Minecraft server at {host}:{port} is offline or unreachable: {data.get('error')}"

    players = ", ".join(data["player_sample"]) if data["player_sample"] else "None"
    return (
        f"🎮 Minecraft Server Status ({host}:{port}):\n"
        f"• Status: 🟢 ONLINE\n"
        f"• Version: {data['version']}\n"
        f"• Latency: {data['latency_ms']} ms\n"
        f"• Players: {data['players_online']}/{data['players_max']} [{players}]\n"
        f"• MOTD: {data['motd']}"
    )


async def minecraft_send_command(
    command: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    password: Optional[str] = None
) -> str:
    """
    Sends an administrative command to the Minecraft server via RCON (e.g. 'time set day', 'weather clear', 'give player diamond 64').
    """
    if not MCRcon:
        return "❌ mcrcon module not loaded."

    def_host, def_port, def_pwd = _get_default_rcon_creds()
    rcon_host = host or def_host
    rcon_port = port or def_port
    rcon_pwd = password or def_pwd

    if not rcon_pwd:
        return "⚠️ RCON Password is required. Set MINECRAFT_RCON_PASSWORD in your environment or provide it in the command."

    if command.startswith("/"):
        command = command[1:]

    def _exec():
        try:
            with MCRcon(rcon_host, rcon_pwd, port=rcon_port) as mcr:
                resp = mcr.command(command)
                return True, resp
        except Exception as e:
            return False, str(e)

    success, resp = await asyncio.to_thread(_exec)
    if success:
        return f"✅ Command executed: '/{command}'\nResponse: {resp or '[Command executed successfully with no output]'}"
    else:
        return f"❌ Failed to execute command '/{command}' via RCON: {resp}"


async def minecraft_broadcast_message(
    message: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    password: Optional[str] = None
) -> str:
    """
    Broadcasts an in-game message from ULTRON to all players currently on the server.
    """
    formatted_cmd = f"tellraw @a [\"\",{{\"text\":\"[ULTRON] \",\"color\":\"gold\",\"bold\":true}},{{\"text\":\"{message}\",\"color\":\"aqua\"}}]"
    return await minecraft_send_command(formatted_cmd, host, port, password)


async def minecraft_set_weather_time(
    weather: str = "clear",
    time_of_day: str = "day",
    host: Optional[str] = None,
    port: Optional[int] = None,
    password: Optional[str] = None
) -> str:
    """
    Changes the in-game weather (clear, rain, thunder) and time (day, noon, night, midnight) in one call.
    """
    res1 = await minecraft_send_command(f"weather {weather}", host, port, password)
    res2 = await minecraft_send_command(f"time set {time_of_day}", host, port, password)
    return f"🌤️ Environment Updated:\n{res1}\n{res2}"


_BOT_PROCESS = None

async def start_minecraft_player_bot(
    host: str = "hamaraserverkabap.aternos.me",
    port: int = 40350,
    username: str = "ULTRON",
    edition: str = "bedrock"
) -> str:
    """
    Launches an autonomous in-game player bot (named ULTRON) to connect directly to the Minecraft SMP server.
    Supports both Bedrock ('bedrock') and Java ('java') editions.
    """
    global _BOT_PROCESS
    import subprocess

    script_name = "bedrock_bot.js" if edition.lower() == "bedrock" else "bot.js"
    bot_script = os.path.join(os.path.expanduser("~"), "Documents", "ULTRON_Data", "minecraft_bot", script_name)
    if not os.path.exists(bot_script):
        return f"❌ Bot script not found at {bot_script}"

    if _BOT_PROCESS and _BOT_PROCESS.poll() is None:
        return "⚠️ ULTRON Minecraft Player Bot is already active and running in the server."

    # Pre-flight check: is server actually online?
    try:
        from mcstatus import BedrockServer, JavaServer
        if edition.lower() == "bedrock":
            s = BedrockServer.lookup(f"{host}:{port}")
            status = s.status()
            if "offline" in str(status.motd.raw).lower():
                return f"⚠️ The Aternos server at {host}:{port} is currently OFFLINE. Please click 'Start' on your Aternos dashboard first."
        else:
            s = JavaServer.lookup(f"{host}:{port}")
            s.status()
    except Exception as e:
        return f"⚠️ The Aternos SMP at {host}:{port} is currently OFFLINE or loading ({e}). Please start it on aternos.org first."

    env = os.environ.copy()
    env["MC_HOST"] = host
    env["MC_PORT"] = str(port)
    env["MC_USERNAME"] = username

    try:
        _BOT_PROCESS = subprocess.Popen(
            ["node", bot_script],
            cwd=os.path.dirname(bot_script),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return f"🟢 Server verified online! ULTRON is now logging into the SMP at {host}:{port} as player '{username}'."
    except Exception as e:
        return f"❌ Failed to launch Minecraft bot: {e}"



async def stop_minecraft_player_bot() -> str:
    """
    Disconnects the ULTRON player bot from the Minecraft SMP server.
    """
    global _BOT_PROCESS
    if not _BOT_PROCESS or _BOT_PROCESS.poll() is not None:
        return "ℹ️ ULTRON Minecraft Player Bot is not currently running."

    try:
        _BOT_PROCESS.terminate()
        _BOT_PROCESS.wait(timeout=5)
        _BOT_PROCESS = None
        return "🔌 ULTRON Minecraft Player Bot has disconnected from the server."
    except Exception as e:
        return f"❌ Error disconnecting bot: {e}"

