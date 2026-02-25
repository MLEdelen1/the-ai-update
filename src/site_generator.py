import json
import os
import re
from pathlib import Path

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
WEBSITE_DIR = PROJECT_ROOT / "website"
ARTICLE_DIR = WEBSITE_DIR / "articles"
TEMPLATE_DIR = WEBSITE_DIR / "templates"
DATA_DIR = PROJECT_ROOT / "data"
NEWS_DATA = DATA_DIR / "news_cache/latest_scan.json"
TOOLS_DATA = DATA_DIR / "assets/tools_db.json"

def clean_text(text):
    if not text: return ""
    return re.sub(r'[^-]+', '', text).strip()

def format_title(title):
    title = str(title).replace('-', ' ').replace('_', ' ')
    title = re.sub(r'^[a-zA-Z0-9.-]+/', '', title)
    title = re.sub(r'[^a-zA-Z0-9 ]', ' ', title)
    title = re.sub(r' +', ' ', title).strip().title()
    words = title.split()
    if len(words) > 10:
        return " ".join(words[:10]) + "..."
    return title

def generate_content(title, summary, index, aid):
    import markdown
    md_path = DATA_DIR / f"research/briefings_2026_02/briefing_{aid}.md"
    if md_path.exists():
        md_text = md_path.read_text()
        return markdown.markdown(md_text, extensions=['tables'])
    return f"<p>Content currently being compiled for {title}. Please check back shortly.</p>"

def generate_site():
    print("REBUILDING: Signal Intelligence Layout...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)

    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()

    stories = json.loads(NEWS_DATA.read_text()) if NEWS_DATA.exists() else []

    featured_html = ""
    news_html = ""
    archive_html = ""

    for i, s in enumerate(stories[:100]):
        aid = s.get('id', 'unknown')
        if aid == 'unknown': continue

        title = format_title(s.get('title', ''))
        summary = clean_text(s.get('summary', s.get('description', '')))

        md_path = DATA_DIR / f"research/briefings_2026_02/briefing_{aid}.md"
        if md_path.exists():
            md_text = md_path.read_text()
            lines = md_text.splitlines()
            for line in lines:
                if line.strip().startswith('# '):
                    title = line.strip().replace('# ', '').strip()
                    break
            if len(summary) < 20:
                for line in lines:
                    cl = line.strip()
                    if cl and not cl.startswith('#') and len(cl) > 40:
                        summary = clean_text(cl)
                        break

        display_summary = summary[:160] + "..." if len(summary) > 160 else summary
        content = generate_content(title, summary, i, aid)

        source_clean = clean_text(s.get('source', 'WEB')).upper()
        if not source_clean: source_clean = "INTEL"

        art_page = article_temp.replace("{{title}}", title)
        art_page = art_page.replace("{{source}}", source_clean)
        art_page = art_page.replace("{{url}}", s.get('url', '#'))
        art_page = art_page.replace("{{content}}", content)
        safe_desc = display_summary.replace('"', '&quot;')
        art_page = art_page.replace("{{description}}", safe_desc)
        art_page = art_page.replace("{{url_full}}", f"https://theaiupdate.org/articles/{aid}.html")
        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)

        if i == 0:
            featured_html += f"""<a href="/articles/{aid}.html" class="lead">
                <div class="lead-visual">
                    <div class="lead-cat">{source_clean}</div>
                    <div class="lead-big">{title[:3].upper()}_</div>
                </div>
                <div class="lead-body">
                    <div class="meta-line">
                        <span>{source_clean}</span><span>DEEP DIVE</span>
                    </div>
                    <h2>{title}</h2>
                    <p>{display_summary}</p>
                </div>
            </a>"""
        else:
            news_html += f"""<a href="/articles/{aid}.html" class="feed-item">
                <div class="meta-line"><span class="cat">{source_clean}</span></div>
                <h3>{title}</h3>
                <p>{display_summary}</p>
            </a>"""

        archive_html += f'<a href="/articles/{aid}.html" class="feed-item" style="padding:12px 0; border-bottom: 1px dashed var(--rule);"><h3>{title}</h3></a>'

    tools_html = ""
    if TOOLS_DATA.exists():
        try:
            tools = json.loads(TOOLS_DATA.read_text())
            for t in tools:
                t_name = t.get("name", "")
                t_cat = t.get("category", "AI")
                t_desc = t.get("description", "")
                t_url = t.get("url", "#")
                tools_html += f"""<a href="{t_url}" target="_blank" class="tool-item">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <h4>{t_name}</h4><span class="tool-cat">{t_cat}</span>
                    </div>
                    <p>{t_desc}</p>
                    <span class="btn-launch">Launch Tool &rarr;</span>
                </a>"""
        except Exception as e:
            print(f"Error loading tools: {e}")

    sm = '<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'
    sm += '  <url>
    <loc>https://theaiupdate.org/</loc>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
'
    try:
        for s in json.loads(NEWS_DATA.read_text()):
            if s.get("id"):
                sm += f'  <url>
    <loc>https://theaiupdate.org/articles/{s.get("id")}.html</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
'
    except:
        pass
    sm += '</urlset>'
    (WEBSITE_DIR / "sitemap.xml").write_text(sm)
    (WEBSITE_DIR / "robots.txt").write_text("User-agent: *
Allow: /
Sitemap: https://theaiupdate.org/sitemap.xml")

    final = master_temp.replace("{{FEATURED_HTML}}", featured_html).replace("{{NEWS_HTML}}", news_html).replace("{{ARCHIVE_HTML}}", archive_html).replace("{{TOOLS_HTML}}", tools_html)
    (WEBSITE_DIR / "index.html").write_text(final)

if __name__ == "__main__":
    generate_site()
