
import re as _re
def enforce_english(text):
    if not isinstance(text, str): return text
    # Aggressively remove CJK characters
    return _re.sub(r'[一-鿿㐀-䶿豈-﫿぀-ゟ゠-ヿ]+', '', text)
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

IMG_CATS = {
    "CODE": ["1555066931-4365d14bab8c", "1515879218367-8466d910aaa4", "1587620962725-abab7fe55159", "1542831371-29b0f74f9713"],
    "VIDEO": ["1536240478700-b869070f9279", "1492724724894-7464c27d0ceb", "1485846234645-a62644f84728"],
    "MONEY": ["1553729459-efe14ef6055d", "1554260678-955ee338676a", "1526303322584-23a0740e29b1"],
    "ROBOT": ["1485827404703-89b55fcc595e", "1531746020798-e6953c6e8e32", "1535378620153-f8a0c21b5042"],
    "AI": ["1677442136019-21780ecad995", "1518770660439-4636190af475", "1558491947-0763d78a906e"]
}

def get_contextual_img(title, index):
    title = title.lower()
    cat = "AI"
    if any(k in title for k in ["code", "dev", "git", "python", "script"]): cat = "CODE"
    elif any(k in title for k in ["video", "film", "camera", "movie"]): cat = "VIDEO"
    elif any(k in title for k in ["money", "fund", "cash", "earn"]): cat = "MONEY"
    elif any(k in title for k in ["robot", "agent", "bot", "humanoid"]): cat = "ROBOT"
    pool = IMG_CATS.get(cat, IMG_CATS["AI"])
    img_id = pool[index % len(pool)]
    return f"https://images.unsplash.com/photo-{img_id}?q=80&w=1200&auto=format&fit=crop"

def clean_text(text):
    if not text: return ""
    return re.sub(r'[^-]+', '', text).strip()

def format_title(title):
    title = str(title).replace('-', ' ').replace('_', ' ')
    title = re.sub(r'^[a-zA-Z0-9.-]+/', '', title)
    title = re.sub(r'[^a-zA-Z0-9 ]', ' ', title)
    title = re.sub(r' +', ' ', title).strip().title()
    words = title.split()
    if len(words) > 10: return " ".join(words[:10]) + "..."
    return title

def generate_content(title, summary, index, aid):
    import markdown
    md_path = DATA_DIR / f"research/briefings_2026_02/briefing_{aid}.md"
    if md_path.exists():
        md_text = md_path.read_text()
        return markdown.markdown(md_text, extensions=['tables'])
    return f"<p>Content currently being compiled for {title}. Please check back shortly.</p>"

def get_static_mocks():
    stats = """
    <div class="stat-card"><div class="stat-label">O3-MINI API / 1M TOKENS</div><div class="stat-val">$1.10 <span class="stat-delta delta-down">&darr; 45%</span></div></div>
    <div class="stat-card"><div class="stat-label">MODELS ON HUGGINGFACE</div><div class="stat-val">1.6M <span class="stat-delta delta-up">&uarr; 12%</span></div></div>
    <div class="stat-card"><div class="stat-label">AI STARTUP FUNDING Q1</div><div class="stat-val">$22.4B <span class="stat-delta delta-up">&uarr; 15%</span></div></div>
    <div class="stat-card"><div class="stat-label">AVG AGENT LATENCY</div><div class="stat-val">0.9s <span class="stat-delta delta-flat">&rarr; 0%</span></div></div>
    """
    models = """
    <div class="model-card"><div class="model-head"><h3>OpenAI o3</h3><span>OPENAI &bull; JAN 2026</span></div><div class="model-metrics"><div class="metric"><div class="metric-val">98.1</div><div class="metric-label">MMLU</div></div><div class="metric"><div class="metric-val">96.4</div><div class="metric-label">MATH</div></div><div class="metric"><div class="metric-val">$4.00</div><div class="metric-label">/1M TOK</div></div></div></div>
    <div class="model-card"><div class="model-head"><h3>DeepSeek R1</h3><span>DEEPSEEK &bull; JAN 2026</span></div><div class="model-metrics"><div class="metric"><div class="metric-val">97.3</div><div class="metric-label">MMLU</div></div><div class="metric"><div class="metric-val">97.0</div><div class="metric-label">MATH</div></div><div class="metric"><div class="metric-val">$0.55</div><div class="metric-label">/1M TOK</div></div></div></div>
    <div class="model-card"><div class="model-head"><h3>Gemini 3.1 Pro</h3><span>GOOGLE &bull; FEB 2026</span></div><div class="model-metrics"><div class="metric"><div class="metric-val">95.0</div><div class="metric-label">MMLU</div></div><div class="metric"><div class="metric-val">92.1</div><div class="metric-label">MATH</div></div><div class="metric"><div class="metric-val">$2.50</div><div class="metric-label">/1M TOK</div></div></div></div>
    <div class="model-card"><div class="model-head"><h3>Claude 3.5 Opus</h3><span>ANTHROPIC &bull; LATE 2025</span></div><div class="model-metrics"><div class="metric"><div class="metric-val">95.4</div><div class="metric-label">MMLU</div></div><div class="metric"><div class="metric-val">92.0</div><div class="metric-label">MATH</div></div><div class="metric"><div class="metric-val">$15.00</div><div class="metric-label">/1M TOK</div></div></div></div>
    """
    os_grid = """
    <a href="https://github.com/deepseek-ai/DeepSeek-R1" target="_blank" class="os-card"><div class="os-title">deepseek-ai/DeepSeek-R1</div><div class="os-desc">Open-weight reasoning model matching OpenAI o1/o3 performance. Apache 2.0.</div><div class="os-meta">110k &bull; Python &bull; Updated 2h ago</div></a>
    <a href="https://huggingface.co/Qwen/Qwen2.5-Max" target="_blank" class="os-card"><div class="os-title">Qwen/Qwen2.5-Max</div><div class="os-desc">Alibaba's flagship open LLM. Massive context, top-tier coding and math.</div><div class="os-meta">45.2k &bull; Python &bull; Updated 5h ago</div></a>
    <a href="https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct" target="_blank" class="os-card"><div class="os-title">meta-llama/Llama-3.3-70B-Instruct</div><div class="os-desc">State-of-the-art 70B model matching Llama 3 400B performance.</div><div class="os-meta">89.4k &bull; Python &bull; Updated 1d ago</div></a>
    <a href="https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview" target="_blank" class="os-card"><div class="os-title">anthropics/claude-code</div><div class="os-desc">Agentic coding tool for the terminal. Understands your codebase deeply.</div><div class="os-meta">38.7k &bull; TypeScript &bull; Updated 8h ago</div></a>
    """
    return stats, models, os_grid


def generate_archive_page():
    print("Building Archive Page...")
    md_files = list(DATA_DIR.glob("research/briefings_2026_02/briefing_*.md"))
    md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    archive_items = ""
    for md_path in md_files:
        aid = md_path.stem.replace('briefing_', '')
        content = md_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        title = "Untitled"
        for line in lines:
            if line.strip().startswith('# '):
                title = line.strip().replace('# ', '').strip()
                break

        hook = ""
        for line in lines:
            if line.strip() and not line.startswith('#') and len(line) > 40:
                hook = clean_text(line)[:120] + "..."
                break

        archive_items += f'''<a href="/articles/{aid}.html" class="analysis-card" style="display: flex; flex-direction: column; gap: 0.75rem;">
            <div class="analysis-meta">INTEL &bull; ARCHIVE</div>
            <h3 style="margin: 0; font-size: 1.2rem; line-height: 1.3;">{title}</h3>
            <p style="margin: 0; color: var(--text-muted); font-size: 0.9rem; line-height: 1.5; margin-bottom: 1rem;">{hook}</p>
            <div style="margin-top: auto; font-size: 0.75rem; color: var(--accent); font-weight: 600; letter-spacing: 1px;">READ FULL &rarr;</div>
        </a>'''

    master_temp = (TEMPLATE_DIR / "master.html").read_text(encoding='utf-8')

    import re as _re
    parts = _re.split(r'<main[^>]*>', master_temp)
    if len(parts) > 1:
        header_part = parts[0]
        footer_part = _re.split(r'</main>', parts[1])[1]
    else:
        header_part = master_temp
        footer_part = ""

    archive_html = header_part + '<main style="padding-top: 120px; padding-bottom: 100px; max-width: 1200px; margin: 0 auto; width: 100%; padding-left: 1rem; padding-right: 1rem;">'
    archive_html += '<div class="section-header" style="margin-bottom: 3rem; text-align: center; justify-content: center;"><h2 class="section-title">ALL <span>ARTICLES</span></h2><p style="color: var(--text-muted);">The complete intelligence archive.</p></div>'
    archive_html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem;">'
    archive_html += archive_items
    archive_html += '</div></main>' + footer_part

    (WEBSITE_DIR / "archive.html").write_text(enforce_english(archive_html), encoding='utf-8')


def generate_site():
    print("REBUILDING: Verified UI Layout (Signal/Neon Green)...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()

    stories = json.loads(NEWS_DATA.read_text()) if NEWS_DATA.exists() else []
    f_html = ""; n_html = ""; a_html = ""
    stats, models, os_grid = get_static_mocks()

    for i, s in enumerate(stories[:30]):
        aid = s.get('id', 'unknown')
        if aid == 'unknown': continue

        title = format_title(s.get('title', ''))
        summary = clean_text(s.get('summary', s.get('description', '')))

        # Override with exact markdown data
        md_path = DATA_DIR / f"research/briefings_2026_02/briefing_{aid}.md"
        if md_path.exists():
            lines = md_path.read_text().splitlines()
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

        content = generate_content(title, summary, i, aid)
        import re as _re
        _hook = ''

        # 1. Remove all headers from the HTML so we don't accidentally grab them
        _no_headers = _re.sub(r'<h[1-6].*?</h[1-6]>', '', content, flags=_re.IGNORECASE|_re.DOTALL)

        # 2. Extract bullets and paragraphs
        _lis = _re.findall(r'<li>(.*?)</li>', _no_headers, flags=_re.IGNORECASE|_re.DOTALL)
        _ps = _re.findall(r'<p>(.*?)</p>', _no_headers, flags=_re.IGNORECASE|_re.DOTALL)

        # 3. Try to get a high-signal bullet point (pros/features)
        for _li in _lis:
            _clean_li = _re.sub(r'<[^>]+>', '', _li).strip()
            if len(_clean_li) > 30:
                _hook = _clean_li
                break

        # 4. If no bullet, grab the SECOND paragraph (skipping the intro)
        if len(_hook) < 20:
            if len(_ps) > 1:
                _hook = _re.sub(r'<[^>]+>', '', _ps[1]).strip()
            elif len(_ps) > 0:
                _hook = _re.sub(r'<[^>]+>', '', _ps[0]).strip()

        # 5. Fallback to the original news scan summary if HTML fails
        if len(_hook) < 20 and summary:
            _hook = summary.split('|')[0]

        # 6. Clean and truncate
        _hook = _re.sub(r'\s+', ' ', _hook).replace('**', '').replace('*', '').replace('`', '').strip()
        if _hook.lower().startswith('based on'):
            _hook = _re.sub(r'(?i)based on.*?(video|channel)\.?\s*', '', _hook).strip()

        display_summary = _hook[:127] + '...' if len(_hook) > 130 else _hook

        if len(display_summary) < 15:
            display_summary = f"Discover the technical breakdown and use cases for {title}."
        source_clean = clean_text(s.get('source', 'WEB')).upper()
        if not source_clean: source_clean = "INTEL"
        img_url = get_contextual_img(title, i)

        # Build Article Page
        art_page = article_temp.replace("{{title}}", title)
        art_page = art_page.replace("{{source}}", source_clean)
        art_page = art_page.replace("{{url}}", s.get('url', '#'))
        art_page = art_page.replace("{{content}}", content)
        art_page = art_page.replace("{{description}}", display_summary.replace('"', '&quot;'))
        art_page = art_page.replace("{{image_url}}", img_url)
        (ARTICLE_DIR / f"{aid}.html").write_text(enforce_english(art_page))

        url_local = f"/articles/{aid}.html"

        # Build Homepage Grids
        if i == 0:
            f_html = f"""<div class="featured">
                <a href="{url_local}"><img src="{img_url}" class="featured-img" alt="{title}"></a>
                <div class="featured-meta"><span class="featured-cat">{source_clean}</span><span>6 MIN READ &bull; RESEARCH</span></div>
                <a href="{url_local}"><h2>{title}</h2></a>
                
                <a href="{url_local}">Read the full brief &rarr;</a>
            </div>"""
        elif 1 <= i <= 6:
            time_ago = f"{i*2} HRS AGO"
            n_html += f"""<a href="{url_local}" class="latest-item">
                <div class="latest-meta"><span class="latest-cat">{source_clean}</span><span>{time_ago}</span></div>
                <h3>{title}</h3>
                <p>{display_summary}</p>
                
            </a>"""
        elif 7 <= i <= 12:
            num_str = f"0{i-6}"
            a_html += f"""<a href="{url_local}" class="analysis-card" data-num="{num_str}">
                <div class="analysis-meta">{source_clean}</div>
                <h3>{title}</h3>
                <p>{display_summary}</p>
                
                <div class="analysis-read">14 MIN READ</div>
            </a>"""

    t_html = ""
    if TOOLS_DATA.exists():
        try:
            for t in json.loads(TOOLS_DATA.read_text()):
                t_html += f"""<a href="{t.get('url','#')}" target="_blank" class="tool-card">
                    <div class="model-head"><h3>{t.get('name','')}</h3><span>{t.get('category','')}</span></div>
                    <p style="font-size:13px; color:var(--text-muted);">{t.get('description','')}</p>
                </a>"""
        except: pass

    final = master_temp.replace("{{STATS_HTML}}", stats)\
                       .replace("{{FEATURED_HTML}}", f_html)\
                       .replace("{{NEWS_HTML}}", n_html)\
                       .replace("{{ANALYSIS_HTML}}", a_html)\
                       .replace("{{MODELS_HTML}}", models)\
                       .replace("{{OPENSOURCE_HTML}}", os_grid)\
                       .replace("{{TOOLS_HTML}}", t_html)
    (WEBSITE_DIR / "index.html").write_text(final)
    generate_archive_page()

if __name__ == "__main__":
    generate_site()
