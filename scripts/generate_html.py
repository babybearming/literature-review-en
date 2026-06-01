# -*- coding: utf-8 -*-
import json
import html
from pathlib import Path

def escape(text):
    if text is None:
        return ""
    return html.escape(str(text))

def format_authors(authors):
    if not authors:
        return "未知作者"
    if len(authors) <= 3:
        return ", ".join(authors)
    return ", ".join(authors[:3]) + " et al."

def format_apa(paper):
    authors = format_authors(paper.get("authors", []))
    year = paper.get("year", "n.d.")
    title = paper.get("title_en", "Unknown Title")
    venue = paper.get("venue", "")
    doi = paper.get("doi", "")
    
    apa = f"{authors} ({year}). {title}."
    if venue:
        apa += f" {venue}."
    if doi:
        apa += f" https://doi.org/{doi.split(\'/\')[-1]}"
    return apa

def generate_sidebar(papers):
    categories = {}
    for p in papers:
        cat = p.get("category", "其他")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)
    
    html_cats = []
    for cat, items in sorted(categories.items(), key=lambda x: -len(x[1])):
        html_cats.append(f\'''
        <div class="category-section">
            <h3 class="category-title">{escape(cat)} <span class="count">({len(items)})</span></h3>
            <ul class="paper-list">
                {chr(10).join(f\'<li><a href="#paper-{i+1}">{escape(p[\'title_en\'][:60])}...</a></li>\' 
                    for i, p in enumerate(items) if items.index(p) < 20)}
            </ul>
        </div>
        \''')
    
    return '\n\'.join(html_cats)

def generate_paper_card(paper, index):
    title_en = escape(paper.get("title_en", ""))
    title_cn = escape(paper.get("title_cn", ""))
    authors = escape(format_authors(paper.get("authors", [])))
    year = paper.get("year", "")
    venue = escape(paper.get("venue", ""))
    cited_by = paper.get("cited_by", 0)
    category = escape(paper.get("category", ""))
    summary = escape(paper.get("summary", ""))
    motivation = escape(paper.get("motivation", ""))
    doi = paper.get("doi", "")
    abstract = escape(paper.get("abstract", "")[:300])
    apa = escape(format_apa(paper))
    
    return f\'''
    <div class="paper-card" id="paper-{index+1}">
        <div class="paper-header">
            <span class="paper-index">{index+1}</span>
            <span class="paper-category">{category}</span>
        </div>
        <h2 class="paper-title-cn">{title_cn}</h2>
        <h3 class="paper-title-en">{title_en}</h3>
        <div class="paper-meta">
            <span class="meta-item"><strong>作者:</strong> {authors}</span>
            <span class="meta-item"><strong>年份:</strong> {year}</span>
            <span class="meta-item"><strong>期刊:</strong> {venue}</span>
            <span class="meta-item"><strong>引用:</strong> {cited_by} 次</span>
        </div>
        <div class="paper-content">
            <div class="section">
                <h4>摘要</h4>
                <p>{abstract or "暂无摘要"}</p>
            </div>
            <div class="section">
                <h4>核心问题与创新点</h4>
                <p>{summary or "待补充"}</p>
            </div>
            <div class="section">
                <h4>研究动机</h4>
                <p>{motivation or "待补充"}</p>
            </div>
            <div class="section apa-citation">
                <h4>APA 引用格式</h4>
                <p>{apa}</p>
            </div>
            <div class="paper-actions">
                <a href="https://doi.org/{doi.split(\'/\')[-1]}" target="_blank" class="btn-doi">访问原文</a>
                <button onclick="copyAPA({index})" class="btn-copy">复制引用</button>
            </div>
        </div>
    </div>
    \'')

def generate_report(papers, output_file, title, subtitle):
    sidebar = generate_sidebar(papers)
    paper_cards = \'\n\'.join(generate_paper_card(p, i) for i, p in enumerate(papers))
    
    html = f\'\'\'<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-top: 1.5rem;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        .container {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            gap: 2rem;
        }}
        .sidebar {{
            width: 300px;
            flex-shrink: 0;
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            height: fit-content;
            position: sticky;
            top: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .sidebar h2 {{
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: #1a365d;
        }}
        .category-section {{
            margin-bottom: 1.5rem;
        }}
        .category-title {{
            font-size: 0.95rem;
            color: #2c5282;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .category-title .count {{
            font-size: 0.8rem;
            color: #666;
        }}
        .paper-list {{
            list-style: none;
        }}
        .paper-list li {{
            margin-bottom: 0.3rem;
        }}
        .paper-list a {{
            color: #4a5568;
            text-decoration: none;
            font-size: 0.85rem;
            display: block;
            padding: 0.3rem 0;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .paper-list a:hover {{
            background: #edf2f7;
            color: #2c5282;
        }}
        .main {{
            flex: 1;
        }}
        .paper-card {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .paper-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        .paper-index {{
            background: #2c5282;
            color: white;
            width: 2rem;
            height: 2rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        .paper-category {{
            background: #bee3f8;
            color: #2b6cb0;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
        }}
        .paper-title-cn {{
            color: #1a365d;
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        .paper-title-en {{
            color: #4a5568;
            font-size: 1.1rem;
            font-weight: normal;
            margin-bottom: 1rem;
        }}
        .paper-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .meta-item {{
            color: #4a5568;
            font-size: 0.9rem;
        }}
        .section {{
            margin-bottom: 1.5rem;
        }}
        .section h4 {{
            color: #2c5282;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }}
        .section p {{
            color: #4a5568;
            line-height: 1.8;
        }}
        .apa-citation {{
            background: #f7fafc;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #2c5282;
        }}
        .apa-citation p {{
            font-size: 0.9rem;
            font-style: italic;
        }}
        .paper-actions {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }}
        .btn-doi, .btn-copy {{
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            cursor: pointer;
            border: none;
        }}
        .btn-doi {{
            background: #2c5282;
            color: white;
        }}
        .btn-copy {{
            background: #e2e8f0;
            color: #4a5568;
        }}
        .btn-copy:hover {{
            background: #cbd5e0;
        }}
        @media (max-width: 900px) {{
            .container {{
                flex-direction: column;
            }}
            .sidebar {{
                width: 100%;
                position: static;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>{escape(title)}</h1>
        <p class="subtitle">{escape(subtitle)}</p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(papers)}</div>
                <div class="stat-label">论文总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{sum(p.get(\'cited_by\', 0) for p in papers)}</div>
                <div class="stat-label">总引用次数</div>
            </div>
        </div>
    </header>
    
    <div class="container">
        <aside class="sidebar">
            <h2>文献分类目录</h2>
            {sidebar}
        </aside>
        
        <main class="main">
            {paper_cards}
        </main>
    </div>
    
    <script>
        function copyAPA(index) {{
            const card = document.getElementById(\'paper-' + (index + 1));
            const apaText = card.querySelector(\'.apa-citation p').textContent;
            navigator.clipboard.writeText(apaText).then(() => {{
                alert(\'APA引用已复制到剪贴板！\');
            }});
        }}
    </script>
</body>
</html>
\'\'\')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Report generated: {output_file}")

if __name__ == "__main__":
    import sys
    papers_file = "../papers_enriched.json"
    output_file = "../report.html"
    title = "气候变化背景下海平面上升对沿海城市影响 - 文献综述"
    subtitle = "Climate Change and Sea Level Rise Impacts on Coastal Cities: A Literature Review"
    
    with open(papers_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    generate_report(papers, output_file, title, subtitle)
