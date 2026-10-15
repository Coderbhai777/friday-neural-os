import subprocess
import sys

def install(package):
    print(f"--------------------------------------------------")
    print(f"[INSTALLING]: {package}")
    print(f"--------------------------------------------------")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[SUCCESS] Installed {package}")
    except subprocess.CalledProcessError:
        print(f"[FAILURE] Failed to install {package}")
    except Exception as e:
        print(f"[ERROR] Error installing {package}: {e}")

def main():
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
            
        packages = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        
        print(f"Found {len(packages)} packages to install.")
        
        for package in packages:
            install(package)
            
        print("\nAll installation attempts completed.")
        
    except FileNotFoundError:
        print("requirements.txt not found.")

if __name__ == "__main__":
    main()
