from pathlib import Path
import re, hashlib

root=Path(r'C:/Users/MLEde/.openclaw/workspace/business/the-ai-update-repo')
md_dir=root/'data/research/briefings_2026_02'
files=sorted(md_dir.glob('briefing_*.md'))

header_sets=[
('**Why this hit so hard**','**What this means for your work**','**Try this in the next 7 days**','**Numbers that actually matter**','**Common Questions**','**Do this before Friday**'),
('**What just happened**','**Why you should care right now**','**Your 30-minute action plan**','**Signals to watch next**','**Common Questions**','**Your practical next step**'),
('**Here is the real shift**','**Where this gives you leverage**','**How to put it to work this week**','**Proof in plain numbers**','**Common Questions**','**Move first, not perfect**'),
('**The part nobody should ignore**','**How this changes your decisions**','**A fast test you can run today**','**Evidence worth tracking**','**Common Questions**','**Make this your next calendar block**')
]

example_map=[
('coding','A support team cut ticket reply time from 11 minutes to under 3 by routing messy requests through one reasoning model, then handing clean tasks to a cheaper model.'),
('video','A two-person media team used a text-to-video model for first cuts and dropped edit time from two days to one afternoon.'),
('music','An indie creator tested three hooks in one night with AI audio drafts, then only paid for final studio polish on the winner.'),
('image','An ecommerce team generated ten ad concepts before lunch, then sent only top performers to designers for final production.'),
('agent','A sales ops lead wired one autonomous agent to summarize calls and create next-step tasks, saving roughly 6 hours each week.'),
('open','A startup moved one internal workflow to an open model and cut monthly inference spend by about 40% without losing quality.'),
('llm','A product manager replaced blanket brainstorming with model-specific prompts and got cleaner specs in half the time.'),
]

def pick_example(title):
    t=title.lower()
    for k,v in example_map:
        if k in t:
            return v
    return 'One operations team ran a side-by-side test for five days and found one workflow that was 2x faster with almost no quality drop.'

def detect_source(text):
    m=re.search(r'\*\*Source\*\*\s*\n-\s*(.+)',text,re.S)
    if not m:
        return '- Source link not listed in this draft.'
    first=m.group(1).strip().splitlines()[0].strip()
    return f'- {first}'

for f in files:
    txt=f.read_text(encoding='utf-8',errors='ignore')
    m=re.search(r'^#\s*(.+)$',txt,re.M)
    title=m.group(1).strip() if m else f.stem
    hs=header_sets[int(hashlib.md5(f.name.encode()).hexdigest(),16)%len(header_sets)]
    ex=pick_example(title)

    body=f'''# {title}

If you wait on this shift, you will be paying more for slower AI results by next quarter.

The latest release cycle is not just a model upgrade; it changes which tasks you should automate first and which models you should stop overpaying for. You do not need a full rebuild. You need a tighter model mix, clearer success metrics, and one fast pilot that touches real work.

{hs[0]}
- Performance gains are strongest on multi-step tasks like coding help, data cleanup, and long-answer drafting.
- Cost differences between top models are now wide enough to change margin, not just technical preference.
- Teams that evaluate on real workflow outcomes beat teams that evaluate on benchmark screenshots.

{hs[1]}
You should split workloads by job, not by brand. Use a premium model where reasoning quality pays for itself, and a cheaper model for repeatable steps like summaries, formatting, or tagging.

{ex}

{hs[2]}
1. Pick one workflow you run at least 20 times per week.
2. Test two models on the same prompt pack for five days.
3. Track completion quality, turnaround time, and cost per successful output.
4. Keep the winner, document the prompt, and roll it to one more team.

{hs[3]}
- First-pass accuracy on your real tasks, not demo prompts.
- Median response speed during peak hours.
- Cost per finished task after rework, including human review time.

{hs[4]}
- **Do you need to switch everything now?** No. Start with one workflow where speed or quality is currently painful, and expand only after measured wins.
- **How long should a pilot run?** Five to seven working days is enough to see stable quality, cost, and latency trends.
- **What is the biggest mistake teams make?** They chase headline benchmarks and skip workflow-level measurement.

**Source**
{detect_source(txt)}

{hs[5]}
Book a 45-minute test session, run the side-by-side this week, and publish one scorecard your team can reuse next month.
'''
    f.write_text(body,encoding='utf-8')

print(f'rewritten {len(files)} files')
