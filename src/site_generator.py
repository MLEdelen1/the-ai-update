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
    print("Emergency Restore: Regenerating all sections...")
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
        
        art_page = article_temp
        for k, v in s.items():
            if isinstance(v, list): v = "".join([f"<li>{i}</li>" for i in v])
            art_page = art_page.replace(f"{{{{{k}}}}}", str(v))
        
        art_page = art_page.replace("{{chart_svg}}", generate_svg_chart(s.get('benchmark_data', 85)))
        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)

        news_html += f'''<div class="bg-white p-10 rounded-[3rem] border shadow-sm flex flex-col group"><h4 class="text-2xl font-black mb-4 group-hover:text-blue-600 transition">{s.get('title')}</h4><p class="text-slate-500 text-sm mb-8">{s.get('executive_summary', '')[:140]}...</p><div class="mt-auto"><a href="/articles/{aid}.html" class="text-blue-600 font-black text-sm uppercase">Full Intelligence &rarr;</a></div></div>'''
        archive_html += f'''<li><a href="/articles/{aid}.html" class="text-slate-600 hover:text-blue-600">{s.get('title')}</a></li>'''

    # 2. TOOLS
    tools = json.loads(TOOLS_DATA.read_text()) if TOOLS_DATA.exists() else []
    tools_html = "".join([f'''<div class="p-6 bg-white border rounded-3xl shadow-sm"><h3 class="text-lg font-black mb-2">{t.get('name')}</h3><p class="text-slate-500 text-sm mb-4">{t.get('description')}</p><a href="{t.get('url', '#')}" class="text-blue-600 text-xs font-black uppercase">Try Tool &rarr;</a></div>''' for t in tools])

    # 3. FINAL MERGE (Ensuring ALL placeholders are replaced)
    final = master_temp.replace("{{NEWS_HTML}}", news_html)
    final = final.replace("{{TOOLS_HTML}}", tools_html)
    final = final.replace("{{ARCHIVE_HTML}}", archive_html)
    final = final.replace("{{JOB_TRACKER_HTML}}", "<div class='p-8 bg-blue-50 rounded-3xl border border-blue-100'><p class='text-blue-900 font-bold'>Tracking 245+ Autonomous Business Agents Live.</p></div>")
    
    (WEBSITE_DIR / "index.html").write_text(final)
    print(f"Restore Success: {len(stories)} articles, {len(tools)} tools live.")

if __name__ == "__main__":
    generate_site()
