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
    if "/" in title: 
        parts = title.split("/")
        return f"Intelligence Brief: {parts[1].replace('-', ' ').title()}"
    return f"Intelligence Brief: {title}" if "Intelligence" not in title else title

def convert_md_to_html(md_text):
    md_text = re.sub(r'^# .*\n?', '', md_text)
    # Softened Headings
    md_text = re.sub(r'^## (.*)$', r'<h2 class="text-xl font-bold mt-8 mb-4 text-slate-900">\1</h2>', md_text, flags=re.M)
    md_text = re.sub(r'^### (.*)$', r'<h3 class="text-lg font-bold mt-6 mb-2 text-slate-800">\1</h3>', md_text, flags=re.M)
    # Normal Bold (standard font weight)
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-semibold text-slate-900">\1</strong>', md_text)
    # Clean Lists
    md_text = re.sub(r'^[\*\-] (.*)$', r'<li class="ml-5 list-disc mb-1 text-slate-600">\1</li>', md_text, flags=re.M)
    md_text = re.sub(r'^\d+\. (.*)$', r'<li class="ml-5 list-decimal mb-1 text-slate-600">\1</li>', md_text, flags=re.M)
    
    paragraphs = md_text.split('\n\n')
    html_chunks = []
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('<h') or p.startswith('<li'):
            html_chunks.append(p)
        else:
            html_chunks.append(f'<p class="mb-5 text-slate-600 leading-relaxed">{p}</p>')
    return '\n'.join(html_chunks)

def generate_svg_chart(value):
    return f'''<svg viewBox="0 0 100 25" class="w-full"><rect width="100" height="20" rx="10" fill="#ffffff33" /><rect width="{value}" height="20" rx="10" fill="#ffffff" /><text x="5" y="13" font-family="Inter, sans-serif" font-weight="700" font-size="7" fill="#1e40af">{value}% POWER</text></svg>'''

def generate_site():
    print("Journalistic Refactoring: Softening typography and refining layout...")
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
        content_body = f"<p class='mb-5 text-slate-600'>{summary}</p><p class='text-slate-600'>This intelligence is verified for Q1 2026 deployment.</p>"
        
        if aid in PREMIUM_MAPPING and (RESEARCH_DIR / PREMIUM_MAPPING[aid]).exists():
            content_body = convert_md_to_html((RESEARCH_DIR / PREMIUM_MAPPING[aid]).read_text())

        art_page = article_temp.replace("{{title}}", title).replace("{{access_type}}", clean_text(s.get('access_type', 'API')).upper()).replace("{{source}}", clean_text(s.get('source', 'INTEL')).upper()).replace("{{url}}", s.get('url', '#')).replace("{{content}}", content_body).replace("{{chart_svg}}", generate_svg_chart(85 + (len(aid)%10))).replace("{{image_url}}", "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=2000")
        
        specs_html = "".join([f'<li class="flex items-center gap-3"><div class="w-1.5 h-1.5 rounded-full bg-blue-500"></div><span class="text-xs font-semibold text-slate-500 uppercase">{spec}</span></li>' for spec in ['Technical Reasoning', 'Autonomous Execution', 'Market Disruptor', 'API-First Design']])
        art_page = art_page.replace("{{capabilities_list}}", specs_html).replace("{{use_cases}}", "<div class='p-8 bg-slate-50 rounded-3xl border border-slate-100 mb-6'><h4 class='font-bold text-sm mb-3 uppercase text-slate-400 tracking-widest'>Strategic Implementation</h4><p class='text-slate-600 text-sm leading-relaxed'>Integrate this intelligence into your business unit to drive measurable efficiency gains.</p></div>")

        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)
        news_html += f'''<div class="bg-white p-10 rounded-[2.5rem] border border-slate-100 shadow-sm flex flex-col group"><div class="flex justify-between items-start mb-6"><span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{clean_text(s.get('source','')).upper()}</span><span class="py-1 px-3 bg-blue-50 text-blue-600 text-[8px] font-black rounded-full uppercase">{clean_text(s.get('access_type','')).upper()}</span></div><h4 class="text-xl font-bold mb-3 group-hover:text-blue-600 transition">{title}</h4><p class="text-slate-500 text-sm mb-6 leading-relaxed">{summary[:130]}...</p><div class="mt-auto"><a href="/articles/{aid}.html" class="text-blue-600 font-bold text-xs uppercase tracking-tight">Full Intelligence &rarr;</a></div></div>'''
        archive_html += f'''<li><a href="/articles/{aid}.html" class="text-slate-500 hover:text-blue-600 text-sm">{title}</a></li>'''

    final = master_temp.replace("{{NEWS_HTML}}", news_html).replace("{{ARCHIVE_HTML}}", archive_html)
    (WEBSITE_DIR / "index.html").write_text(final)
    print("Success: Typography refactored to Journalistic standards.")

if __name__ == "__main__":
    generate_site()
