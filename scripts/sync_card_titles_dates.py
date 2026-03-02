from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

base = Path(r"C:/Users/MLEde/.openclaw/workspace/business/the-ai-update-repo/website")
article_dir = base / "articles"

article_meta = {}
for ap in article_dir.glob("*.html"):
    try:
        s = BeautifulSoup(ap.read_text(encoding="utf-8"), "html.parser")
        h1 = s.find("h1")
        title = h1.get_text(" ", strip=True) if h1 else (s.title.get_text(" ", strip=True) if s.title else ap.stem)
        dt = datetime.fromtimestamp(ap.stat().st_mtime)
        article_meta[ap.name] = {"title": title, "date": dt.strftime("%b %d, %Y").replace(" 0", " ")}
    except Exception:
        continue

changed = []
for page in base.rglob("*.html"):
    if page.parent == article_dir:
        continue

    soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
    page_changed = False
    processed_cards = set()

    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "articles/" not in href or not href.endswith(".html"):
            continue

        fname = href.split("articles/")[-1].split("?")[0].split("#")[0]
        if "/" in fname:
            fname = fname.split("/")[-1]
        meta = article_meta.get(fname)
        if not meta:
            continue

        card = None
        for anc in [a] + list(a.parents):
            if getattr(anc, "name", None) in ("article", "a", "div", "li", "section") and anc.find("h3"):
                card = anc
                break
        if card is None:
            continue

        card_key = str(card)
        if card_key in processed_cards:
            continue
        processed_cards.add(card_key)

        h3 = card.find("h3")
        if h3 and h3.get_text(" ", strip=True) != meta["title"]:
            h3.clear()
            h3.append(meta["title"])
            page_changed = True

        existing_date = card.find(class_="card-date")
        desired = f"Published {meta['date']}"
        if existing_date:
            if existing_date.get_text(" ", strip=True) != desired:
                existing_date.clear()
                existing_date.append(desired)
                page_changed = True
        else:
            d = soup.new_tag("div", attrs={"class": "card-date"})
            d.append(desired)
            if h3:
                h3.insert_after(d)
            else:
                card.insert(0, d)
            page_changed = True

    if page_changed:
        page.write_text(str(soup), encoding="utf-8")
        changed.append(str(page.relative_to(base)).replace("\\", "/"))

print("\n".join(changed))
print(f"TOTAL_CHANGED={len(changed)}")
