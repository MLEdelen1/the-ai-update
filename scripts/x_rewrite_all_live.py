#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.topic_filter import is_ai_topic_strict
from src.x_api import XAPIClient

POSTED_FILE = PROJECT_ROOT / "data" / "posted" / "x_posted_articles.json"
REPORT_FILE = PROJECT_ROOT / "data" / "reports" / "x_rewrite_all_latest.json"
HOMEPAGE_URL = "https://theaiupdate.org"

URL_RE = re.compile(r"https?://\\S+")
HASHTAG_RE = re.compile(r"#\\w+")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(s: str) -> str:
    s = unescape(s or "")
    s = TAG_RE.sub(" ", s)
    s = WS_RE.sub(" ", s).strip()
    return s


def _clip(s: str, n: int) -> str:
    s = (s or "").strip()
    if len(s) <= n:
        return s
    return s[: max(0, n - 1)].rstrip(" ,.;:-") + "…"


def _first_sentence(s: str, max_len: int = 110) -> str:
    s = _clean_text(s)
    if not s:
        return ""
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(s) if p.strip()]
    cand = parts[0] if parts else s
    return _clip(cand, max_len)


def _extract_article_id_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        name = Path(p.path).name
        if name.endswith(".html"):
            return name[:-5]
        return name
    except Exception:
        return ""


def _parse_article_html(article_url: str, article_id: str = "") -> dict:
    aid = article_id or _extract_article_id_from_url(article_url)
    if not aid:
        return {}

    candidates = [
        PROJECT_ROOT / "website" / "articles" / f"{aid}.html",
        PROJECT_ROOT / "data" / "articles" / f"{aid}.md",
        PROJECT_ROOT / "data" / "articles" / f"{aid}.markdown",
    ]

    for path in candidates:
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() == ".html":
            title = ""
            subtitle = ""
            m_title = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
            if m_title:
                title = _clean_text(m_title.group(1))

            m_sub = re.search(r'<p[^>]*class=["\']article-sub["\'][^>]*>(.*?)</p>', raw, re.I | re.S)
            if m_sub:
                subtitle = _clean_text(m_sub.group(1))

            m_why = re.search(r"<strong>Why you should care</strong>(.*?)</p>", raw, re.I | re.S)
            if m_why:
                why = _clean_text(m_why.group(1))
                if why and why not in subtitle:
                    subtitle = f"{subtitle} {why}".strip()

            if not subtitle:
                p_tags = re.findall(r"<p[^>]*>(.*?)</p>", raw, flags=re.I | re.S)
                for p in p_tags:
                    txt = _clean_text(p)
                    if txt and len(txt) > 35:
                        subtitle = txt
                        break

            return {"title": title, "summary": subtitle, "source_file": str(path)}

        # markdown fallback
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        title = ""
        summary = ""
        for ln in lines:
            if ln.startswith("#") and not title:
                title = ln.lstrip("# ").strip()
                continue
            if len(ln) > 35:
                summary = ln
                break
        return {"title": title, "summary": summary, "source_file": str(path)}

    return {}


def get_all_user_tweets(client: XAPIClient, user_id: str, max_pages: int = 10) -> list[dict]:
    tweets = []
    seen = set()
    token = None
    backoff = 6
    consecutive_429 = 0

    for _ in range(max_pages):
        url = f"{client.BASE_URL}/users/{user_id}/tweets"
        params = {
            "max_results": "100",
            "exclude": "retweets,replies",
            "tweet.fields": "created_at,text",
        }
        if token:
            params["pagination_token"] = token

        headers = client._get_bearer_headers()
        resp = client.client.get(url, params=params, headers=headers)
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}

        if resp.status_code == 429:
            consecutive_429 += 1
            if consecutive_429 >= 3:
                break
            time.sleep(min(backoff, 45))
            backoff = min(backoff * 2, 45)
            continue

        if resp.status_code != 200:
            raise RuntimeError(f"timeline fetch failed status={resp.status_code} body={data}")

        consecutive_429 = 0
        backoff = 6
        chunk = data.get("data") or []
        for t in chunk:
            tid = str(t.get("id"))
            if tid and tid not in seen:
                seen.add(tid)
                tweets.append(t)

        token = ((data.get("meta") or {}).get("next_token"))
        if not token or not chunk:
            break

    return tweets


def _normalize_line(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def build_rewrite(original_text: str, article_title: str = "", article_summary: str = "", article_url: str = "") -> str:
    original_no_urls = URL_RE.sub("", original_text or "")
    original_no_tags = HASHTAG_RE.sub("", original_no_urls)
    original_no_tags = _clean_text(original_no_tags)

    title = _clean_text(article_title) or _first_sentence(original_no_tags, max_len=78) or "AI update"
    summary = _clean_text(article_summary) or _first_sentence(original_no_tags, max_len=140)

    bits = [b.strip() for b in SENTENCE_SPLIT_RE.split(summary) if b.strip()]
    key_bit = _clip(bits[0] if bits else summary, 78) or "A major shift just landed."

    hook_templates = [
        "{title} just landed — this one is wild.",
        "This AI drop is moving faster than most people realize:",
        "Big shift today: {title}",
        "You can steal an edge from this update tonight:",
        "Most people will scroll past this. Don’t:",
    ]
    why_templates = [
        "Why it hits: {key}",
        "What changed: {key}",
        "The lever: {key}",
        "Fast read: {key}",
    ]
    action_templates = [
        "Move: test one workflow in 20 minutes.",
        "Action: run one A/B test this week.",
        "Next: apply this to your highest-friction task.",
        "Do this now: ship one small experiment.",
    ]
    cta_templates = [
        "Full breakdown:",
        "Read the full article:",
        "Deep dive here:",
        "See the complete breakdown:",
    ]

    seed = abs(hash((title or "") + "|" + (article_url or "")))
    hook = _clip(hook_templates[seed % len(hook_templates)].format(title=title), 92)
    why = _clip(why_templates[seed % len(why_templates)].format(key=key_bit), 92)
    action = _clip(action_templates[seed % len(action_templates)], 70)
    cta = cta_templates[seed % len(cta_templates)]

    article = (article_url or "").strip()
    lines = [hook, why, action, cta, article if article else HOMEPAGE_URL, "#AI #LLM"]

    # Deduplicate near-identical lines
    deduped = []
    seen = set()
    for ln in lines:
        n = _normalize_line(ln)
        if not n or n in seen:
            continue
        seen.add(n)
        deduped.append(ln)

    tweet = "\n".join(deduped).strip()

    if len(tweet) > 280:
        hook = _clip(hook, 72)
        why = _clip(why, 72)
        action = _clip(action, 54)
        deduped = [hook, why, action, article if article else HOMEPAGE_URL, "#AI #LLM"]
        tweet = "\n".join(deduped).strip()

    return tweet[:280]


def call_with_backoff(action, max_seconds: int = 360):
    start = time.time()
    backoff = 15
    last = None
    while (time.time() - start) < max_seconds:
        res = action()
        last = res
        status = None
        if isinstance(res, dict):
            status = res.get("status")
            if status is None:
                status = (((res.get("data") or {}).get("status")))
            if status is None and not res.get("success"):
                err_blob = json.dumps(res, ensure_ascii=False).lower()
                if "rate limit" in err_blob or "too many requests" in err_blob:
                    status = 429
        if status == 429:
            time.sleep(min(backoff, 180))
            backoff = min(backoff * 2, 180)
            continue
        return res
    return last


def load_state() -> dict:
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


def save_state(state: dict) -> None:
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    POSTED_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main(only_ids: set[str] | None = None) -> int:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    client = XAPIClient()
    if not client.is_configured():
        payload = {"ok": False, "error": "X API credentials missing", "generated_at": now_iso()}
        REPORT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2

    me = client.get_me()
    if "data" not in me:
        payload = {"ok": False, "error": "Failed to resolve authenticated user", "me": me, "generated_at": now_iso()}
        REPORT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 3

    user = me["data"]
    tweets = get_all_user_tweets(client, str(user["id"]), max_pages=10)

    state = load_state()
    posted_rows = state.get("posted", [])
    row_by_tweet_id = {str((r or {}).get("tweet_id") or ""): (r or {}) for r in posted_rows}

    scanned = len(tweets)
    rewritten = 0
    deleted = 0
    reposted = 0
    failed = 0

    mappings = []
    failures = []
    deleted_offtopic_ids = []

    for t in tweets:
        old_id = str(t.get("id"))
        if only_ids and old_id not in only_ids:
            continue
        text = (t.get("text") or "").strip()

        in_scope = is_ai_topic_strict(title=text, summary=text, content=text)

        if not in_scope:
            dres = call_with_backoff(lambda: client.delete_tweet(old_id), max_seconds=360)
            if dres and dres.get("success"):
                deleted += 1
                deleted_offtopic_ids.append(old_id)
            else:
                failed += 1
                failures.append({"id": old_id, "stage": "delete_offtopic", "error": dres})
            continue

        row = row_by_tweet_id.get(old_id, {})
        article_url = str((row or {}).get("url") or "")
        article_id = str((row or {}).get("article_id") or "")

        article_meta = _parse_article_html(article_url=article_url, article_id=article_id)
        article_title = (article_meta.get("title") or (row or {}).get("title") or "").strip()
        article_summary = (article_meta.get("summary") or "").strip()

        new_text = build_rewrite(
            text,
            article_title=article_title,
            article_summary=article_summary,
            article_url=article_url,
        )

        dres = call_with_backoff(lambda: client.delete_tweet(old_id), max_seconds=360)
        if not (dres and dres.get("success")):
            failed += 1
            failures.append({"id": old_id, "stage": "delete_ai", "error": dres})
            continue
        deleted += 1

        pres = call_with_backoff(lambda: client.post_tweet(new_text), max_seconds=360)
        if not (pres and pres.get("success")):
            failed += 1
            failures.append({"id": old_id, "stage": "repost_ai", "error": pres, "draft": new_text})
            continue

        new_id = str((((pres.get("data") or {}).get("data") or {}).get("id") or ""))
        rewritten += 1
        reposted += 1
        mappings.append({
            "old_tweet_id": old_id,
            "new_tweet_id": new_id,
            "old_text": text,
            "new_text": new_text,
            "article_title": article_title,
            "article_summary": article_summary,
        })

        for prow in posted_rows:
            if str((prow or {}).get("tweet_id") or "") == old_id:
                prow["tweet_id"] = new_id
                prow["rewritten_at"] = now_iso()

    if deleted_offtopic_ids:
        delete_set = set(deleted_offtopic_ids)
        posted_rows = [r for r in posted_rows if str((r or {}).get("tweet_id") or "") not in delete_set]
        state["posted"] = posted_rows

    save_state(state)

    remaining_ids = [f["id"] for f in failures if f.get("id")]
    retry_cmd = ""
    if remaining_ids:
        retry_cmd = f"python scripts/x_rewrite_all_live.py --only-ids {' '.join(remaining_ids)}"

    payload = {
        "ok": True,
        "user": {"id": str(user.get("id")), "name": user.get("name"), "username": user.get("username")},
        "counts": {
            "scanned": scanned,
            "rewritten": rewritten,
            "deleted": deleted,
            "reposted": reposted,
            "failed": failed,
            "mappings_total": len(mappings),
        },
        "mappings_first_10": mappings[:10],
        "failures": failures,
        "remaining_ids": remaining_ids,
        "retry_command": retry_cmd,
        "generated_at": now_iso(),
    }

    REPORT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "scanned": scanned,
        "rewritten": rewritten,
        "deleted": deleted,
        "reposted": reposted,
        "failed": failed,
        "report": str(REPORT_FILE),
    }, indent=2))

    return 0 if not remaining_ids else 4


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--only-ids", nargs="*", default=[])
    args = parser.parse_args()
    only = set(args.only_ids) if args.only_ids else None
    raise SystemExit(main(only_ids=only))
