import os
import re
from pathlib import Path

TEMPLATE_DIR = Path('/a0/usr/projects/x-manage/website/templates')
WEBSITE_DIR = Path('/a0/usr/projects/x-manage/website')
SRC_DIR = Path('/a0/usr/projects/x-manage/src')

master_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The AI Update | Practical AI for Business</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
        body { font-family: 'Space Grotesk', sans-serif; background-color: #020617; color: #f8fafc; }
        .neon-text { text-shadow: 0 0 10px rgba(34, 211, 238, 0.5); }
        .glass-card { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(12px); }
    </style>
</head>
<body class="bg-slate-950 text-slate-200 antialiased selection:bg-cyan-500 selection:text-slate-900">
    <nav class="max-w-7xl mx-auto px-6 py-6 flex justify-between items-center border-b border-slate-800/50">
        <div class="flex items-center space-x-4">
            <a href="/"><img src="img/logo.png" alt="The AI Update" class="h-12 object-contain drop-shadow-[0_0_8px_rgba(34,211,238,0.4)]"></a>
        </div>
        <div class="hidden md:flex space-x-8 font-semibold text-slate-400">
            <a href="#news" class="hover:text-cyan-400 transition">Intelligence Briefs</a>
            <a href="#" class="hover:text-cyan-400 transition">Free Toolkit</a>
            <a href="#" class="hover:text-cyan-400 transition">Sponsor</a>
            <a href="https://x.com/The_AIUpdate" target="_blank" class="hover:text-cyan-400 transition"><i class="fab fa-x-twitter text-xl"></i></a>
        </div>
    </nav>

    <header class="relative py-40 text-center overflow-hidden border-b border-slate-800">
        <div class="absolute inset-0 z-0 bg-cover bg-center opacity-30" style="background-image: url('img/banner.png');"></div>
        <div class="absolute inset-0 bg-gradient-to-b from-slate-950/40 to-slate-950 z-10"></div>
        <div class="relative z-20 max-w-4xl mx-auto px-6">
            <span class="px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-sm font-bold tracking-widest uppercase mb-8 inline-block shadow-[0_0_10px_rgba(34,211,238,0.2)]">Next-Gen Intelligence</span>
            <h1 class="text-5xl md:text-7xl font-bold mb-6 tracking-tighter text-white drop-shadow-lg">The <span class="text-cyan-400 neon-text">AI</span> Update</h1>
            <p class="text-xl text-slate-400 mb-10 font-light max-w-2xl mx-auto">High-signal, practical AI implementation guides for the modern enterprise. No hype, just ROI.</p>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-24 grid grid-cols-1 lg:grid-cols-3 gap-12" id="news">
        <div class="lg:col-span-2 space-y-8">
            <div class="flex items-center justify-between mb-8 border-b border-slate-800 pb-4">
                <h2 class="text-3xl font-bold text-white tracking-tight"><span class="text-cyan-400 mr-2">///</span> Latest Briefings</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {{NEWS_HTML}}
            </div>
        </div>
        <aside class="space-y-12">
            <div class="glass-card rounded-3xl p-8 border border-slate-800 shadow-xl">
                <h3 class="text-xl font-bold text-white mb-6 border-b border-slate-800 pb-4 flex items-center"><i class="fas fa-terminal text-cyan-400 mr-3"></i> Intelligence Archive</h3>
                <ul class="space-y-4 text-sm max-h-[700px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-slate-700">
                    {{ARCHIVE_HTML}}
                </ul>
            </div>
            {{JOB_TRACKER_HTML}}
        </aside>
    </main>

    <section class="border-t border-slate-800/80 bg-slate-900/40 relative">
        <div class="max-w-7xl mx-auto px-6 py-24">
            <div class="flex items-center justify-between mb-12">
                <h2 class="text-3xl font-bold text-white tracking-tight"><span class="text-cyan-400 mr-2">///</span> Top Free AI Tools</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {{TOOLS_HTML}}
            </div>
        </div>
    </section>

    <footer class="border-t border-slate-800 bg-slate-950 py-12 text-center text-slate-500 text-sm font-light">
        <p>&copy; 2026 The AI Update. Automated Intelligence.</p>
    </footer>
</body>
</html>
"""
(TEMPLATE_DIR / "master.html").write_text(master_html)

article_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} | The AI Update</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
        body { font-family: 'Space Grotesk', sans-serif; background-color: #020617; color: #f8fafc; }
    </style>
</head>
<body class="bg-slate-950 text-slate-200 antialiased selection:bg-cyan-500 selection:text-slate-900">
    <nav class="max-w-4xl mx-auto px-6 py-8 flex justify-between items-center border-b border-slate-800/50">
        <a href="/"><img src="../img/logo.png" alt="The AI Update" class="h-10 object-contain drop-shadow-[0_0_8px_rgba(34,211,238,0.4)]"></a>
        <a href="/" class="text-sm font-bold text-cyan-400 hover:text-cyan-300 tracking-widest uppercase transition-colors"><i class="fas fa-arrow-left mr-2"></i> Back to Hub</a>
    </nav>

    <article class="max-w-4xl mx-auto px-6 py-20">
        <header class="mb-16 border-b border-slate-800 pb-12">
            <div class="flex items-center space-x-4 mb-8">
                <span class="px-4 py-1.5 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-black rounded-full uppercase shadow-[0_0_10px_rgba(34,211,238,0.15)]">{{access_type}}</span>
                <span class="text-xs font-bold text-slate-500 uppercase tracking-widest"><i class="fas fa-satellite-dish mr-1 text-cyan-500/50"></i> {{source}}</span>
            </div>
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-black mb-6 tracking-tighter text-white leading-tight">{{title}}</h1>
        </header>

        <div class="prose prose-invert prose-cyan max-w-none text-lg text-slate-300 leading-relaxed font-light">
            {{content}}
        </div>
        
        <div class="mt-24 pt-12 border-t border-slate-800 text-center">
            <a href="{{url}}" target="_blank" class="inline-block px-10 py-5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black rounded-xl transition-all shadow-[0_0_20px_rgba(34,211,238,0.3)] hover:shadow-[0_0_30px_rgba(34,211,238,0.5)] uppercase tracking-widest">Verify Original Source <i class="fas fa-external-link-alt ml-2"></i></a>
        </div>
    </article>
</body>
</html>
"""
(TEMPLATE_DIR / "article.html").write_text(article_html)

sg_path = SRC_DIR / 'site_generator.py'
sg = sg_path.read_text()

sg = re.sub(
    r"news_html \+= f'<div class=\"bg-white.*?</div></div>'",
    r"news_html += f'<div class=\"bg-slate-900/50 p-8 rounded-[2rem] border border-slate-800 shadow-lg backdrop-blur-sm flex flex-col hover:border-cyan-400 hover:shadow-[0_0_20px_rgba(34,211,238,0.15)] transition-all group\"><div class=\"flex justify-between items-center mb-6\"><span class=\"text-[10px] font-bold text-slate-500 uppercase tracking-widest\">{clean_text(s.get(\"source\",\"\")).upper()}</span><span class=\"px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[8px] font-black rounded-full uppercase\">DEEP DIVE</span></div><h4 class=\"text-2xl font-black mb-4 leading-tight text-white group-hover:text-cyan-300 transition-colors\">{title}</h4><p class=\"text-slate-400 text-sm mb-8 font-light leading-relaxed\">{display_summary}</p><div class=\"mt-auto pt-5 border-t border-slate-800/50\"><a href=\"/articles/{aid}.html\" class=\"text-cyan-400 font-bold text-xs uppercase tracking-widest flex items-center group-hover:text-cyan-300\">Read Briefing <i class=\"fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform\"></i></a></div></div>'",
    sg
)

sg = re.sub(
    r"tools_html \+= f'<div class=\"bg-slate-800.*?</div>'",
    r"tools_html += f'<div class=\"bg-slate-900/80 p-8 rounded-2xl border border-slate-800 flex flex-col hover:border-cyan-500 hover:shadow-[0_0_15px_rgba(34,211,238,0.1)] transition-all\"><div class=\"flex justify-between items-center mb-5\"><h4 class=\"text-xl font-bold text-white\">{t_name}</h4><span class=\"px-2 py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[10px] font-black rounded uppercase\">{t_cat}</span></div><p class=\"text-slate-400 text-sm mb-8 font-light\">{t_desc}</p><a href=\"{t_url}\" target=\"_blank\" class=\"mt-auto text-cyan-400 font-bold text-xs uppercase tracking-widest hover:text-cyan-300 transition-colors\">Launch Tool &rarr;</a></div>'",
    sg
)

new_gen_content = '''def generate_content(title, summary, index, aid):
    import markdown
    md_path = DATA_DIR / f"research/briefings_2026_02/briefing_{aid}.md"
    if md_path.exists():
        md_text = md_path.read_text()
        html_content = markdown.markdown(md_text, extensions=['tables'])
        html_content = html_content.replace('<table>', '<div class="overflow-x-auto my-12"><table class="min-w-full bg-slate-900 shadow-xl rounded-xl overflow-hidden border border-slate-800">')
        html_content = html_content.replace('</table>', '</table></div>')
        html_content = html_content.replace('<thead>', '<thead class="bg-slate-950 border-b border-slate-800">')
        html_content = html_content.replace('<th>', '<th class="px-6 py-5 text-left text-xs font-black uppercase tracking-widest text-cyan-500">')
        html_content = html_content.replace('<td>', '<td class="px-6 py-4 border-t border-slate-800 text-slate-300 font-light">')
        html_content = html_content.replace('<blockquote>', '<blockquote class="border-l-4 border-cyan-500 pl-6 py-4 my-8 bg-cyan-900/10 text-cyan-100 italic rounded-r-lg shadow-inner">')
        html_content = html_content.replace('<h1>', '<h1 class="text-4xl md:text-5xl font-black mb-8 text-white tracking-tight">')
        html_content = html_content.replace('<h2>', '<h2 class="text-2xl md:text-3xl font-bold mt-16 mb-6 text-cyan-400 flex items-center tracking-tight"><span class="mr-4 text-cyan-500/30">//</span>')
        html_content = html_content.replace('<h3>', '<h3 class="text-xl font-bold mt-10 mb-4 text-white">')
        html_content = html_content.replace('<p>', '<p class="mb-8 text-lg text-slate-300 leading-relaxed font-light">')
        html_content = html_content.replace('<ul>', '<ul class="list-disc pl-6 mb-8 space-y-3 text-lg text-slate-300 font-light marker:text-cyan-500">')
        html_content = html_content.replace('<strong>', '<strong class="text-white font-bold">')
        return html_content
    else:
        return f"<p class='text-lg text-slate-400'>Content currently being compiled for {title}. Please check back shortly.</p>"'''

sg = re.sub(r"def generate_content\(title, summary, index, aid\):.*?return f\"<p class='text-lg'.*?shortly\.</p>\"", new_gen_content, sg, flags=re.DOTALL)
sg_path.write_text(sg)
