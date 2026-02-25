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
    return f'''<svg viewBox="0 0 100 25" class="w-full"><rect width="100" height="20" rx="10" fill="#ffffff33"/><rect width="{value}" height="20" rx="10" fill="#ffffff"/><text x="5" y="13" font-family="Inter, sans-serif" font-weight="900" font-size="7" fill="#1e40af">{value}% POWER</text></svg>'''

def generate_site():
    print("Master Production Cycle: Regenerating High-Fidelity Portal...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load Templates
    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()

    # 1. NEWS & ARTICLES
    if not NEWS_DATA.exists():
        print("No news data found.")
        return
        
    stories = json.loads(NEWS_DATA.read_text())
    news_html = ""
    archive_html = ""

    for s in stories:
        aid = s.get('id', 'unknown')
        if aid == 'unknown': continue
        
        # Prepare dynamic content for article page
        art_page = article_temp
        fields = ['title', 'source', 'url', 'access_type', 'executive_summary']
        for f in fields:
            val = s.get(f, 'N/A')
            art_page = art_page.replace(f"{{{{{f}}}}}", str(val))
            
        # Complex fields (lists)
        cap_html = "".join([f'<li>{c}</li>' for c in s.get('capabilities', [])])
        use_html = "".join([f'<div class="p-4 bg-slate-50 rounded-xl">{u}</div>' for u in s.get('practical_use_cases', [])])
        
        art_page = art_page.replace("{{capabilities_list}}", cap_html)
        art_page = art_page.replace("{{use_cases}}", use_html)
        art_page = art_page.replace("{{content}}", s.get('executive_summary', '').replace('\n', '<br><br>'))
        art_page = art_page.replace("{{chart_svg}}", generate_svg_chart(s.get('benchmark_data', 85)))
        
        # Save individual article
        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)

        # Homepage Summary Card
        news_html += f'''
        <div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm hover:shadow-xl transition-all group flex flex-col">
            <div class="flex justify-between items-start mb-6">
                <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{s.get('source', 'Intel')}</span>
                <span class="py-1 px-3 bg-blue-50 text-blue-600 text-[8px] font-black rounded-full uppercase">{s.get('access_type', 'API')}</span>
            </div>
            <h4 class="text-2xl font-black mb-4 group-hover:text-blue-600 transition">{s.get('title', 'AI Breakthrough')}</h4>
            <p class="text-slate-500 text-sm mb-8 leading-relaxed">{s.get('executive_summary', '')[:140]}...</p>
            <div class="mt-auto">
                <a href="/articles/{aid}.html" class="inline-flex items-center gap-2 text-blue-600 font-black text-sm uppercase tracking-tighter">Full Intelligence &rarr;</a>
            </div>
        </div>'''
        
        archive_html += f'<li><a href="/articles/{aid}.html" class="text-slate-600 hover:text-blue-600 font-medium">{s.get("title")}</a></li>'

    # 2. TOOLS
    tools = []
    if TOOLS_DATA.exists():
        tools = json.loads(TOOLS_DATA.read_text())
    
    tools_html = "".join([f'''
    <div class="p-6 bg-white border border-slate-100 rounded-3xl shadow-sm">
        <h3 class="text-lg font-black mb-2">{t.get('name')}</h3>
        <p class="text-slate-500 text-sm mb-4">{t.get('description')}</p>
        <a href="{t.get('url', '#')}" target="_blank" class="text-blue-600 text-xs font-black uppercase">Try Tool &rarr;</a>
    </div>''' for t in tools])

    # 3. FINAL MERGE INTO MASTER
    final_home = master_temp.replace("{{NEWS_HTML}}", news_html)
    final_home = final_home.replace("{{TOOLS_HTML}}", tools_html)
    final_home = final_home.replace("{{ARCHIVE_HTML}}", archive_html)
    final_home = final_home.replace("{{JOB_TRACKER_HTML}}", "<div class='p-8 bg-blue-50 rounded-3xl border border-blue-100'><p class='text-blue-900 font-bold'>Tracking 245+ Autonomous Business Agents Live.</p></div>")
    
    (WEBSITE_DIR / "index.html").write_text(final_home)
    print(f"Production Build Complete: {len(stories)} articles, {len(tools)} tools published.")

if __name__ == "__main__":
    generate_site()
