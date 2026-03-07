import json, re
from pathlib import Path
from datetime import datetime, timezone
import sys

ROOT = Path('C:/Users/MLEde/.openclaw/workspace/business/the-ai-update-repo')
BRIEF_DIR = ROOT / 'data/research/briefings_2026_02'
ART_DIR = ROOT / 'website/articles'
ARTICLES_INDEX = ROOT / 'website/articles.html'
ARCHIVE = ROOT / 'website/archive.html'
REPORT = ROOT / 'data/reports/topic_audit_site.json'

ALLOW_PATTERNS = [r'\b(llm|large language model|reasoning model|reasoning ai|inference model|agentic ai|ai agent|foundation model)\b',r'\b(text[- ]to[- ]image|image generation|diffusion|text[- ]to[- ]video|video generation|music generation|ai music|suno|udio|runway|kling|sora|luma|midjourney|stable diffusion)\b',r'\b(openai|anthropic|gemini|claude|deepseek|llama|mistral|hugging ?face|copilot|notebooklm|perplexity|ollama)\b',r'\b(ai tool|ai platform|model update|model release|model launch|api update|artificial intelligence|machine learning|generative ai)\b']
CONCRETE_PATTERNS = [r'\b(openai|anthropic|gemini|claude|deepseek|llama|mistral|gpt|o1|o3|r1|qwen|midjourney|runway|suno|udio|kling|sora|ollama|notebooklm|openclaw|copilot|perplexity|stability ai)\b',r'\b(reasoning model|llm|text[- ]to[- ]image|text[- ]to[- ]video|music generation|image generation|video generation|diffusion|model (update|release|launch))\b']
OFFTOPIC_PATTERNS = [r'\b(bra|bras|lingerie|fashion)\b',r'\b(murder|mass shooting|homicide|crime|police blotter)\b',r'\b(pope|homil(?:y|ies)|religion)\b']
WEAK_GENERIC_PATTERNS = [r'\b(productivity revolution|extreme roi|economic growth|economy|fighting ai slop|investor loyalty|consultants?)\b']

def classify_text(title: str, content: str):
    text = f"{title}\n{content}".lower()
    if not any(re.search(p, text, re.I) for p in ALLOW_PATTERNS):
        return False, 'no_allowed_ai_topic'
    if any(re.search(p, text, re.I) for p in OFFTOPIC_PATTERNS):
        return False, 'offtopic_domain'
    concrete = any(re.search(p, text, re.I) for p in CONCRETE_PATTERNS)
    weak = any(re.search(p, text, re.I) for p in WEAK_GENERIC_PATTERNS)
    if weak and not concrete:
        return False, 'weak_generic_ai'
    return True, 'allowed_ai_topic'

def title_from_md(text: str, fallback: str):
    for ln in text.splitlines():
        if ln.strip().startswith('# '):
            return ln.strip()[2:].strip()
    return fallback

def render_articles_html(items):
    cards = []
    for it in items:
        aid = it['id']; title = it['title']; date = it.get('published',''); reason = it['reason']
        cards.append(f'<article class="tool"><div class="tool-cat">AI</div><h3>{title}</h3><div class="card-date">{date}</div><p>{reason.replace("_"," ")}</p><a class="tool-link" href="articles/{aid}.html">Read full article &rarr;</a></article>')
    cards_html = ''.join(cards)
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><title>Articles | The AI Update</title><link href="./styles.css?v=14" rel="stylesheet"/></head><body><canvas id="particles"></canvas><div class="top-glow"></div><nav id="nav"><div class="nav-wrap"><a class="logo-group" href="./index.html"><img alt="" class="logo-img" src="./assets/logo.png"/><div class="logo-text">THE AI<span class="logo-accent">UPDATE</span></div></a><div class="nav-links" id="navLinks"><a href="./intel.html">Latest Intel</a><a href="./workflows.html">Workflows</a><a href="./tools.html">Tools</a><a href="./guides/index.html">Guides</a><a href="./articles.html">Articles</a><a href="./resources.html">Resources</a><a class="nav-btn" href="./starter-kit.html">Get Free Kit</a></div><button class="burger" onclick="document.getElementById('navLinks').classList.toggle('show')"><span></span><span></span><span></span></button></div></nav><main class="articles-index"><div class="sect-head"><p class="tag">ARTICLES</p><h1>AI-only published articles</h1><p class="sect-sub">Filtered to LLMs, reasoning models, generation models, and AI tools/platform updates.</p></div><section class="sect" style="padding-top:12px; padding-bottom:28px;"><div class="sect-head"><p class="tag">AI TOPICS</p><h2>Current AI archive</h2></div><section class="articles-grid">{cards_html}</section></section><p class="article-cta"><a class="btn-main" href="guides/index.html">Start with the beginner roadmap</a></p></main><footer><div class="contain foot-inner"><div class="foot-brand"><img alt="" class="foot-logo" src="./assets/logo.png"/><span>THE AI UPDATE</span></div><div class="foot-links"><a href="./index.html">Home</a><a href="./guides/index.html">Guides</a><a href="./articles.html">Articles</a><a href="./tools.html">Tools</a><a href="./resources.html">Resources</a><a href="./starter-kit.html">Starter Kit</a></div></div></footer><script src="./site.js?v=14"></script></body></html>'''

report = {'timestamp_utc': datetime.now(timezone.utc).isoformat(),'rules': {'allow_only': ['LLMs','reasoning models','image/music/video generation','AI tools/platform/model updates'],'remove': ['non-AI','weakly-related generic content']},'scanned': {'briefings': 0, 'article_pages': 0, 'articles_index': str(ARTICLES_INDEX), 'archive_page': str(ARCHIVE)},'kept': {'briefings': [], 'article_pages': []},'removed': {'briefings': [], 'article_pages': []},'d292ba3ac0bc': {}}
briefing_class = {}
for md in sorted(BRIEF_DIR.glob('briefing_*.md')):
    text = md.read_text(encoding='utf-8', errors='ignore')
    aid = md.stem.replace('briefing_', '')
    title = title_from_md(text, aid)
    keep, reason = classify_text(title, text)
    briefing_class[aid] = {'id': aid, 'path': str(md), 'title': title, 'keep': keep, 'reason': reason}
    report['scanned']['briefings'] += 1

for aid, row in briefing_class.items():
    target = {'id': aid, 'path': row['path'], 'reason': row['reason'], 'title': row['title']}
    if row['keep']:
        report['kept']['briefings'].append(target)
    else:
        Path(row['path']).unlink(missing_ok=True)
        report['removed']['briefings'].append(target)

for html in sorted(ART_DIR.glob('*.html')):
    aid = html.stem
    html_text = html.read_text(encoding='utf-8', errors='ignore')
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>|<title[^>]*>(.*?)</title>', html_text, re.I|re.S)
    title = (title_match.group(1) or title_match.group(2)).strip() if title_match else aid
    if aid in briefing_class:
        keep = briefing_class[aid]['keep']; reason = briefing_class[aid]['reason']
    else:
        keep, reason = classify_text(title, re.sub(r'<[^>]+>', ' ', html_text))
    report['scanned']['article_pages'] += 1
    target = {'id': aid, 'path': str(html), 'reason': reason, 'title': title}
    if keep:
        report['kept']['article_pages'].append(target)
    else:
        html.unlink(missing_ok=True)
        report['removed']['article_pages'].append(target)

id_target = 'd292ba3ac0bc'
brief_path = BRIEF_DIR / f'briefing_{id_target}.md'
html_path = ART_DIR / f'{id_target}.html'
report['d292ba3ac0bc'] = {'briefing_exists': brief_path.exists(),'article_page_exists': html_path.exists(),'status': 'not_found_in_scope','action': 'none_required'}

sys.path.insert(0, str(ROOT / 'src'))
from site_generator import generate_site
generate_site()

remaining = []
for md in sorted(BRIEF_DIR.glob('briefing_*.md'), key=lambda p: p.stat().st_mtime, reverse=True):
    aid = md.stem.replace('briefing_','')
    txt = md.read_text(encoding='utf-8', errors='ignore')
    t = title_from_md(txt, aid)
    keep, reason = classify_text(t, txt)
    if keep:
        dt = datetime.fromtimestamp(md.stat().st_mtime)
        remaining.append({'id': aid, 'title': t, 'reason': reason, 'published': dt.strftime('Published %b %d, %Y')})

ARTICLES_INDEX.write_text(render_articles_html(remaining), encoding='utf-8')

report['counts'] = {'briefings_scanned': report['scanned']['briefings'],'briefings_kept': len(report['kept']['briefings']),'briefings_removed': len(report['removed']['briefings']),'article_pages_scanned': report['scanned']['article_pages'],'article_pages_kept': len(report['kept']['article_pages']),'article_pages_removed': len(report['removed']['article_pages']),'articles_index_regenerated': True,'archive_regenerated': True}
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report['counts'], indent=2))
