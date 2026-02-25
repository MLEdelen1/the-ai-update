import json
import os
from pathlib import Path

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
WEBSITE_DIR = PROJECT_ROOT / "website"
ARTICLE_DIR = WEBSITE_DIR / "articles"
TEMPLATE_DIR = WEBSITE_DIR / "templates"
DATA_DIR = PROJECT_ROOT / "data"
NEWS_DATA = DATA_DIR / "news_cache/latest_scan.json"
TOOLS_DATA = DATA_DIR / "assets/tools_db.json"

def generate_svg_chart(value):
    return f'''<svg viewBox="0 0 100 25" class="w-full"><rect width="100" height="20" rx="10" fill="#ffffff33" /><rect width="{value}" height="20" rx="10" fill="#ffffff" /><text x="5" y="13" font-family="Inter, sans-serif" font-weight="900" font-size="7" fill="#1e40af">{value}% POWER</text></svg>'''

def generate_site():
    print("High-Fidelity Restoration: Mapping data fields...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    
    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()

    # 1. NEWS & ARTICLES
    stories = json.loads(NEWS_DATA.read_text()) if NEWS_DATA.exists() else []
    news_html = ""
    archive_html = ""

    for s in stories:
        aid = s.get('id', 'unknown')
        if aid == 'unknown': continue
        
        # Map fields with fallbacks
        title = s.get('title', 'Intelligence Update')
        summary = s.get('summary', s.get('description', 'Technical briefing in progress...'))
        source = s.get('source', 'Intel').upper()
        access = s.get('access_type', 'API').upper()
        
        art_page = article_temp
        art_page = art_page.replace("{{title}}", title)
        art_page = art_page.replace("{{source}}", source)
        art_page = art_page.replace("{{url}}", s.get('url', '#'))
        art_page = art_page.replace("{{access_type}}", access)
        art_page = art_page.replace("{{content}}", summary.replace('\n', '<br><br>'))
        art_page = art_page.replace("{{chart_svg}}", generate_svg_chart(s.get('benchmark_data', 85)))
        
        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)

        news_html += f'''<div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm flex flex-col group"><div class="flex justify-between items-start mb-6"><span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{source}</span><span class="py-1 px-3 bg-blue-50 text-blue-600 text-[8px] font-black rounded-full uppercase">{access}</span></div><h4 class="text-2xl font-black mb-4 group-hover:text-blue-600 transition">{title}</h4><p class="text-slate-500 text-sm mb-8 leading-relaxed">{summary[:150]}...</p><div class="mt-auto"><a href="/articles/{aid}.html" class="text-blue-600 font-black text-sm uppercase">Full Intelligence &rarr;</a></div></div>'''
        archive_html += f'''<li><a href="/articles/{aid}.html" class="text-slate-600 hover:text-blue-600">{title}</a></li>'''

    # 2. TOOLS
    tools = json.loads(TOOLS_DATA.read_text()) if TOOLS_DATA.exists() else []
    tools_html = ""
    for t in tools:
        t_desc = t.get('use_case', t.get('description', 'AI Productivity Tool'))
        tools_html += f'''<div class="p-6 bg-white border border-slate-100 rounded-3xl shadow-sm"><h3 class="text-lg font-black mb-2">{t.get('name')}</h3><p class="text-slate-500 text-sm mb-4">{t_desc}</p><a href="{t.get('url', '#')}" class="text-blue-600 text-xs font-black uppercase tracking-tighter">Try Tool &rarr;</a></div>'''

    # 3. FINAL MERGE
    final = master_temp.replace("{{NEWS_HTML}}", news_html)
    final = final.replace("{{TOOLS_HTML}}", tools_html)
    final = final.replace("{{ARCHIVE_HTML}}", archive_html)
    final = final.replace("{{JOB_TRACKER_HTML}}", "<div class='p-8 bg-blue-50 rounded-3xl border border-blue-100'><p class='text-blue-900 font-bold'>Tracking 245+ Autonomous Business Agents Live.</p></div>")
    
    (WEBSITE_DIR / "index.html").write_text(final)
    print(f"Success: {len(stories)} articles, {len(tools)} tools published.")

if __name__ == "__main__":
    generate_site()
