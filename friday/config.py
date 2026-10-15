import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED = [
    "GOOGLE_API_KEY",
    "GMAIL_USER",
    "GMAIL_APP_PASSWORD",
    "MEM0_API_KEY",
    "GITHUB_TOKEN",
]

def validate_env():
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            "Friday is not fully configured.\n"
            "Run: friday config setup\n\nMissing:\n"
            + "\n".join(missing)
        )
