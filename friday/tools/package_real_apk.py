"""
ULTRON Satellite Real-Device APK Packager
Injects ULTRON Mobile Assets & Cyberpunk HUD into verified Android WebView APK container,
re-signs with RSA-2048, and deploys to Downloads and Data directory.
"""

import os
import shutil
import zipfile
import subprocess
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
DOWNLOADS_DIR = Path.home() / "Downloads"

JDK_BIN = Path(r"C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot\bin")
KEYTOOL = JDK_BIN / "keytool.exe"
JARSIGNER = JDK_BIN / "jarsigner.exe"

BASE_APK = DATA_DIR / "base_valid.apk"
OUTPUT_APK_DATA = DATA_DIR / "ULTRON_Satellite.apk"
OUTPUT_APK_DOWNLOADS = DOWNLOADS_DIR / "ULTRON_Satellite.apk"

def package_ultron_apk():
    print("[1/4] Preparing ULTRON Satellite APK build workspace...")
    build_dir = DATA_DIR / "apk_real_build"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    build_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_dir = build_dir / "unpacked"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Unzip base APK
    with zipfile.ZipFile(BASE_APK, 'r') as zin:
        zin.extractall(extracted_dir)
        
    # 2. Remove old signatures
    meta_inf = extracted_dir / "META-INF"
    if meta_inf.exists():
        for item in meta_inf.iterdir():
            if item.suffix in [".RSA", ".SF", ".MF", ".DSA", ".EC"]:
                try:
                    item.unlink()
                except Exception:
                    pass

    # 3. Read our Cyberpunk Mobile HUD UI
    html_src = Path.home() / ".gemini" / "antigravity" / "brain" / "fbd594d0-e2ba-4f8a-98c6-03687bf1f910" / "ultron_mobile_apk_ui.html"
    with open(html_src, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 4. Place UI in assets
    assets_dir = extracted_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    with open(assets_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(assets_dir / "ultron.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(assets_dir / "homepage.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("[2/4] Assembling unsigned APK container...")
    unsigned_apk = build_dir / "unsigned.apk"
    with zipfile.ZipFile(unsigned_apk, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(extracted_dir)
                zout.write(full_path, str(rel_path).replace("\\", "/"))
                
    print("[3/4] Generating RSA-2048 Debug Keystore and Signing APK...")
    keystore_path = DATA_DIR / "ultron_debug.keystore"
    if not keystore_path.exists():
        cmd = [
            str(KEYTOOL if KEYTOOL.exists() else "keytool"),
            "-genkeypair",
            "-v",
            "-keystore", str(keystore_path),
            "-alias", "ultron_key",
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-storepass", "ultron123",
            "-keypass", "ultron123",
            "-dname", "CN=ULTRON Satellite, OU=AI, O=Friday, L=London, ST=UK, C=GB"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
    signed_apk = build_dir / "ULTRON_Satellite.apk"
    sign_cmd = [
        str(JARSIGNER if JARSIGNER.exists() else "jarsigner"),
        "-keystore", str(keystore_path),
        "-storepass", "ultron123",
        "-keypass", "ultron123",
        "-sigalg", "SHA256withRSA",
        "-digestalg", "SHA-256",
        "-signedjar", str(signed_apk),
        str(unsigned_apk),
        "ultron_key"
    ]
    res = subprocess.run(sign_cmd, capture_output=True, text=True)
    
    print("[4/4] Deploying to Downloads & ULTRON Data...")
    shutil.copy2(signed_apk, OUTPUT_APK_DATA)
    shutil.copy2(signed_apk, OUTPUT_APK_DOWNLOADS)
    
    size_mb = OUTPUT_APK_DOWNLOADS.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Real Android APK created and signed ({size_mb:.2f} MB)")
    print(f"[PATH 1] {OUTPUT_APK_DOWNLOADS}")
    print(f"[PATH 2] {OUTPUT_APK_DATA}")

if __name__ == "__main__":
    package_ultron_apk()
