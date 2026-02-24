
#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime
from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
sys.path.append(str(PROJECT_ROOT))

def run_full_business_cycle():
    now = datetime.now()
    print(f"[{now}] --- THE AI UPDATE: FULL CEO CYCLE START ---")

    # Phase 1: Intelligence Scan
    print("Phase 1: Scanning Global AI Intelligence...")
    subprocess.run(["python", "/a0/usr/projects/x-manage/src/news_scanner.py"])

    # Phase 1.5: Technical Journalism Enrichment
    print("Phase 1.5: Enriching Intelligence with Technical Journalism...")
    subprocess.run(["python", "/a0/usr/projects/x-manage/src/technical_journalist.py"])

    # Phase 2: Content & Portal Generation
    print("Phase 2: Generating Technical Journalism & Site Update...")
    subprocess.run(["python", "/a0/usr/projects/x-manage/src/site_generator.py"])

    # Phase 3: Production Push (GitHub -> Cloudflare)
    print("Phase 3: Deploying to Production Repository...")
    os.system("cd /a0/usr/projects/x-manage && git add . && git commit -m 'Autonomous: Daily Intelligence Update' && git push origin main")

    # Phase 4: Social Distribution (Posting to X)
    print("Phase 4: Executing Stealth Social Distribution...")
    subprocess.run(["python", "/a0/usr/projects/x-manage/scripts/post_with_cookies.py"])

    # Phase 5: Social Engagement (Replying to Mentions)
    print("Phase 5: Engaging with the X Community...")
    # This is handled by the agent context in the scheduled task

    # Phase 6: Business Intelligence (Newsletter & Growth)
    print("Phase 6: Auditing Business Growth & Lead Pipeline...")
    subprocess.run(["python", "/a0/usr/projects/x-manage/src/newsletter_ops.py"])

    print(f"[{datetime.now()}] --- FULL CEO CYCLE COMPLETE ---")

if __name__ == '__main__':
    run_full_business_cycle()
