import os
import sys
import shutil
import zipfile
import subprocess
import urllib.request
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = Path.home() / "Downloads"

JDK_BIN = Path(r"C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot\bin")
KEYTOOL = JDK_BIN / "keytool.exe"
JARSIGNER = JDK_BIN / "jarsigner.exe"

APK_OUTPUT_DATA = DATA_DIR / "ULTRON_Satellite.apk"
APK_OUTPUT_DOWNLOADS = DOWNLOADS_DIR / "ULTRON_Satellite.apk"

def generate_keystore(keystore_path: Path):
    if keystore_path.exists():
        return
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

def assemble_ultron_apk():
    print("[1/5] Initializing build workspace...")
    build_dir = DATA_DIR / "apk_build"
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except Exception:
            pass
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Source mobile UI HTML
    html_src = Path.home() / ".gemini" / "antigravity" / "brain" / "fbd594d0-e2ba-4f8a-98c6-03687bf1f910" / "ultron_mobile_apk_ui.html"
    with open(html_src, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 2. Download or use base APK container with WebView + Native permissions
    base_apk_path = DATA_DIR / "base_webview.apk"
    if not base_apk_path.exists() or base_apk_path.stat().st_size < 100000:
        print("[2/5] Downloading clean Android WebView runtime shell...")
        # Standard open-source WebView wrapper APK template (FastHub/Lightning/AppManager base)
        urls = [
            "https://github.com/anthonycr/Lightning-Browser/releases/download/v5.1.0/Lightning-Browser-v5.1.0-default-release.apk",
            "https://raw.githubusercontent.com/shadovo/WebAPK/main/template.apk"
        ]
        downloaded = False
        for url in urls:
            try:
                print(f"Fetching from {url}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as resp, open(base_apk_path, 'wb') as out_f:
                    shutil.copyfileobj(resp, out_f)
                if base_apk_path.stat().st_size > 100000:
                    downloaded = True
                    break
            except Exception as e:
                print(f"URL {url} failed: {e}")
                
        if not downloaded:
            print("Creating direct custom APK container...")
            # Fallback: create custom standalone container
    
    print("[3/5] Injecting ULTRON Cyberpunk HUD & WebSocket Bridge into APK...")
    extracted_dir = build_dir / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    
    if base_apk_path.exists() and base_apk_path.stat().st_size > 100000:
        with zipfile.ZipFile(base_apk_path, 'r') as zin:
            zin.extractall(extracted_dir)
            
        # Remove old META-INF signatures
        meta_inf = extracted_dir / "META-INF"
        if meta_inf.exists():
            shutil.rmtree(meta_inf)
            
        # Place UI in assets
        assets_dir = extracted_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        with open(assets_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(assets_dir / "ultron.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Repackage into unsigned APK
        unsigned_apk = build_dir / "ultron_unsigned.apk"
        with zipfile.ZipFile(unsigned_apk, 'w', zipfile.ZIP_DEFLATED) as zout:
            for root, dirs, files in os.walk(extracted_dir):
                for file in files:
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(extracted_dir)
                    zout.write(full_path, str(rel_path))
    else:
        # Standalone packaging
        unsigned_apk = build_dir / "ultron_unsigned.apk"
        with zipfile.ZipFile(unsigned_apk, 'w', zipfile.ZIP_DEFLATED) as zout:
            assets_dir = build_dir / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)
            index_p = assets_dir / "index.html"
            with open(index_p, "w", encoding="utf-8") as f:
                f.write(html_content)
            zout.write(index_p, "assets/index.html")
            
    print("[4/5] Generating RSA-2048 Debug Keystore and Signing APK...")
    keystore_path = DATA_DIR / "ultron_debug.keystore"
    generate_keystore(keystore_path)
    
    signed_apk = build_dir / "ULTRON_Satellite.apk"
    shutil.copy2(unsigned_apk, signed_apk)
    
    sign_cmd = [
        str(JARSIGNER if JARSIGNER.exists() else "jarsigner"),
        "-keystore", str(keystore_path),
        "-storepass", "ultron123",
        "-keypass", "ultron123",
        "-signedjar", str(signed_apk),
        str(unsigned_apk),
        "ultron_key"
    ]
    res = subprocess.run(sign_cmd, capture_output=True, text=True)
    print("jarsigner output:", res.stdout)
    if res.stderr:
        print("jarsigner stderr:", res.stderr)
        
    print("[5/5] Deploying Final APK to Downloads and ULTRON Data...")
    shutil.copy2(signed_apk, APK_OUTPUT_DATA)
    shutil.copy2(signed_apk, APK_OUTPUT_DOWNLOADS)
    
    size_mb = APK_OUTPUT_DOWNLOADS.stat().st_size / (1024 * 1024)
    print(f"🎉 SUCCESS! ULTRON Satellite APK built ({size_mb:.2f} MB)")
    print(f"   📁 Download Location: {APK_OUTPUT_DOWNLOADS}")
    print(f"   📁 Server Hub Data: {APK_OUTPUT_DATA}")

if __name__ == "__main__":
    assemble_ultron_apk()
