import os

path = '/a0/usr/projects/x-manage/src/site_generator.py'
with open(path, 'r') as f:
    content = f.read()

idx = content.find('def generate_site():')
if idx != -1:
    top = content[:idx]
else:
    top = content

new_func = """def generate_site():
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
            import json
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
"""

with open(path, 'w') as f:
    f.write(top + new_func)
