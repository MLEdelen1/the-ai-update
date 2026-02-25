import json
import os
import re
import hashlib
from pathlib import Path

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
WEBSITE_DIR = PROJECT_ROOT / "website"
ARTICLE_DIR = WEBSITE_DIR / "articles"
TEMPLATE_DIR = WEBSITE_DIR / "templates"
DATA_DIR = PROJECT_ROOT / "data"
NEWS_DATA = DATA_DIR / "news_cache/latest_scan.json"
TOOLS_DATA = DATA_DIR / "assets/tools_db.json"

# Categorized high-quality unique Unsplash IDs
IMG_CATS = {
    "CODE": ["1555066931-4365d14bab8c", "1515879218367-8466d910aaa4", "1587620962725-abab7fe55159", "1542831371-29b0f74f9713", "1550751827-4bd374c3f58b", "1498050108023-c5249f4df085"],
    "VIDEO": ["1536240478700-b869070f9279", "1492724724894-7464c27d0ceb", "1485846234645-a62644f84728", "1535016120720-40c64658530e", "1470225620779-ad8a333d42d2"],
    "MONEY": ["1553729459-efe14ef6055d", "1554260678-955ee338676a", "1526303322584-23a0740e29b1", "1565514020-1864760ebe58", "1579621970518-1e16e5049bcd"],
    "ROBOT": ["1485827404703-89b55fcc595e", "1531746020798-e6953c6e8e32", "1535378620153-f8a0c21b5042", "1589254065821-4f114674780d", "1527430614720-8033f749ca0a"],
    "AI": ["1677442136019-21780ecad995", "1518770660439-4636190af475", "1558491947-0763d78a906e", "1592478411213-6153e4ebc07d", "1531746020798-e6953c6e8e32", "1507413241184-b12eaf468677", "1618005182384-a83a8bd57fbe", "1620712446950-ed20f396657c"],
    "TECH": ["1518770660439-4636190af475", "1550439062-609e15462721", "1519389950441-db75ce01cd91", "1487058715970-3f47b5e54911", "1563986768-d0e2c2f7b83d", "1551434678-e076c223a692", "1526374965328-7f61d4dc18c5", "1550741164-1507413241184", "1544197150-149955d52239"]
}

# Fallback pool
FALLBACK_POOL = ["1517077304055-6e89a3842c17", "1460925895917-afdab827c52f", "1581092160239-7f1a23e2076a", "1523961131910-4473c72c9d7f", "1539321397402-15a98401f252", "1516116216646-da5e3ae8b74a", "1496065187424-4d5af4a7d194", "1531206714890-00120cd89f14"]

USED_IMAGES = set()

def get_contextual_img(title, index, offset=0):
    title = title.lower()
    cat = "AI"
    if any(k in title for k in ["code", "dev", "git", "python", "script"]): cat = "CODE"
    elif any(k in title for k in ["video", "film", "camera", "movie", "frame"]): cat = "VIDEO"
    elif any(k in title for k in ["money", "fund", "cash", "earn", "profit", "business"]): cat = "MONEY"
    elif any(k in title for k in ["robot", "agent", "bot", "humanoid"]): cat = "ROBOT"

    pool = IMG_CATS.get(cat, FALLBACK_POOL)
    # Attempt to pick a unique one from cat pool first, then fallback
    for i in range(len(pool)):
        img_id = pool[(index + i + offset) % len(pool)]
        if img_id not in USED_IMAGES:
            USED_IMAGES.add(img_id)
            return f"https://images.unsplash.com/photo-{img_id}?q=80&w=1200&auto=format&fit=crop"

    # Complete unique fallback
    for img_id in FALLBACK_POOL:
        if img_id not in USED_IMAGES:
            USED_IMAGES.add(img_id)
            return f"https://images.unsplash.com/photo-{img_id}?q=80&w=1200&auto=format&fit=crop"

    # Last resort (should not happen with 150+ pool)
    return f"https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop"

def clean_text(text):
    if not text: return ""
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()

def format_title(title):
    import re
    title = str(title).replace('-', ' ').replace('_', ' ')
    title = re.sub(r'^[a-zA-Z0-9.-]+/', '', title) # clean repo prefixes
    title = re.sub(r'[^a-zA-Z0-9 ]', ' ', title)   # remove weird chars
    title = re.sub(r' +', ' ', title).strip().title() # remove double spaces
    words = title.split()
    if len(words) > 10:
        return " ".join(words[:10]) + "..."
    return title

def generate_content(title, summary, index, aid):
    import markdown
    md_path = DATA_DIR / f"research/briefings_2026_02/briefing_{aid}.md"
    if md_path.exists():
        md_text = md_path.read_text()
        # Convert markdown to html
        html_content = markdown.markdown(md_text, extensions=['tables'])
        # Add a bit of styling to tables and blockquotes
        html_content = html_content.replace('<table>', '<table class="min-w-full my-8 bg-white shadow-sm rounded-xl overflow-hidden">')
        html_content = html_content.replace('<thead>', '<thead class="bg-slate-50">')
        html_content = html_content.replace('<th>', '<th class="px-6 py-4 text-left text-xs font-bold uppercase tracking-widest text-slate-500">')
        html_content = html_content.replace('<td>', '<td class="px-6 py-4 border-t border-slate-100">')
        html_content = html_content.replace('<blockquote>', '<blockquote class="border-l-4 border-blue-500 pl-4 py-2 my-6 bg-blue-50 text-slate-700 italic rounded-r-lg">')
        html_content = html_content.replace('<h1>', '<h1 class="text-4xl font-black mb-6">')
        html_content = html_content.replace('<h2>', '<h2 class="text-2xl font-bold mt-10 mb-4 text-blue-900">')
        html_content = html_content.replace('<h3>', '<h3 class="text-xl font-bold mt-8 mb-3">')
        html_content = html_content.replace('<p>', '<p class="mb-6 text-lg text-slate-700 leading-relaxed">')
        html_content = html_content.replace('<ul>', '<ul class="list-disc pl-6 mb-6 space-y-2 text-lg text-slate-700">')
        return html_content
    else:
        return f"<p class='text-lg'>Content currently being compiled for {title}. Please check back shortly.</p>"


def generate_site():
    print("REBUILDING: Contextual Image & Human-Divergence Engine...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    USED_IMAGES.clear()

    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()

    stories = json.loads(NEWS_DATA.read_text()) if NEWS_DATA.exists() else []
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
                        
        display_summary = summary[:130] + "..." if len(summary) > 130 else summary
        content = generate_content(title, summary, i, aid)
        
        art_page = article_temp.replace("{{title}}", title)
        art_page = art_page.replace("{{access_type}}", "Technical Brief")
        art_page = art_page.replace("{{source}}", clean_text(s.get('source', 'WEB')).upper())
        art_page = art_page.replace("{{url}}", s.get('url', '#'))
        art_page = art_page.replace("{{content}}", content)
        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)
        
        news_html += f'<div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm flex flex-col hover:border-blue-400 transition-all"><div class="flex justify-between items-center mb-6"><span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{clean_text(s.get("source","")).upper()}</span><span class="px-3 py-1 bg-blue-600 text-white text-[8px] font-black rounded-full uppercase">DEEP DIVE</span></div><h4 class="text-2xl font-black mb-4 leading-none">{title}</h4><p class="text-slate-500 text-sm mb-10 font-medium">{display_summary}</p><div class="mt-auto"><a href="/articles/{aid}.html" class="text-blue-600 font-bold text-xs uppercase tracking-widest border-b-2 border-blue-50">Read Comprehensive Resource &rarr;</a></div></div>'
        
        archive_html += f'<li><a href="/articles/{aid}.html" class="text-slate-500 hover:text-blue-600 transition-colors">{title}</a></li>'

    tools_html = ""
    if TOOLS_DATA.exists():
        try:
            tools = json.loads(TOOLS_DATA.read_text())
            for t in tools:
                t_name = t.get("name", "")
                t_cat = t.get("category", "AI")
                t_desc = t.get("description", "")
                t_url = t.get("url", "#")
                tools_html += f'<div class="bg-slate-800 p-8 rounded-3xl border border-slate-700 flex flex-col"><div class="flex justify-between items-center mb-4"><h4 class="text-xl font-bold text-white">{t_name}</h4><span class="px-2 py-1 bg-blue-600/20 text-blue-400 text-[10px] font-black rounded uppercase">{t_cat}</span></div><p class="text-slate-400 text-sm mb-6">{t_desc}</p><a href="{t_url}" target="_blank" class="mt-auto text-blue-400 font-bold text-xs uppercase tracking-widest hover:text-white transition-colors">Try Now &rarr;</a></div>'
        except Exception as e:
            print(f"Error loading tools: {e}")

    final = master_temp.replace("{{NEWS_HTML}}", news_html).replace("{{ARCHIVE_HTML}}", archive_html).replace("{{TOOLS_HTML}}", tools_html).replace("{{JOB_TRACKER_HTML}}", "")
    (WEBSITE_DIR / "index.html").write_text(final)

if __name__ == "__main__":
    generate_site()
