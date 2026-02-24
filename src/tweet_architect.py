#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("/a0/usr/projects/x-manage/data")
DRAFTS_DIR = DATA_DIR / "drafts"
CACHE_DIR = DATA_DIR / "news_cache"

def build_prompt(story):
    return f"""You are @The_AIUpdate. Categorize and draft a tweet for this AI news:

TITLE: {story['title']}
SUMMARY: {story['summary']}
URL: {story['url']}

REQUIRED CATEGORIES:
1. AI in the Workplace and Businesses: Focus on productivity, ROI, enterprise shifts, and B2B tools.
2. AI for Regular People: Focus on practical use for day-to-day life. Target people who CANNOT afford high-end GPUs or thousands of dollars in subscriptions. Explain what they can do, which models to use (free/low-cost), and how it solves their problems.

TASK:
- Identify which category this belongs to.
- Draft an engaging tweet (<280 chars).
- For Category 2: Emphasize accessibility and practical 'daily life' impact.
- Include the URL at the end.
- Format: CATEGORY: [Name] | TWEET: [Text]"""

def prepare_batch():
    latest = CACHE_DIR / "latest_scan.json"
    if not latest.exists(): return
    stories = json.loads(latest.read_text())
    batch = {"generated_at": datetime.now(timezone.utc).isoformat(), "tweets": []}
    for s in stories[:10]:
        batch["tweets"].append({"story": s, "prompt": build_prompt(s), "status": "pending"})
    (DRAFTS_DIR / "latest_batch.json").write_text(json.dumps(batch, indent=2))

if __name__ == "__main__":
    prepare_batch()
