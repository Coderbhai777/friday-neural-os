
import os
import json
import time
import asyncio
import platform
import psutil
from datetime import datetime
from typing import List, Dict, Any, Optional


class AntiGravityEngine:
    """Advanced Intelligence Engine for ULTRON."""

    def __init__(self, tools=None):
        self.tools = tools or []
        self.goal_stack = []
        self.skill_cache = {}
        self.runtime_state = {}
        self.trace_log = []
        self.confidence_score = 1.0

    async def process_task(self, task: str):
        self.add_trace(f"Initiated: {task}")
        env_state = self.get_environment_awareness()
        self.add_trace(f"Env: {env_state['os']} | CPU: {env_state['cpu']}%")
        context = self.retrieve_multi_layer_memory(task)
        plan = await self.generate_plan(task, context)
        self.add_trace(f"Strategy: {len(plan)} steps")

        for step in plan:
            risk = self.simulate_action(step)
            if risk > 0.7:
                self.add_trace(f"HIGH RISK for '{step['action']}'")

        results = []
        for i, step in enumerate(plan):
            self.add_trace(f"Step {i+1}: {step['description']}")
            result = await self.execute_step(step)
            if "error" in result.lower() or "failed" in result.lower():
                self.add_trace("Step Failed. Re-planning...")
                new_plan = await self.rephrase_plan(task, results, step)
                plan.extend(new_plan)
                continue
            results.append(result)
            reflection = self.self_reflect(step, result)
            self.add_trace(f"Reflection: {reflection}")

        if results:
            self.learn_skill(task, plan)
        return results[-1] if results else "Task completed."

    async def generate_plan(self, task: str, context: str):
        return [
            {"action": "analyze", "description": f"Identify requirements: {task}"},
            {"action": "lookup", "description": "Check knowledge and tools"},
            {"action": "execute", "description": f"Perform action: {task}"},
        ]

    async def execute_step(self, step: Dict):
        action = step.get("action", "").lower()
        desc = step.get("description", "")
        self.add_trace(f"Emitted: execute_{action} ({desc})")
        if "ask" in action or "request" in action:
            return await self.request_user_intervention(desc)
        return f"Processed: {desc}"

    async def request_user_intervention(self, prompt: str):
        self.add_trace(f"REQUEST: {prompt}")
        return f"User intervention requested: {prompt}"

    def self_reflect(self, step: Dict, result: str):
        if "success" in result.lower():
            self.confidence_score = min(1.0, self.confidence_score + 0.05)
            return "Outcome matches objective."
        self.confidence_score = max(0.0, self.confidence_score - 0.2)
        return "Divergence detected. Correction required."

    def get_environment_awareness(self):
        self.runtime_state = {
            "os": platform.system(),
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "time": datetime.now().isoformat(),
            "active_tasks": len(self.goal_stack),
        }
        return self.runtime_state

    def retrieve_multi_layer_memory(self, query: str):
        try:
            from friday_tools.core import search_memory
            local_data = search_memory(query)
        except Exception:
            local_data = []
        skill_match = self.skill_cache.get(query.lower())
        return f"Local: {local_data} | Skills: {skill_match}"

    def simulate_action(self, step: Dict):
        risky = ["delete", "shutdown", "format", "rm", "kill", "attack", "exploit"]
        if any(kw in step.get("description", "").lower() for kw in risky):
            return 0.8
        return 0.2

    def add_trace(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {message}"
        self.trace_log.append(entry)
        print(entry)

    def learn_skill(self, task: str, plan: List):
        if self.confidence_score > 0.8:
            self.skill_cache[task.lower()] = plan

    async def rephrase_plan(self, original_task, partial_results, failed_step):
        return [{"action": "retry", "description": f"Alternate path for {failed_step['action']}"}]

    def get_trace(self):
        return "\n".join(self.trace_log)
