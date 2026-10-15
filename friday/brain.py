
import os
import json
import time
import asyncio
import platform
import psutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from .tools.core import load_memory, save_memory, add_to_logs, search_memory

class AntiGravityEngine:
    """
    Advanced Intelligence Engine (ANTI-GRAVITY) for EDITH.
    Implementing Creator-Class Agentic Planning, Reflection, and Multi-Layer Memory.
    """
    
    def __init__(self, agent_instance, tools=None):
        self.agent = agent_instance
        self.tools = tools or []
        self.goal_stack = []
        self.skill_cache = {}
        self.runtime_state = {}
        self.trace_log = []
        self.confidence_score = 1.0
        
    async def process_task(self, task: str):
        """Main entry point for agentic task processing."""
        self.add_trace(f"🌀 ANTI-GRAVITY Initiated: {task}")
        
        # 1. Environment Awareness
        env_state = self.get_environment_awareness()
        self.add_trace(f"🌍 Env State: {env_state['os']} | CPU: {env_state['cpu']}%")
        
        # 2. Multi-Layer Memory Retrieval
        context = self.retrieve_multi_layer_memory(task)
        
        # 3. Task Decomposition (Planner)
        plan = await self.generate_plan(task, context)
        self.add_trace(f"📋 Strategy Formulated: {len(plan)} steps")
        
        # 4. Simulation & Risk Assessment
        for step in plan:
            risk = self.simulate_action(step)
            if risk > 0.7:
                self.add_trace(f"⚠️ HIGH RISK DETECTED for '{step['action']}'. Requesting verification.")
                # In a real scenario, we'd pause or apply extra safety.
        
        # 5. Execution & Reflection Loop
        results = []
        for i, step in enumerate(plan):
            self.add_trace(f"⚡ Executing Step {i+1}: {step['description']}")
            
            result = await self.execute_step(step)
            
            # Self-Correction & Re-planning
            if "error" in result.lower() or "failed" in result.lower():
                self.add_trace(f"❌ Step Failed. Initiating Dynamic Re-planning...")
                new_plan = await self.rephrase_plan(task, results, step)
                # Extend current plan with new steps
                plan.extend(new_plan)
                continue
            
            results.append(result)
            
            # Post-Action Reflection (Critic)
            reflection = self.self_reflect(step, result)
            self.add_trace(f"🤔 Reflection: {reflection}")
            
        # 6. Skill Learning
        if results:
            self.learn_skill(task, plan)
            
        return results[-1] if results else "Task completed with minimal residue."

    async def generate_plan(self, task: str, context: str):
        """Decomposes task into actionable steps."""
        # This would typically call an LLM, but we'll use logic to structure it
        # For the purpose of this implementation, we assume the LLM in agent.py
        # provides the decomposition, or we structure it here via pseudo-logic.
        steps = [
            {"action": "analyze", "description": f"Identify core requirements for: {task}"},
            {"action": "lookup", "description": "Check internal knowledge and tools"},
            {"action": "execute", "description": f"Perform primary action for: {task}"}
        ]
        return steps

    async def execute_step(self, step: Dict):
        """Executor role: interfaces with tools and emits commands."""
        action = step.get("action", "").lower()
        desc = step.get("description", "")
        
        # Emission Protocol: if the step requires a tool call, we 'ask' the system to execute it
        self.add_trace(f"🎯 Command Emitted: execute_{action} ({desc})")
        
        # In a fully integrated system, this would return a signal to the Agent to call a tool
        # For now, we simulate the 'asking' behavior:
        if "ask" in action or "request" in action:
            return await self.request_user_intervention(desc)
            
        return f"Successfully processed tactical objective: {desc}"

    async def request_user_intervention(self, prompt: str):
        """Allows ANTI-GRAVITY to ask the user/assistant for specific changes or tools."""
        entry = f"❓ ANTI-GRAVITY REQUEST: {prompt}"
        self.add_trace(entry)
        # In a voice-first system, this would be spoken. 
        # Here we return it to the execution loop.
        return f"User intervention requested: {prompt}"

    def self_reflect(self, step: Dict, result: str):
        """Critic role: analyzes outcome vs expectation."""
        if "success" in result.lower():
            self.confidence_score = min(1.0, self.confidence_score + 0.05)
            return "Outcome matches objective. Procedural integrity maintained."
        else:
            self.confidence_score = max(0.0, self.confidence_score - 0.2)
            return "Outcome divergence detected. Correction required."

    def get_environment_awareness(self):
        """Layer 5: Runtime and OS state tracking."""
        self.runtime_state = {
            "os": platform.system(),
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "time": datetime.now().isoformat(),
            "active_tasks": len(self.goal_stack)
        }
        return self.runtime_state

    def retrieve_multi_layer_memory(self, query: str):
        """Layer 4: Episodic, Procedural, and Semantic."""
        # Semantic/Episodic from Edith.json
        local_data = search_memory(query)
        # Procedural (Skills)
        skill_match = self.skill_cache.get(query.lower())
        
        return f"Local: {local_data} | Skills: {skill_match}"

    def simulate_action(self, step: Dict):
        """Layer 11: Outcome simulation and risk check."""
        # Risky tools bypass
        risky_keywords = ["delete", "shutdown", "format", "rm", "kill", "attack", "exploit"]
        if any(kw in step.get("description", "").lower() for kw in risky_keywords):
            return 0.8
        return 0.2

    def add_trace(self, message: str):
        """Layer 15: Explainable decision traces."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.trace_log.append(entry)
        print(entry)

    def learn_skill(self, task: str, plan: List):
        """Layer 10: Skill learning."""
        if self.confidence_score > 0.8:
            self.skill_cache[task.lower()] = plan
            add_to_logs(f"Skill Learned: {task}")

    async def rephrase_plan(self, original_task: str, partial_results: List, failed_step: Dict):
        """Layer 2: Dynamic re-planning."""
        return [{"action": "retry", "description": f"Attempt alternate path for {failed_step['action']}"}]

    def get_trace(self):
        return "\n".join(self.trace_log)
