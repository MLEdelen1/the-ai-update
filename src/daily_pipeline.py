#!/usr/bin/env python3
"""
Daily Orchestrator - Runs the full X-Manage pipeline
Part of X-Manage: The AI Update (@The_AIUpdate)

1. Scan news sources
2. Prepare content batch
3. Signal Agent Zero to generate drafts
4. Queue for posting
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/a0/usr/projects/x-manage/src")

from news_scanner import run_full_scan
from tweet_architect import prepare_daily_batch, get_pending_prompts

DATA_DIR = Path("/a0/usr/projects/x-manage/data")
LOGS_DIR = Path("/a0/usr/projects/x-manage/logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def run_pipeline(num_tweets=5, num_threads=1, max_age_hours=48):
    """Run the full daily content pipeline."""
    log = []
    ts = datetime.now(timezone.utc)

    print("\n" + "#" * 60)
    print("  THE AI UPDATE - Daily Pipeline")
    print(f"  {ts.strftime('%Y-%m-%d %H:%M UTC')}")
    print("#" * 60)

    # Step 1: Scan
    print("\n[STEP 1] Scanning news sources...")
    stories = run_full_scan(max_age_hours=max_age_hours)
    log.append(f"Scanned: {len(stories)} new stories found")

    if not stories:
        print("No new stories found. Exiting.")
        return {"status": "no_news", "log": log}

    # Step 2: Prepare batch
    print(f"\n[STEP 2] Preparing content batch...")
    batch = prepare_daily_batch(num_tweets=num_tweets, num_threads=num_threads)
    log.append(f"Batch: {len(batch['tweets'])} tweets, {len(batch['threads'])} threads")

    # Step 3: Get prompts for Agent Zero
    print(f"\n[STEP 3] Content prompts ready for generation...")
    pending = get_pending_prompts()
    log.append(f"Pending prompts: {len(pending)}")

    # Save run log
    run_log = {
        "timestamp": ts.isoformat(),
        "stories_found": len(stories),
        "tweets_queued": len(batch.get("tweets", [])),
        "threads_queued": len(batch.get("threads", [])),
        "log": log,
    }
    log_file = LOGS_DIR / f"run_{ts.strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(run_log, indent=2))

    print(f"\n[DONE] Pipeline complete.")
    print(f"  Log: {log_file}")
    print(f"  Next: Agent Zero generates drafts from prompts")
    print(f"  Then: Post via browser automation")

    return run_log


def get_status():
    """Get current pipeline status."""
    drafts_dir = DATA_DIR / "drafts"
    cache_dir = DATA_DIR / "news_cache"
    posted_dir = DATA_DIR / "posted"

    latest_batch = drafts_dir / "latest_batch.json"
    latest_scan = cache_dir / "latest_scan.json"

    status = {"scan": None, "batch": None, "posted_today": 0}

    if latest_scan.exists():
        scan = json.loads(latest_scan.read_text())
        status["scan"] = f"{len(scan)} stories in cache"

    if latest_batch.exists():
        batch = json.loads(latest_batch.read_text())
        drafted = sum(1 for t in batch.get("tweets", []) if t["status"] == "drafted")
        pending = sum(1 for t in batch.get("tweets", []) if t["status"] == "pending")
        posted = sum(1 for t in batch.get("tweets", []) if t["status"] == "posted")
        status["batch"] = f"{drafted} drafted, {pending} pending, {posted} posted"

    return status


if __name__ == "__main__":
    run_pipeline()
