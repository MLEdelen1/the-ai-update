from pathlib import Path
import json,re

root=Path(r'C:/Users/MLEde/.openclaw/workspace/business/the-ai-update-repo')
md_files=sorted((root/'data/research/briefings_2026_02').glob('briefing_*.md'))
html_files=sorted((root/'website/articles').glob('*.html'))
phrases=['The quick take','What changed and why it matters','How to use this this week','Proof points worth tracking','Your next move']
checks=[]
failed=[]
for p in phrases:
    md_hits=sum(f.read_text(encoding='utf-8',errors='ignore').count(p) for f in md_files)
    html_hits=sum(f.read_text(encoding='utf-8',errors='ignore').count(p) for f in html_files)
    item={'phrase':p,'md_hits':md_hits,'html_hits':html_hits,'total_hits':md_hits+html_hits}
    checks.append(item)
    if item['total_hits']!=0:
        failed.append(item)

samples=[]
for f in html_files[:3]:
    t=f.read_text(encoding='utf-8',errors='ignore')
    p=re.search(r'<p>(.*?)</p>',t,re.S)
    first_para=re.sub('<[^<]+?>','',p.group(1)).strip() if p else ''
    samples.append({'file':f.name,'first_paragraph':first_para[:180]})

report={
    'rewritten_markdown_count':len(md_files),
    'generated_article_html_count':len(html_files),
    'forbidden_phrase_checks':checks,
    'failed_checks_count':len(failed),
    'failed_checks':failed,
    'sample_page_verification':samples
}
out=root/'data/reports/article_style_overhaul_v2.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(f'Wrote {out}')
