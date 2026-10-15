import os
import shutil
import psutil

# ==============================
# FILE SYSTEM
# ==============================
async def create_file(path: str, content: str = "") -> str:
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File created: {path}"
    except Exception as e:
        return f"Failed to create file: {e}"

async def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content[:500] + ("..." if len(content) > 500 else "")
    except Exception as e:
        return f"Failed to read file: {e}"

async def delete_file(path: str) -> str:
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"File deleted: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Folder deleted: {path}"
        else:
            return "Path not found"
    except Exception as e:
        return f"Delete failed: {e}"

async def rename_file(old_path: str, new_path: str) -> str:
    try:
        os.rename(old_path, new_path)
        return f"Renamed: {old_path} -> {new_path}"
    except Exception as e:
        return f"Rename failed: {e}"

async def list_directory(path: str = ".") -> str:
    try:
        items = os.listdir(path)
        if len(items) > 50:
            return f"Found {len(items)} items. First 50: " + ", ".join(items[:50])
        return ", ".join(items)
    except Exception as e:
        return f"Failed to list directory: {e}"

async def create_folder(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return f"Failed to create folder: {e}"

async def create_project_files(base_path: str, files: str) -> str:
    """
    Creates multiple files in a directory. useful for saving generated code projects.
    Args:
        base_path: The root directory for the project.
        files: A JSON string dictionary where keys are relative file paths and values are file content.
               Example: '{"index.html": "<html>...</html>", "css/style.css": "body { ... }"}'
    """
    import json
    import os

    try:
        file_dict = json.loads(files)
        results = []
        
        # Ensure base path exists
        os.makedirs(base_path, exist_ok=True)

        for rel_path, content in file_dict.items():
            full_path = os.path.join(base_path, rel_path)
            
            # Ensure subdirectories exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            results.append(f"Created: {rel_path}")

        return f"✅ Project files created at {base_path}:\n" + "\n".join(results)

    except json.JSONDecodeError:
        return "❌ Error: 'files' argument must be a valid JSON string."
    except Exception as e:
        return f"❌ Failed to create project files: {e}"

async def disk_usage(path: str = "C:\\") -> str:
    try:
        usage = psutil.disk_usage(path)
        total_gb = usage.total / (1024**3)
        free_gb = usage.free / (1024**3)
        return f"{path} - Total: {total_gb:.1f}GB | Free: {free_gb:.1f}GB ({usage.percent}% used)"
    except Exception as e:
        return f"Failed to get disk usage: {e}"


def _resolve_smart_path(file_path: str):
    from pathlib import Path
    if not file_path:
        return None
    p = Path(file_path)
    if p.exists():
        return p
    name = p.name
    home = Path.home()
    search_dirs = [
        home / "OneDrive" / "Pictures" / "Camera Roll",
        home / "Pictures" / "Camera Roll",
        home / "Pictures",
        home / "OneDrive" / "Pictures",
        home / "Downloads",
        home / "Desktop",
        home / "Documents",
        home / "Documents" / "ULTRON_Data",
    ]
    for d in search_dirs:
        if d.exists():
            cand = d / name
            if cand.exists():
                return cand
    for d in search_dirs[:3]:
        if d.exists():
            matches = list(d.glob(f"*{name}*"))
            if matches:
                return matches[0]
    return None


async def analyze_file(file_path: str, instruction: str = "") -> str:
    """
    Analyzes any file (Image, PDF, Code, JSON, CSV, Document, Text) using Gemini multi-modal AI.
    """
    def _execute():
        from pathlib import Path
        p = _resolve_smart_path(file_path)
        if not p or not p.exists():
            return f"[ERROR] File '{file_path}' does not exist."
        
        ext = p.suffix.lower()
        inst = instruction.strip() or "Provide an exhaustive breakdown, key takeaways, and answer any questions."
        
        import os
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "[ERROR] GEMINI_API_KEY missing."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        if ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']:
            from PIL import Image
            img = Image.open(str(p))
            resp = model.generate_content([f"Analyze this image: {inst}", img])
            return resp.text.strip() if resp and resp.text else "Image analyzed."
            
        elif ext == '.pdf':
            try:
                import fitz
                doc = fitz.open(str(p))
                txt = "\n".join([f"--- Page {i+1} ---\n" + doc[i].get_text() for i in range(min(len(doc), 50))])
                doc.close()
            except Exception:
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(p))
                    txt = "\n".join([page.extract_text() or "" for page in reader.pages[:50]])
                except Exception as err:
                    txt = f"[Could not extract PDF text: {err}]"
            resp = model.generate_content(f"Analyze this PDF document '{p.name}': {inst}\n\nContent:\n{txt[:60000]}")
            return resp.text.strip() if resp and resp.text else "PDF analyzed."
            
        else:
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"[Binary data: {p.stat().st_size} bytes]"
            resp = model.generate_content(f"Analyze file '{p.name}': {inst}\n\nContent:\n{content[:60000]}")
            return resp.text.strip() if resp and resp.text else "File analyzed."

    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute)

