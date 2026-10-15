from setuptools import setup, find_packages

setup(
    name="friday-neural-os",
    version="1.8.0",
    description="EDITH Neural OS: Advanced AI Agent with OS automation, security suite, and smart memory.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "mem0ai",
        "duckduckgo-search",
        "langchain_community",
        "requests",
        "python-dotenv",
        "scapy",
        "pyautogui",
        "psutil",
        "pyperclip",
        "pywin32",
        "pywebostv",
        "pillow",
        "google-genai",
        "screen-brightness-control",
        "win10toast",
        "opencv-python",
        "truecallerpy",
        "phonenumbers",
        "opencage",
        "folium"
    ],
    entry_points={
        'console_scripts': [
            'friday=friday.cli:main',
        ],
    },
    python_requires='>=3.8',
)
