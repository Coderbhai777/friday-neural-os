"""
ULTRON Full-Stack Project Architect & Auto-Deployer
Scaffolds complete, production-ready React/Vite/Tailwind and FastAPI/Python applications in seconds and launches them locally.
"""

import os
import sys
import time
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from friday_tools.sound_engine import play_sound_async

_PROJECTS_DIR = Path.home() / "Projects"
_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


async def generate_fullstack_project(project_name: str, description: str, template: str = "fastapi-react") -> str:
    """
    Generates a full-stack production application (Frontend + Backend + Config + README) from a description and launches it.
    
    Args:
        project_name: Name of the project directory (e.g. 'cyber_dashboard', 'ai_resume_builder').
        description: Comprehensive description of the features, UI, and data models required.
        template: 'fastapi-react', 'python-cli', 'html5-app'
    """
    play_sound_async("scan")
    target_dir = _PROJECTS_DIR / project_name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        
        prompt = (
            f"You are ULTRON's Senior Full-Stack Architect. Scaffold a complete project named '{project_name}'.\n"
            f"Description: {description}\n"
            f"Template: {template}\n"
            f"Return a JSON object with this exact schema:\n"
            f'{{"files": {{"filename.ext": "full code content...", "backend/main.py": "code...", "README.md": "..."}}}}\n'
            f"Write complete, production-ready, beautiful code. Include FastAPI backend and sleek HTML/Tailwind or React frontend."
        )
        
        model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        
        data = json.loads(response.text)
        files = data.get("files", {})
        
        created = []
        for rel_path, content in files.items():
            full_path = target_dir / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            created.append(rel_path)
            
        play_sound_async("chime")
        return (
            f"🚀 [PROJECT ARCHITECT COMPLETE]\n"
            f"• Project: {project_name}\n"
            f"• Location: {target_dir}\n"
            f"• Files Generated ({len(created)}):\n" + "\n".join(f"   - {f}" for f in created[:10]) +
            f"\n\nSir, the codebase is ready at: file:///{str(target_dir).replace('\\', '/')}"
        )
    except Exception as e:
        return f"[FAIL] Project generation error: {e}"


async def list_user_projects() -> str:
    """Lists all projects generated in the user's Projects directory."""
    if not _PROJECTS_DIR.exists():
        return "[INFO] Projects directory is empty."
    dirs = [d.name for d in _PROJECTS_DIR.iterdir() if d.is_dir()]
    if not dirs:
        return "[INFO] No projects found in ~/Projects."
    return f"[PROJECTS] Available Codebases in {_PROJECTS_DIR}:\n" + "\n".join(f"  • {d}" for d in dirs)
