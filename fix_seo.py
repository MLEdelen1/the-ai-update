import os
import re
from pathlib import Path

# 1. Rollback to the clean dark theme commit
os.system('cd /a0/usr/projects/x-manage && git reset --hard c501a90')

# 2. Update Master HTML with SEO
master_path = Path('/a0/usr/projects/x-manage/website/templates/master.html')
master = master_path.read_text()
seo_master = '''<meta name="description" content="High-signal, practical AI implementation guides for the modern enterprise. No hype, just ROI.">
    <meta name="keywords" content="AI news, Artificial Intelligence, AI implementation, AI for business, Machine Learning, AI tools">
    <link rel="canonical" href="https://theaiupdate.org/">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:title" content="The AI Update | Practical AI for Business">
    <meta property="og:description" content="High-signal, practical AI implementation guides for the modern enterprise. No hype, just ROI.">
    <meta property="og:url" content="https://theaiupdate.org/">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://theaiupdate.org/img/banner.png">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@The_AIUpdate">
    <meta name="twitter:title" content="The AI Update | Practical AI for Business">
    <meta name="twitter:description" content="High-signal, practical AI implementation guides for the modern enterprise.">
    <meta name="twitter:image" content="https://theaiupdate.org/img/banner.png">
    
    <!-- JSON-LD Schema -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "The AI Update",
      "url": "https://theaiupdate.org/"
    }
    </script>
    <title>The AI Update | Practical AI for Business</title>'''
master = re.sub(r'<title>.*?</title>', seo_master, master, flags=re.DOTALL)
master_path.write_text(master)

# 3. Update Article HTML with SEO
article_path = Path('/a0/usr/projects/x-manage/website/templates/article.html')
article = article_path.read_text()
seo_article = '''<meta name="description" content="{{description}}">
    <link rel="canonical" href="{{url_full}}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:title" content="{{title}} | The AI Update">
    <meta property="og:description" content="{{description}}">
    <meta property="og:url" content="{{url_full}}">
    <meta property="og:type" content="article">
    <meta property="og:image" content="https://theaiupdate.org/img/banner.png">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@The_AIUpdate">
    <meta name="twitter:title" content="{{title}} | The AI Update">
    <meta name="twitter:description" content="{{description}}">
    <meta name="twitter:image" content="https://theaiupdate.org/img/banner.png">
    
    <!-- JSON-LD Schema -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{{title}}",
      "description": "{{description}}",
      "image": "https://theaiupdate.org/img/banner.png",
      "publisher": {
        "@type": "Organization",
        "name": "The AI Update",
        "logo": {
          "@type": "ImageObject",
          "url": "https://theaiupdate.org/img/logo.png"
        }
      }
    }
    </script>
    <title>{{title}} | The AI Update</title>'''
article = re.sub(r'<title>.*?</title>', seo_article, article, flags=re.DOTALL)
article_path.write_text(article)

# 4. Safely Patch site_generator.py line by line
sg_path = '/a0/usr/projects/x-manage/src/site_generator.py'
with open(sg_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'art_page = art_page.replace("{{content}}", content)' in line:
        new_lines.append(line)
        new_lines.append('        safe_desc = display_summary.replace("\\"", "&quot;")\n')
        new_lines.append('        art_page = art_page.replace("{{description}}", safe_desc)\n')
        new_lines.append('        art_page = art_page.replace("{{url_full}}", f"https://theaiupdate.org/articles/{aid}.html")\n')
    elif 'final = master_temp.replace' in line:
        sitemap_code = """
    # Generate Sitemap and robots.txt
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += '  <url>\n    <loc>https://theaiupdate.org/</loc>\n    <changefreq>hourly</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
    for s in DATA:
        if s.get("id"):
            sm += f'  <url>\n    <loc>https://theaiupdate.org/articles/{s.get("id")}.html</loc>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    sm += '</urlset>'
    (WEBSITE_DIR / "sitemap.xml").write_text(sm)
    (WEBSITE_DIR / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://theaiupdate.org/sitemap.xml")
"""
        new_lines.append(sitemap_code)
        new_lines.append(line)
    else:
        new_lines.append(line)

with open(sg_path, 'w') as f:
    f.writelines(new_lines)
