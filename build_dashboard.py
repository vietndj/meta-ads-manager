import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build():
    print("Exporting JSON...")
    subprocess.run(["python3", str(BASE_DIR / "export_json.py")], check=True)
    print("Dashboard static files are ready in dist/")

if __name__ == "__main__":
    build()
