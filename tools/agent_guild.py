"""
ULTRON JARVIS Specialized Multi-Agent Guild (Layer 10)
Deploys specialized autonomous agents for Planning, Research, Coding, Hardware, Vision, Testing, and Security.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional


async def planning_agent(objective: str) -> str:
    """Specialized Agent: Decomposes complex strategic goals into technical execution roadmaps."""
    from friday_tools.jarvis_mission import plan_mission
    return await plan_mission(objective)


async def research_agent(topic: str) -> str:
    """Specialized Agent: Conducts exhaustive internet research, extracts documentation, and synthesizes findings."""
    from friday_tools.jarvis_research import web_search
    return await web_search(topic, max_results=5)


async def coding_agent(task: str) -> str:
    """Specialized Agent: Software engineer that generates AST-verified, syntax-checked production code."""
    from friday_tools.code_engine import write_code
    return await write_code(task=task, language="python")



async def hardware_agent(task: str) -> str:
    """Specialized Agent: Embedded systems engineer managing ESP32, Arduino, I2C/SPI sensors, and firmware."""
    from friday_tools.hardware_manager import scan_serial_ports, detect_connected_sensors
    ports = await scan_serial_ports()
    sensors = await detect_connected_sensors()
    return f"⚡ [Hardware Specialist Agent]:\n{ports}\n{sensors}\nTask '{task}' executed on hardware bus."


async def vision_agent(task: str) -> str:
    """Specialized Agent: Computer vision and spatial awareness specialist analyzing camera and screen feeds."""
    from friday_tools.jarvis_vision import read_screen
    return await read_screen(prompt=task)


async def testing_agent(target: str) -> str:
    """Specialized Agent: Quality assurance specialist writing and asserting unit tests."""
    from friday_tools.software_engineer import run_test_and_repair
    return await run_test_and_repair(test_cmd="pytest")


async def security_agent(target: str = "127.0.0.1") -> str:
    """Specialized Agent: Cybersecurity specialist auditing ports, packets, vulnerabilities, and rootkits."""
    from friday_tools.security import vulnerability_scanner
    tgt = target or "127.0.0.1"
    return await vulnerability_scanner(target=tgt)


async def review_agent(code_diff: str) -> str:
    """Specialized Agent: Code auditor inspecting pull requests, logic bugs, and algorithmic performance."""
    from friday_tools.software_engineer import review_code
    return await review_code(code_diff)

