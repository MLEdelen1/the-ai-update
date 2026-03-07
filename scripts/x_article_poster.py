#!/usr/bin/env python3
"""Post article links to X with idempotent URL dedupe.

Modes:
- post-new: post only articles newer than --since (epoch seconds)
- backfill: post recent unposted articles
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.x_api import XAPIClient
from src.topic_filter import is_ai_topic_strict

DATA_POSTED_DIR = PROJECT_ROOT / "data" / "posted"
POSTED_FILE = DATA_POSTED_DIR / "x_posted_articles.json"
ARTICLES_DIR = PROJECT_ROOT / "data" / "research" / "briefings_2026_02"
BASE_URL = "https://theaiupdate.org/articles"

HOOKS = [
    "just dropped and people are already moving on it.",
    "changed the game again.",
    "is a real signal, not noise.",
    "is worth your attention today.",
    "has practical impact right now.",
]

BODIES = [
    "What changed, why it matters, and the one move to test first.",
    "If you build with AI, this is the one you should not skip.",
    "Short breakdown, clear takeaway, and next step inside.",
    "This can save time fast if you use it the right way.",
    "Most people will miss this angle. You do not have to.",
]

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> Dict:
    if not POSTED_FILE.exists():
        return {"version": 1, "posted": []}
    try:
        payload = json.loads(POSTED_FILE.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {"version": 1, "posted": []}
        payload.setdefault("version", 1)
        payload.setdefault("posted", [])
        return payload
    except Exception:
        return {"version": 1, "posted": []}


def _save_state(state: Dict) -> None:
    DATA_POSTED_DIR.mkdir(parents=True, exist_ok=True)
    POSTED_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _posted_urls(state: Dict) -> set:
    out = set()
    for row in state.get("posted", []):
        url = (row or {}).get("url")
        if isinstance(url, str) and url:
            out.add(url)
    return out


def _extract_title(md_path: Path) -> str:
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return md_path.stem.replace("briefing_", "").replace("_", " ").strip().title()

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return html.unescape(html.unescape(s[2:].strip()))

    source_match = re.search(r"Source:\s*\[([^\]]+)\]\(", text, flags=re.IGNORECASE)
    if source_match:
        return html.unescape(html.unescape(source_match.group(1).strip()))

    any_link_match = re.search(r"\[([^\]]+)\]\(https?://[^\)]+\)", text, flags=re.IGNORECASE)
    if any_link_match:
        return html.unescape(html.unescape(any_link_match.group(1).strip()))

    return md_path.stem.replace("briefing_", "").replace("_", " ").strip().title()


def _clean_text(s: str) -> str:
    s = html.unescape(html.unescape(s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _build_tweet(title: str, url: str, idx: int) -> str:
    title = _clean_text(title)
    hook = HOOKS[idx % len(HOOKS)]

    lead = f"{title} {hook}"
    body = BODIES[idx % len(BODIES)]
    cta = f"Read + grab the free AI Toolkit: {url}"

    tweet = f"{lead}\n\n{body}\n\n{cta}"
    if len(tweet) <= 280:
        return tweet

    max_lead = max(40, 280 - len(body) - len(cta) - 4)
    if len(lead) > max_lead:
        lead = lead[: max_lead - 1].rstrip() + "…"

    tweet = f"{lead}\n\n{body}\n\n{cta}"
    if len(tweet) <= 280:
        return tweet

    compact_body = BODIES[idx % len(BODIES)]
    tweet = f"{lead}\n\n{compact_body}\n\n{cta}"
    return tweet[:280]


def _list_articles() -> List[Tuple[Path, float]]:
    if not ARTICLES_DIR.exists():
        return []
    rows = []
    for p in ARTICLES_DIR.glob("briefing_*.md"):
        try:
            mtime = p.stat().st_mtime
        except Exception:
            mtime = 0.0
        rows.append((p, mtime))
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows


def _article_id_from_path(p: Path) -> str:
    return p.stem.replace("briefing_", "")


def _article_url(article_id: str) -> str:
    return f"{BASE_URL}/{article_id}.html"


def _pick_candidates(mode: str, since: float, limit: int, state: Dict) -> List[Dict]:
    posted = _posted_urls(state)
    candidates = []

    for p, mtime in _list_articles():
        if mode == "post-new" and since and mtime < since:
            continue

        aid = _article_id_from_path(p)
        url = _article_url(aid)
        if url in posted:
            continue

        title = _extract_title(p)
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        if not is_ai_topic_strict(title=title, content=content):
            continue

        candidates.append({
            "id": aid,
            "url": url,
            "title": title,
            "path": str(p),
            "mtime": mtime,
        })

    return candidates[: max(0, limit)]


def post_articles(mode: str, limit: int, since: float, sleep_seconds: float) -> Dict:
    client = XAPIClient()
    if not client.is_configured():
        return {
            "ok": False,
            "error": "X API credentials missing or incomplete",
            "attempted": 0,
            "succeeded": 0,
            "failed": 0,
            "results": [],
        }

    state = _load_state()
    to_post = _pick_candidates(mode=mode, since=since, limit=limit, state=state)

    attempted = 0
    succeeded = 0
    failed = 0
    results = []

    for idx, art in enumerate(to_post):
        attempted += 1
        tweet = _build_tweet(art["title"], art["url"], idx)

        try:
            res = client.post_tweet(tweet)
        except Exception as exc:
            res = {"success": False, "status": None, "error": f"exception: {exc}"}

        if res.get("success"):
            succeeded += 1
            tweet_id = (((res.get("data") or {}).get("data") or {}).get("id"))
            state["posted"].append({
                "article_id": art["id"],
                "url": art["url"],
                "title": art["title"],
                "tweet_id": tweet_id,
                "posted_at": _now_iso(),
                "mode": mode,
            })
            _save_state(state)
            results.append({"article_id": art["id"], "url": art["url"], "success": True, "tweet_id": tweet_id})
        else:
            failed += 1
            results.append({
                "article_id": art["id"],
                "url": art["url"],
                "success": False,
                "status": res.get("status"),
                "error": res.get("error"),
            })

        if sleep_seconds > 0 and idx < len(to_post) - 1:
            time.sleep(sleep_seconds)

    return {
        "ok": True,
        "mode": mode,
        "attempted": attempted,
        "succeeded": succeeded,
        "failed": failed,
        "results": results,
        "state_file": str(POSTED_FILE),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Post article links to X with URL dedupe state")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("post-new", help="Post newly generated articles since --since")
    p_new.add_argument("--since", type=float, default=0.0, help="Epoch seconds cutoff from pipeline start")
    p_new.add_argument("--limit", type=int, default=8)
    p_new.add_argument("--sleep", type=float, default=1.5)

    p_backfill = sub.add_parser("backfill", help="Post recent unposted backlog articles")
    p_backfill.add_argument("--limit", type=int, default=15)
    p_backfill.add_argument("--sleep", type=float, default=2.0)

    args = parser.parse_args()

    if args.cmd == "post-new":
        out = post_articles(mode="post-new", limit=args.limit, since=args.since, sleep_seconds=args.sleep)
    else:
        out = post_articles(mode="backfill", limit=args.limit, since=0.0, sleep_seconds=args.sleep)

    print(json.dumps(out, indent=2))
    if not out.get("ok"):
        return 1
    return 0 if out.get("failed", 0) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())


