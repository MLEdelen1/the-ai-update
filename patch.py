import os
with open('/a0/usr/projects/x-manage/src/site_generator.py', 'r') as f:
    content = f.read()

idx = content.find('def generate_site():')
top_part = content[:idx]

new_gen = '''def generate_site():
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
            lines = md_text.split('\n')
            
            # 1. Grab EXACT title from the markdown file
            for line in lines:
                if line.startswith('# '):
                    title = clean_text(line.replace('# ', ''))
                    break
            
            # 2. Grab real summary from the first paragraph if missing
            if len(summary) < 20:
                for line in lines:
                    cl = line.strip()
                    if cl and not cl.startswith('#') and len(cl) > 30:
                        summary = clean_text(cl)
                        break
                        
        display_summary = summary[:130] + "..." if len(summary) > 130 else summary
        
        content = generate_content(title, summary, i, aid)
        
        # Article page gets exact title
        art_page = article_temp.replace("{{title}}", title)
        art_page = art_page.replace("{{access_type}}", "Technical Brief")
        art_page = art_page.replace("{{source}}", clean_text(s.get('source', 'WEB')).upper())
        art_page = art_page.replace("{{url}}", s.get('url', '#'))
        art_page = art_page.replace("{{content}}", content)
        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)
        
        # Homepage card gets exact title & real overview
        news_html += f'<div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm flex flex-col hover:border-blue-400 transition-all"><div class="flex justify-between items-center mb-6"><span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{clean_text(s.get("source","")).upper()}</span><span class="px-3 py-1 bg-blue-600 text-white text-[8px] font-black rounded-full uppercase">DEEP DIVE</span></div><h4 class="text-2xl font-black mb-4 leading-none">{title}</h4><p class="text-slate-500 text-sm mb-10 font-medium">{display_summary}</p><div class="mt-auto"><a href="/articles/{aid}.html" class="text-blue-600 font-bold text-xs uppercase tracking-widest border-b-2 border-blue-50">Read Comprehensive Resource &rarr;</a></div></div>'
        
        archive_html += f'<li><a href="/articles/{aid}.html" class="text-slate-500 hover:text-blue-600 transition-colors">{title}</a></li>'

    final = master_temp.replace("{{NEWS_HTML}}", news_html).replace("{{ARCHIVE_HTML}}", archive_html)
    (WEBSITE_DIR / "index.html").write_text(final)

if __name__ == "__main__":
    generate_site()
'''

with open('/a0/usr/projects/x-manage/src/site_generator.py', 'w') as f:
    f.write(top_part + new_gen)
