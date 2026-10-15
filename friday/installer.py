import os

ENV_VARS = {
    "GOOGLE_API_KEY": "Google AI (Gemini) API Key",
    "GMAIL_USER": "Gmail Address",
    "GMAIL_APP_PASSWORD": "Gmail App Password",
    "MEM0_API_KEY": "Mem0 AI API Key",
    "GITHUB_TOKEN": "GitHub Token",
}

def setup():
    env_path = os.path.join(os.getcwd(), ".env")

    print("\n" + "═"*60)
    print("      🛠️  FRIDAY NEURAL OS - API CONFIGURATION")
    print("═"*60)
    print("Please provide the following credentials. Press Enter to skip/keep current.\n")

    # Load existing values if any
    existing = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        existing[k] = v
        except:
            pass

    lines = []
    for var, description in ENV_VARS.items():
        current = existing.get(var, "")
        display_val = f" [{current[:5]}...{current[-5:]}]" if current else ""
        
        value = input(f" ➤ {description}{display_val}: ").strip()
        
        final_value = value if value else current
        lines.append(f"{var}={final_value}")

    with open(env_path, "w") as f:
        f.write("\n".join(lines))

    print("\n✅ Configuration updated successfully!")
    print("═"*60 + "\n")
