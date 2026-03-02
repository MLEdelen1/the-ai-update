#!/usr/bin/env python3
import sys
import os
from datetime import datetime
from pathlib import Path
import subprocess

from runtime_paths import project_root, python_executable

PROJECT_ROOT = project_root(Path(__file__))
sys.path.append(str(PROJECT_ROOT))
PYTHON = python_executable()


def run_full_business_cycle():
    now = datetime.now()
    print(f"[{now}] --- THE AI UPDATE: FULL CEO CYCLE START ---")

    print("Phase 1: Scanning Global AI Intelligence...")
    subprocess.run([PYTHON, str(PROJECT_ROOT / "src/news_scanner.py")])

    print("Phase 1.5: Enriching Intelligence with Technical Journalism...")
    subprocess.run([PYTHON, str(PROJECT_ROOT / "src/technical_journalist.py")])

    print("Phase 2: Generating Technical Journalism & Site Update...")
    subprocess.run([PYTHON, str(PROJECT_ROOT / "src/site_generator.py")])

    print("Phase 3: Deploying to Production Repository...")
    os.chdir(PROJECT_ROOT)
    os.system("git add . && git commit -m 'Autonomous: Daily Intelligence Update' && git push origin main")

    print("Phase 4: Executing Stealth Social Distribution...")
    subprocess.run([PYTHON, str(PROJECT_ROOT / "scripts/post_with_cookies.py")])

    print("Phase 5: Engaging with the X Community...")

    print("Phase 6: Auditing Business Growth & Lead Pipeline...")
    subprocess.run([PYTHON, str(PROJECT_ROOT / "src/newsletter_ops.py")])

    print(f"[{datetime.now()}] --- FULL CEO CYCLE COMPLETE ---")


if __name__ == '__main__':
    run_full_business_cycle()
