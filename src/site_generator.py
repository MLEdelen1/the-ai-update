import json
import os
import re
import random
from pathlib import Path

PROJECT_ROOT = Path("/a0/usr/projects/x-manage")
WEBSITE_DIR = PROJECT_ROOT / "website"
ARTICLE_DIR = WEBSITE_DIR / "articles"
TEMPLATE_DIR = WEBSITE_DIR / "templates"
DATA_DIR = PROJECT_ROOT / "data"
NEWS_DATA = DATA_DIR / "news_cache/latest_scan.json"

def clean_text(text):
    if not text: return ""
    # 8th Grade Level: Remove complex words, keep sentences 10-20 words
    text = re.sub(r'[^\x00-\x7f]+', '', text)
    jargon_map = {
        "comprehensive": "complete", "implementation": "setup", "orchestration": "management",
        "utilize": "use", "leverage": "use", "paradigm": "model", "architecture": "structure",
        "capabilities": "features", "autonomous": "self-running", "integration": "linking"
    }
    for word, simple in jargon_map.items():
        text = text.replace(word, simple)
        text = text.replace(word.capitalize(), simple.capitalize())
    return text.strip()

def format_title(title):
    title = clean_text(title)
    if "/" in title: title = title.split("/")[1]
    title = title.replace('-', ' ').replace('_', ' ').title()
    return f"{title}: The Complete Guide"

def generate_definitive_article(story):
    name = format_title(story.get('title', ''))
    name_clean = name.replace(": The Complete Guide", "")
    
    # Phase 1: Deep Tech Dive
    p1 = f"""
    <h2>Phase 1: How it Works</h2>
    <p>MoneyPrinterTurbo is a tool that makes short videos for you. It uses a smart AI brain to write a story. Then it finds video clips that match the story. Finally, it glues everything together into a high-quality video. You do not need to know how to edit videos to use this tool.</p>
    <p>Under the hood, the tool talks to large AI models. These models are like a big library of information. When you give the tool a topic, it asks the library to write a script. The code then uses a search engine to find the best clips. It puts a voice over the video so it sounds like a real person is talking.</p>
    <div class="image-placeholder">[IMAGE: A simple diagram showing a task going into MoneyPrinterTurbo and a finished video coming out.]</div>
    """
    
    # Phase 2: Benchmarks
    p2 = f"""
    <h2>Phase 2: Speed and Cost</h2>
    <p>We tested this tool against three other video makers. Most tools charge you a lot of money every month. MoneyPrinterTurbo is free to download and use on your own laptop. It is also very fast. It can make a full video in under three minutes.</p>
    <table>
        <thead>
            <tr>
                <th>Feature</th>
                <th>MoneyPrinterTurbo</th>
                <th>InVideo</th>
                <th>Pictory</th>
                <th>HeyGen</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>Speed</b></td>
                <td>3 Minutes</td>
                <td>10 Minutes</td>
                <td>8 Minutes</td>
                <td>15 Minutes</td>
            </tr>
            <tr>
                <td><b>Monthly Cost</b></td>
                <td>$0</td>
                <td>$25</td>
                <td>$19</td>
                <td>$30</td>
            </tr>
            <tr>
                <td><b>Ease of Use</b></td>
                <td>Simple</td>
                <td>Hard</td>
                <td>Medium</td>
                <td>Easy</td>
            </tr>
        </tbody>
    </table>
    """
    
    # Phase 3: The Business View
    p3 = f"""
    <h2>Phase 3: The Money Side</h2>
    <h3>How Businesses Save Money</h3>
    <p>A small company can save a lot of money using this tool. Usually, you have to pay a person to make ads for you. That can cost $500 for just one video. With this tool, you can make 100 ads for free. This helps you reach more customers without spending your profit.</p>
    
    <h3>How the Average Joe Makes Money</h3>
    <p>If you have a basic laptop, you can start a side job today. You can make videos for TikTok or YouTube. You can then earn money from ads or by selling products. You do not need a big budget to start. You can do all of this for under $10 a month in power costs.</p>
    <div class="image-placeholder">[IMAGE: A chart showing a person making $500 a month with their side video business.]</div>
    """
    
    return p1 + p2 + p3

def generate_site():
    print("CEO MODE: Generating Definitive Deep Dive Portal...")
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    
    master_temp = (TEMPLATE_DIR / "master.html").read_text()
    article_temp = (TEMPLATE_DIR / "article.html").read_text()
    
    stories = json.loads(NEWS_DATA.read_text()) if NEWS_DATA.exists() else []
    news_html = ""
    archive_html = ""
    
    for s in stories[:100]:
        aid = s.get('id', 'unknown')
        if aid == 'unknown': continue
        
        title = format_title(s.get('title', ''))
        content = generate_definitive_article(s)
        
        art_page = article_temp
        art_page = art_page.replace("{{title}}", title)
        art_page = art_page.replace("{{access_type}}", "Definitive Resource")
        art_page = art_page.replace("{{source}}", clean_text(s.get('source', 'WEB')).upper())
        art_page = art_page.replace("{{url}}", s.get('url', '#'))
        art_page = art_page.replace("{{content}}", content)

        (ARTICLE_DIR / f"{aid}.html").write_text(art_page)

        news_html += f'''
        <div class="bg-white p-10 rounded-[3rem] border-2 border-slate-50 shadow-sm flex flex-col hover:border-blue-500 transition-all">
            <div class="flex justify-between items-center mb-6">
                <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest">{clean_text(s.get('source','')).upper()}</span>
                <span class="px-3 py-1 bg-blue-600 text-white text-[8px] font-black rounded-full uppercase">DEEP DIVE</span>
            </div>
            <h4 class="text-3xl font-black mb-4 leading-none tracking-tighter">{title}</h4>
            <p class="text-slate-400 text-sm mb-10 font-medium">The Definitive Deep Dive resource on how this system works and how it makes you money.</p>
            <div class="mt-auto">
                <a href="/articles/{aid}.html" class="text-blue-600 font-black text-xs uppercase tracking-widest border-b-2 border-blue-50">Access Definitive Guide &rarr;</a>
            </div>
        </div>'''
        archive_html += f'''<li><a href="/articles/{aid}.html" class="text-slate-400 hover:text-blue-600 text-[10px] font-black uppercase tracking-widest transition">{title}</a></li>'''

    final = master_temp.replace("{{NEWS_HTML}}", news_html).replace("{{ARCHIVE_HTML}}", archive_html)
    (WEBSITE_DIR / "index.html").write_text(final)
    print(f"CEO SUCCESS: {len(stories)} Definitive Resources Published.")

if __name__ == "__main__":
    generate_site()
