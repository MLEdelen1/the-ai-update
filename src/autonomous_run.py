#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime
from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
sys.path.append(str(PROJECT_ROOT))

from src.news_scanner import run_full_scan
from src.tweet_architect import prepare_batch
from src.site_generator import generate_site

def run_pipeline():
    now = datetime.now()
    hour = now.hour
    print(f"[{now}] --- THE AI UPDATE: AUTONOMOUS CEO CYCLE START ---")
    
    # Phase 1: Intelligence Gathering
    print("Phase 1: Scanning Intelligence Sources...")
    run_full_scan()
    
    # Phase 2: Authority & Content Strategy
    print("Phase 2: Building Authority & Content Strategy...")
    prepare_batch()
    if 7 <= hour < 10: subprocess.run(["python", "/a0/usr/projects/x-manage/src/authority_builder.py"])
    
    # Phase 3: Autonomous Posting (The Execution Loop)
    print("Phase 3: Pushing Live to X...")
    # This script uses the cookies to post the latest drafted tweet
    subprocess.run(["python", "/a0/usr/projects/x-manage/scripts/post_with_cookies.py"])

    # Phase 4: Asset Building & Site Updates
    print("Phase 4: Updating Intelligence Portal (Website)...")
    generate_site()
    
    # Phase 5: Business Operations & Innovation
    # Generate a Video Script for the daily news
    print("Phase 5: Generating Video Spokesperson Scripts...")
    subprocess.run(["python", "/a0/usr/projects/x-manage/src/video_script_engine.py"])

    # Phase 6: Business Health Monitoring
    print("Phase 6: Updating Business Dashboard...")
    subprocess.run(["python", "/a0/usr/projects/x-manage/src/business_dashboard.py"])

    print(f"[{datetime.now()}] --- CEO CYCLE COMPLETE ---")

if __name__ == "__main__":
    run_pipeline()
