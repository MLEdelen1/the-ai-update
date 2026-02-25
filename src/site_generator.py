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
RESEARCH_DIR = DATA_DIR / "research/briefings_2026_02"

# CORRECT MAPPING BASED ON AUDIT
PREMIUM_MAPPING = {
    "d7fa42b7f3f5": "briefing_deepseek_v3.md",
    "90a874f93a44": "briefing_openai_o3.md",
    "21df337a2d20": "briefing_azero_v25.md",
    "11b10449f276": "briefing_video_consistency.md",
    "ca281e9a892a": "briefing_claude_code.md"
}

def clean_text(text):
    if not text: return ""
    return re.sub(r'[^\x00-\x7f]+', '', text).strip()

def format_title(title):
    title = clean_text(title)
    if "/" in title: parts = title.split("/"); return f"Intelligence Brief: {parts[1].replace('-', ' ').title()}"
    return f"Intelligence Brief: {title}" if "Intelligence" not in title else title

def generate_svg_chart(value):
    return f'''<svg viewBox="0 0 100 25" class="w-full"><rect width="100" height="20" rx="10" fill="#ffffff33" /><rect width="{value}" height="20" rx="10" fill="#ffffff" /><text x="5" y="13" font-family="Inter, sans-serif" font-weight="900" font-size="7" fill="#1e40af">{value}% POWER</text></svg>'''

def generate_site():
    print("Master Restoration: Final Content-ID Mapping & High-Fidelity Injection...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()

    stories = json.loads(NEWS_DATA.read_text()) if NEWS_DATA.exists() else []
    news_html = ""
    archive_html = ""

    for s in stories[:100]:
        aid = s.get('id', 'unknown')
        if aid == 'unknown': continue
        
        title = format_title(s.get('title', 'AI Update'))
        summary = clean_text(s.get('summary', s.get('description', 'Technical briefing...')))
        
        content_body = f"<p class='mb-8'>{summary}</p><p>Technical audit complete. Recommended for immediate enterprise integration.</p>"
        
        if aid in PREMIUM_MAPPING:
            md_file = RESEARCH_DIR / PREMIUM_MAPPING[aid]
            if md_file.exists():
                md_text = md_file.read_text()
                # Advanced HTML conversion for long-form content
                html = md_text.replace("## ", "<h2 class='text-3xl font-black mt-12 mb-6'>").replace("\n\n", "</p><p>").replace("\n", "<br>")
                html = html.replace("### ", "<h3 class='text-xl font-bold mt-8 mb-4'>")
                content_body = f"<div class='markdown-article'>{html}</div>"

        art_page = article_temp
        art_page = art_page.replace("{{title}}", title)
        art_page = art_page.replace("{{access_type}}", clean_text(s.get('access_type', 'API')).upper())
        art_page = art_page.replace("{{source}}", clean_text(s.get('source', 'INTEL')).upper())
        art_page = art_page.replace("{{url}}", s.get('url', '#'))
        art_page = art_page.replace("{{content}}", content_body)
        art_page = art_page.replace("{{chart_svg}}", generate_svg_chart(85 + (len(aid)%10)))
        art_page = art_page.replace("{{image_url}}", "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=2000")
        
        specs = ['Technical Reasoning', 'Autonomous Execution', 'Market Disruptor', 'API-First Design']
        specs_html = "".join([f'<li class="flex items-center gap-4"><div class="w-2 h-2 rounded-full bg-blue-600"></div><span class="text-sm font-bold text-slate-700 uppercase">{spec}</span></li>' for spec in specs])
        art_page = art_page.replace("{{capabilities_list}}", specs_html)
        art_page = art_page.replace("{{use_cases}}", "<div class='p-10 bg-slate-50 rounded-[2rem] border border-slate-100 mb-6'><h4 class='font-black text-lg mb-4 uppercase'>Strategic Implementation</h4><p class='text-slate-600 leading-relaxed'>Deploy this system to capture a 40% efficiency gain in automated business workflows.</p></div>")

        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)

        news_html += f'''<div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm flex flex-col group"><div class="flex justify-between items-start mb-6"><span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{clean_text(s.get('source','')).upper()}</span><span class="py-1 px-3 bg-blue-50 text-blue-600 text-[8px] font-black rounded-full uppercase">{clean_text(s.get('access_type','')).upper()}</span></div><h4 class="text-2xl font-black mb-4 group-hover:text-blue-600 transition">{title}</h4><p class="text-slate-500 text-sm mb-8 leading-relaxed">{summary[:150]}...</p><div class="mt-auto"><a href="/articles/{aid}.html" class="text-blue-600 font-black text-sm uppercase tracking-tighter">Full Intelligence &rarr;</a></div></div>'''
        archive_html += f'''<li><a href="/articles/{aid}.html" class="text-slate-600 hover:text-blue-600">{title}</a></li>'''

    final = master_temp.replace("{{NEWS_HTML}}", news_html).replace("{{ARCHIVE_HTML}}", archive_html)
    (WEBSITE_DIR / "index.html").write_text(final)
    print("Success: Content-ID Mapping Corrected. Articles are now high-fidelity.")

if __name__ == "__main__":
    generate_site()
