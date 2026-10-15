
import tools
import re

# Read agent.py to parse ALL_TOOLS with utf-8 encoding
with open('agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the content inside ALL_TOOLS = [...]
match = re.search(r'ALL_TOOLS = \[(.*?)\]', content, re.DOTALL)
if match:
    tools_block = match.group(1)
    # Split by comma and clean up
    tool_names = [name.strip() for name in tools_block.split(',') if name.strip() and not name.strip().startswith('#')]
    
    missing_tools = []
    print(f"Checking {len(tool_names)} tools...")
    for name in tool_names:
        if not hasattr(tools, name):
            missing_tools.append(name)
            
    print("Missing tools:", missing_tools)
else:
    print("ALL_TOOLS not found")
