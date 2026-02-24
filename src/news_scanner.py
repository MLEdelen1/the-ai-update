#!/usr/bin/env python3
"""
NewsScanner Engine - Scans AI news, GitHub, and YouTube
Part of X-Manage: The AI Update (@The_AIUpdate)
"""
import json
import os
import hashlib
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import httpx
import feedparser
from bs4 import BeautifulSoup

DATA_DIR = Path("/a0/usr/projects/x-manage/data")
CACHE_DIR = DATA_DIR / "news_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

RSS_FEEDS = {
    "openai_blog": "https://openai.com/blog/rss.xml",
    "anthropic_blog": "https://www.anthropic.com/rss.xml",
    "google_ai_blog": "https://blog.google/technology/ai/rss/",
    "verge_ai": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "techcrunch_ai": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "ai_search_yt": "https://www.youtube.com/feeds/videos.xml?channel_id=UCIgnGlGkVRhd4qNFcEwLL4A",
    "matt_wolfe_yt": "https://www.youtube.com/feeds/videos.xml?channel_id=UC_f-86_T9eLutWpM6I2U92w",
    "two_minute_papers": "https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7q4hHx690fz8w",
}

def _make_id(text):
    return hashlib.md5(text.encode()).hexdigest()[:12]

def _is_duplicate(story_id):
    seen_file = CACHE_DIR / "seen_ids.json"
    if seen_file.exists():
        try:
            return story_id in json.loads(seen_file.read_text())
        except:
            return False
    return False

def _mark_seen(story_ids):
    seen_file = CACHE_DIR / "seen_ids.json"
    seen = json.loads(seen_file.read_text()) if seen_file.exists() else []
    seen.extend(story_ids)
    seen_file.write_text(json.dumps(seen[-5000:]))

def scan_rss_feeds(max_age_hours=48):
    stories = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                published = None
                for df in ["published_parsed", "updated_parsed"]:
                    if getattr(entry, df, None):
                        published = datetime(*getattr(entry, df)[:6], tzinfo=timezone.utc)
                        break
                if published and published < cutoff: continue
                stories.append({
                    "source": source_name,
                    "title": entry.get("title", "No title"),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "timestamp": published.isoformat() if published else datetime.now(timezone.utc).isoformat(),
                    "id": _make_id(entry.get("title", "") + entry.get("link", "")),
                })
        except Exception as e: print(f"[WARN] Failed {source_name}: {e}")
    return stories

def run_full_scan():
    print("Starting Full Scan...")
    stories = scan_rss_feeds()
    new_stories = [s for s in stories if not _is_duplicate(s['id'])]
    _mark_seen([s['id'] for s in new_stories])
    latest_file = CACHE_DIR / "latest_scan.json"
    latest_file.write_text(json.dumps(new_stories, indent=2))
    print(f"Scan complete. Found {len(new_stories)} new stories.")
    return new_stories

if __name__ == "__main__":
    run_full_scan()
