#!/usr/bin/env python3
import json
import os
from pathlib import Path

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
WEBSITE_DIR = PROJECT_ROOT / "website"
ARTICLE_DIR = WEBSITE_DIR / "articles"
TEMPLATE_DIR = WEBSITE_DIR / "templates"
DATA_DIR = PROJECT_ROOT / "data"
NEWS_DATA = DATA_DIR / "news_cache/latest_scan.json"

def generate_svg_chart(value, label="Power"):
    return f'''
    <svg viewBox="0 0 100 25" class="w-full">
        <rect width="100" height="20" rx="10" fill="#ffffff33" />
        <rect width="{value}" height="20" rx="10" fill="#ffffff" />
        <text x="5" y="13" font-family="Inter, sans-serif" font-weight="900" font-size="7" fill="#1e40af">{value}% {label.upper()}</text>
    </svg>'''

def generate_site():
    print("Generating High-End Journalism Portal...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()

    stories = json.loads(NEWS_DATA.read_text())
    news_html = ""

    for s in stories:
        aid = s['id']
        local_link = f"/articles/{aid}.html"
        
        # Mapping Complex Fields
        cap_html = "".join([f'<li class="flex items-start gap-3 text-xs font-bold text-slate-600"><span class="text-blue-500 mt-1">●</span>{c}</li>' for c in s.get('capabilities', [])])
        use_html = "".join([f'<div class="p-6 bg-slate-50 rounded-2xl border border-slate-100"><p class="text-base font-bold text-slate-800">{u}</p></div>' for u in s.get('practical_use_cases', [])])
        chart_svg = generate_svg_chart(s.get('benchmark_data', 80))
        
        # Build Article
        art_page = article_temp.replace("{{title}}", s['title'])
        art_page = art_page.replace("{{source}}", s['source'])
        art_page = art_page.replace("{{url}}", s['url'])
        art_page = art_page.replace("{{access_type}}", s['access_type'])
        art_page = art_page.replace("{{capabilities_list}}", cap_html)
        art_page = art_page.replace("{{use_cases}}", use_html)
        art_page = art_page.replace("{{chart_svg}}", chart_svg)
        art_page = art_page.replace("{{content}}", s['executive_summary'].replace('\n', '<br><br>'))
        
        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)

        # Homepage Card
        news_html += f'''
        <div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm hover:shadow-xl transition-all group flex flex-col">
            <div class="flex justify-between items-start mb-6">
                <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{s['source']}</span>
                <span class="py-1 px-3 bg-blue-50 text-blue-600 text-[8px] font-black rounded-full uppercase">{s['access_type']}</span>
            </div>
            <h4 class="text-2xl font-black mb-4 group-hover:text-blue-600 transition">{s['title']}</h4>
            <p class="text-slate-500 text-sm mb-8 leading-relaxed">{s['executive_summary'][:160]}...</p>
            <div class="mt-auto">
                <a href="{local_link}" class="inline-flex items-center gap-2 text-blue-600 font-black text-sm uppercase tracking-tighter">Full Intelligence &rarr;</a>
            </div>
        </div>'''

    final_home = master_temp.replace("{{NEWS_HTML}}", news_html).replace("<!-- NEWS_INJECTION -->", news_html)
    (WEBSITE_DIR / "index.html").write_text(final_home)
    print(f"Deployment successful. {len(stories)} technical briefings published.")

if __name__ == "__main__":
    generate_site()
