#!/usr/bin/env python3
"""
NewsScanner Engine 2.0 - High-Intensity Global AI Intelligence
Categories: LLMs, Reasoning, Video, Music, Avatars, AI Agents
"""
import json
import hashlib
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
import feedparser

DATA_DIR = Path("/a0/usr/projects/x-manage/data")
CACHE_DIR = DATA_DIR / "news_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

RSS_FEEDS = {
    # LLMs & Reasoning
    
    # New Consumer & Startup Sources
    "huggingface": "https://huggingface.co/blog/feed.xml",
    "meta_ai": "https://ai.meta.com/blog/rss/",
    "mistral": "https://mistral.ai/news/index.xml",
    "stability": "https://stability.ai/blog?format=rss",
    "reddit_localllama": "https://www.reddit.com/r/LocalLLaMA/top.rss?t=day",
    "n8n_blog": "https://blog.n8n.io/rss/",
    "venturebeat_ai": "https://venturebeat.com/category/ai/feed/",

    "openai": "https://openai.com/blog/rss.xml",
    "anthropic": "https://www.anthropic.com/rss.xml",
    "google_ai": "https://blog.google/technology/ai/rss/",
    "deepseek": "https://github.com/deepseek-ai/DeepSeek-V3/releases.atom",
    
    # Multi-Modal (Video/Image/Music)
    "runway": "https://runwayml.com/blog/rss.xml",
    "luma": "https://lumalabs.ai/blog/rss.xml",
    "suno_news": "https://techcrunch.com/tag/suno/feed/",
    
    # Industry News
    "verge_ai": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "techcrunch_ai": "https://techcrunch.com/category/artificial-intelligence/feed/",
    
    # YouTube Channels
    "ai_evolution_yt": "https://www.youtube.com/feeds/videos.xml?channel_id=UC5LTm52VaiV-5Q3C-txWVGQ",
    "ai_search_yt": "https://www.youtube.com/feeds/videos.xml?channel_id=UCIgnGlGkVRhd4qNFcEwLL4A",
    "matt_wolfe_yt": "https://www.youtube.com/feeds/videos.xml?channel_id=UC_f-86_T9eLutWpM6I2U92w",
    "agent_zero_yt": "https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7q4hHx690fz8w",
}

def _make_id(text):
    return hashlib.md5(text.encode()).hexdigest()[:12]

def _is_duplicate(story_id):
    seen_file = CACHE_DIR / "seen_ids.json"
    if seen_file.exists():
        try: return story_id in json.loads(seen_file.read_text())
        except: return False
    return False

def _mark_seen(story_ids):
    seen_file = CACHE_DIR / "seen_ids.json"
    seen = json.loads(seen_file.read_text()) if seen_file.exists() else []
    seen.extend(story_ids)
    seen_file.write_text(json.dumps(list(set(seen[-10000:]))))

def _youtube_channel_id_from_feed_url(url: str):
    m = re.search(r"channel_id=([A-Za-z0-9_-]+)", url or "")
    return m.group(1) if m else None

def _youtube_fallback_entries(channel_id: str, max_items: int = 8):
    if not channel_id:
        return []
    channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
    cmd = [
        "python", "-m", "yt_dlp",
        "--flat-playlist", "--playlist-end", str(max_items),
        "--dump-single-json", channel_url,
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        data = json.loads(out)
        entries = data.get("entries", []) or []
    except Exception:
        return []

    parsed = []
    for e in entries:
        vid = e.get("id")
        title = e.get("title") or "No title"
        if not vid:
            continue
        date = e.get("upload_date")
        ts = datetime.now(timezone.utc)
        if date and len(date) == 8:
            ts = datetime.strptime(date, "%Y%m%d").replace(tzinfo=timezone.utc)
        parsed.append({
            "title": title,
            "link": f"https://www.youtube.com/watch?v={vid}",
            "summary": e.get("description") or "",
            "published": ts,
        })
    return parsed

def run_full_scan():
    print("Starting High-Intensity Global Scan...")
    stories = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=7) # Look back 1 week for massive content pull
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            added_from_feed = 0

            for entry in feed.entries[:15]:
                published = None
                for df in ["published_parsed", "updated_parsed"]:
                    if getattr(entry, df, None):
                        published = datetime(*getattr(entry, df)[:6], tzinfo=timezone.utc)
                        break
                if published and published < cutoff:
                    continue

                stories.append({
                    "source": source_name,
                    "title": entry.get("title", "No title"),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:1000], # Larger summaries for better briefing
                    "timestamp": published.isoformat() if published else datetime.now(timezone.utc).isoformat(),
                    "id": _make_id(entry.get("title", "") + entry.get("link", "")),
                })
                added_from_feed += 1

            # YouTube RSS can return empty/404 in some runtime paths. Fallback to yt-dlp.
            if source_name.endswith("_yt") and added_from_feed == 0:
                channel_id = _youtube_channel_id_from_feed_url(feed_url)
                for item in _youtube_fallback_entries(channel_id, max_items=8):
                    published = item.get("published")
                    if published and published < cutoff:
                        continue
                    stories.append({
                        "source": source_name,
                        "title": item.get("title", "No title"),
                        "url": item.get("link", ""),
                        "summary": (item.get("summary") or "")[:1000],
                        "timestamp": published.isoformat() if published else datetime.now(timezone.utc).isoformat(),
                        "id": _make_id((item.get("title") or "") + (item.get("link") or "")),
                    })

        except Exception as e:
            print(f"[WARN] Failed {source_name}: {e}")

    new_stories = [s for s in stories if not _is_duplicate(s['id'])]
    _mark_seen([s['id'] for s in new_stories])
    
    (CACHE_DIR / "latest_scan.json").write_text(json.dumps(new_stories, indent=2))
    print(f"Scan complete. Found {len(new_stories)} new stories across all AI sectors.")
    return new_stories

if __name__ == "__main__":
    run_full_scan()


# Inject new YouTube source
try:
    YOUTUBE_SOURCES.append('Julian Goldie SEO')
except NameError:
    YOUTUBE_SOURCES = ['NetworkChuck', 'AI Search', 'AI Revolution', 'Julian Goldie SEO']
