#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.runtime_paths import python_executable
from src.topic_filter import is_ai_topic_strict
from src.x_api import XAPIClient

BRIEF_DIR = PROJECT_ROOT / "data" / "research" / "briefings_2026_02"
WEB_ARTICLES_DIR = PROJECT_ROOT / "website" / "articles"
ARTICLES_HTML = PROJECT_ROOT / "website" / "articles.html"
ARCHIVE_HTML = PROJECT_ROOT / "website" / "archive.html"
POSTED_FILE = PROJECT_ROOT / "data" / "posted" / "x_posted_articles.json"
REPORT_FILE = PROJECT_ROOT / "data" / "reports" / "topic_audit_latest.json"
VERIFY_ID = "d292ba3ac0bc"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def md_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return fallback


def html_text_title(html: str, fallback: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    if not m:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if m:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip() or fallback
    return fallback


def strip_html(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or ""))


def find_article_links(html_text: str) -> set[str]:
    ids = set(re.findall(r"href=\"(?:\.?/?)*articles/([^\"#?]+)\.html\"", html_text, flags=re.I))
    ids.update(re.findall(r"href=\"/(?:articles)/([^\"#?]+)\.html\"", html_text, flags=re.I))
    return ids


def render_articles_html(items: list[dict]) -> str:
    cards = []
    for it in items:
        aid = it["id"]
        title = it["title"]
        date = it["date"]
        cards.append(
            f'<article class="tool"><div class="tool-cat">AI</div><h3>{title}</h3><div class="card-date">{date}</div>'
            f'<a class="tool-link" href="articles/{aid}.html">Read full article &rarr;</a></article>'
        )
    cards_html = "".join(cards)
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
        '<title>Articles | The AI Update</title><link href="./styles.css?v=14" rel="stylesheet"/></head><body>'
        '<canvas id="particles"></canvas><div class="top-glow"></div><nav id="nav"><div class="nav-wrap"><a class="logo-group" href="./index.html">'
        '<img alt="" class="logo-img" src="./assets/logo.png"/><div class="logo-text">THE AI<span class="logo-accent">UPDATE</span></div></a>'
        '<div class="nav-links" id="navLinks"><a href="./intel.html">Latest Intel</a><a href="./workflows.html">Workflows</a><a href="./tools.html">Tools</a>'
        '<a href="./guides/index.html">Guides</a><a href="./articles.html">Articles</a><a href="./resources.html">Resources</a><a class="nav-btn" href="./starter-kit.html">Get Free Kit</a></div>'
        '<button class="burger" onclick="document.getElementById(\'navLinks\').classList.toggle(\'show\')"><span></span><span></span><span></span></button></div></nav>'
        '<main class="articles-index"><div class="sect-head"><p class="tag">ARTICLES</p><h1>AI-only published articles</h1>'
        '<p class="sect-sub">Filtered to LLMs, reasoning models, generation models, and AI tools/platform updates.</p></div>'
        '<section class="sect" style="padding-top:12px; padding-bottom:28px;"><div class="sect-head"><p class="tag">AI TOPICS</p><h2>Current AI archive</h2></div>'
        f'<section class="articles-grid">{cards_html}</section></section><p class="article-cta"><a class="btn-main" href="guides/index.html">Start with the beginner roadmap</a></p></main>'
        '<footer><div class="contain foot-inner"><div class="foot-brand"><img alt="" class="foot-logo" src="./assets/logo.png"/><span>THE AI UPDATE</span></div>'
        '<div class="foot-links"><a href="./index.html">Home</a><a href="./guides/index.html">Guides</a><a href="./articles.html">Articles</a><a href="./tools.html">Tools</a><a href="./resources.html">Resources</a><a href="./starter-kit.html">Starter Kit</a></div>'
        '</div></footer><script src="./site.js?v=14"></script></body></html>'
    )


def render_archive_html(items: list[dict]) -> str:
    cards = []
    for it in items:
        cards.append(
            f'<a href="articles/{it["id"]}.html" class="analysis-card" style="display:block; margin:0 0 16px 0;">'
            f'<div class="analysis-meta">INTEL &bull; ARCHIVE</div><h3>{it["title"]}</h3><p>{it["date"]}</p></a>'
        )
    cards_html = "".join(cards)
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
        '<title>Archive | The AI Update</title><link href="./styles.css?v=14" rel="stylesheet"/></head><body>'
        '<canvas id="particles"></canvas><div class="top-glow"></div><nav id="nav"><div class="nav-wrap"><a class="logo-group" href="./index.html">'
        '<img alt="" class="logo-img" src="./assets/logo.png"/><div class="logo-text">THE AI<span class="logo-accent">UPDATE</span></div></a></div></nav>'
        '<main class="articles-index"><div class="sect-head"><p class="tag">ARCHIVE</p><h1>AI-only archive</h1></div>'
        f'<section class="sect"><section class="articles-grid">{cards_html}</section></section></main>'
        '<footer><div class="contain foot-inner"><div class="foot-brand"><img alt="" class="foot-logo" src="./assets/logo.png"/><span>THE AI UPDATE</span></div></div></footer>'
        '</body></html>'
    )


def run_cleanup(delete_remote: bool, dry_run: bool) -> dict:
    report: dict = {
        "audit": "topic_audit_latest",
        "generated_at": now_iso(),
        "rule": "Only AI-relevant topics are allowed: LLMs, reasoning models, image/music/video generation, AI tools/platform/model updates.",
        "scanned": {
            "briefings_md": 0,
            "website_article_pages": 0,
            "website_articles_html_links": 0,
            "website_archive_html_links": 0,
            "x_posted_rows": 0,
        },
        "removed": {
            "articles": [],
            "website_pages": [],
        },
        "deleted_tweets": [],
        "kept_counts": {},
        "delete_failures": [],
        "verification": {},
    }

    md_rows: dict[str, dict] = {}
    removed_article_ids: set[str] = set()

    for md in sorted(BRIEF_DIR.glob("briefing_*.md")):
        aid = md.stem.replace("briefing_", "")
        text = md.read_text(encoding="utf-8", errors="ignore")
        title = md_title(text, aid)
        keep = is_ai_topic_strict(title=title, content=text)
        report["scanned"]["briefings_md"] += 1
        md_rows[aid] = {"id": aid, "title": title, "keep": keep, "path": str(md.relative_to(PROJECT_ROOT))}
        if not keep:
            removed_article_ids.add(aid)
            report["removed"]["articles"].append({"id": aid, "title": title, "source": "briefing_md"})
            if not dry_run:
                md.unlink(missing_ok=True)

    for hp in sorted(WEB_ARTICLES_DIR.glob("*.html")):
        aid = hp.stem
        html = hp.read_text(encoding="utf-8", errors="ignore")
        title = html_text_title(html, aid)
        if aid in md_rows:
            keep = md_rows[aid]["keep"]
        else:
            keep = is_ai_topic_strict(title=title, content=strip_html(html))
        report["scanned"]["website_article_pages"] += 1
        if not keep:
            removed_article_ids.add(aid)
            report["removed"]["website_pages"].append({"id": aid, "title": title, "path": str(hp.relative_to(PROJECT_ROOT))})
            if not dry_run:
                hp.unlink(missing_ok=True)

    links_articles = set()
    links_archive = set()
    if ARTICLES_HTML.exists():
        txt = ARTICLES_HTML.read_text(encoding="utf-8", errors="ignore")
        links_articles = find_article_links(txt)
        report["scanned"]["website_articles_html_links"] = len(links_articles)
    if ARCHIVE_HTML.exists():
        txt = ARCHIVE_HTML.read_text(encoding="utf-8", errors="ignore")
        links_archive = find_article_links(txt)
        report["scanned"]["website_archive_html_links"] = len(links_archive)

    all_link_ids = sorted(links_articles | links_archive)
    kept_md_ids = {aid for aid, row in md_rows.items() if row["keep"] and (BRIEF_DIR / f"briefing_{aid}.md").exists()}
    for aid in all_link_ids:
        if aid in kept_md_ids:
            continue
        if aid not in removed_article_ids:
            removed_article_ids.add(aid)
            report["removed"]["articles"].append({"id": aid, "title": aid, "source": "website_link_only"})

    x_deleted = []
    x_kept = 0
    if POSTED_FILE.exists():
        payload = json.loads(POSTED_FILE.read_text(encoding="utf-8"))
        posted = payload.get("posted", []) if isinstance(payload, dict) else []
        report["scanned"]["x_posted_rows"] = len(posted)

        client = XAPIClient()
        can_delete = (not dry_run) and delete_remote and client.is_configured()

        kept_rows = []
        for row in posted:
            article_id = (row or {}).get("article_id", "")
            title = (row or {}).get("title", "")
            url = (row or {}).get("url", "")
            tweet_id = (row or {}).get("tweet_id")

            if article_id and article_id in md_rows:
                ai_ok = md_rows[article_id]["keep"]
            else:
                ai_ok = is_ai_topic_strict(title=title, summary=url)

            if ai_ok:
                kept_rows.append(row)
                x_kept += 1
                continue

            if can_delete and tweet_id:
                try:
                    res = client.delete_tweet(str(tweet_id))
                    if res.get("success"):
                        x_deleted.append({"tweet_id": str(tweet_id), "title": title, "article_id": article_id})
                    else:
                        report["delete_failures"].append({"tweet_id": str(tweet_id), "title": title, "error": res})
                except Exception as exc:
                    report["delete_failures"].append({"tweet_id": str(tweet_id), "title": title, "error": str(exc)})

        if not dry_run:
            payload["posted"] = kept_rows
            POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
            POSTED_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if not dry_run:
        subprocess.run([python_executable(), str(PROJECT_ROOT / "src" / "site_generator.py")], check=True, cwd=str(PROJECT_ROOT))
        remaining = []
        for md in sorted(BRIEF_DIR.glob("briefing_*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            aid = md.stem.replace("briefing_", "")
            txt = md.read_text(encoding="utf-8", errors="ignore")
            title = md_title(txt, aid)
            if not is_ai_topic_strict(title=title, content=txt):
                continue
            dt = datetime.fromtimestamp(md.stat().st_mtime)
            remaining.append({"id": aid, "title": title, "date": dt.strftime("Published %b %d, %Y")})
        ARTICLES_HTML.write_text(render_articles_html(remaining), encoding="utf-8")
        ARCHIVE_HTML.write_text(render_archive_html(remaining), encoding="utf-8")

    verify_hits = []
    for p in [BRIEF_DIR, WEB_ARTICLES_DIR, ARTICLES_HTML, ARCHIVE_HTML, POSTED_FILE]:
        if p.is_dir():
            for f in p.rglob("*"):
                if not f.is_file():
                    continue
                if VERIFY_ID in f.name:
                    verify_hits.append(str(f.relative_to(PROJECT_ROOT)))
                    continue
                try:
                    txt = f.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if VERIFY_ID in txt:
                    verify_hits.append(str(f.relative_to(PROJECT_ROOT)))
        elif p.exists():
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if VERIFY_ID in p.name or VERIFY_ID in txt:
                verify_hits.append(str(p.relative_to(PROJECT_ROOT)))

    report["deleted_tweets"] = x_deleted
    report["kept_counts"] = {
        "briefings_md": len(list(BRIEF_DIR.glob("briefing_*.md"))) if BRIEF_DIR.exists() else 0,
        "website_article_pages": len(list(WEB_ARTICLES_DIR.glob("*.html"))) if WEB_ARTICLES_DIR.exists() else 0,
        "x_posted_rows": x_kept,
    }
    report["verification"] = {
        "article_id": VERIFY_ID,
        "present_anywhere": bool(verify_hits),
        "paths": sorted(set(verify_hits)),
    }
    report["totals"] = {
        "removed_article_items": len(report["removed"]["articles"]),
        "removed_website_pages": len(report["removed"]["website_pages"]),
        "deleted_tweets": len(report["deleted_tweets"]),
        "delete_failures": len(report["delete_failures"]),
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Strict AI-topic cleanup across site + X + audit output")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delete-remote", action="store_true", help="Delete non-AI tweets via X API")
    args = ap.parse_args()

    out = run_cleanup(delete_remote=args.delete_remote, dry_run=args.dry_run)
    print(json.dumps({
        "report": str(REPORT_FILE),
        "scanned": out["scanned"],
        "totals": out["totals"],
        "verification": out["verification"],
    }, indent=2))
    return 0 if not out["verification"]["present_anywhere"] and not out["delete_failures"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
