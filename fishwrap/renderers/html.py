import json
import os
import html
import random # Import random
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from fishwrap import _config
from fishwrap import utils

def get_css_block():
    css_lines = [
        "/* Variables - Dracula Theme */",
        ":root {",
        "    --bg-color: #282a36;",
        "    --card-bg: #44475a;",
        "    --text-color: #f8f8f2;",
        "    --muted-color: #6272a4;",
        "    --accent-pink: #ff79c6;",
        "    --accent-green: #50fa7b;",
        "    --accent-cyan: #8be9fd;",
        "    --accent-orange: #ffb86c;",
        "    --accent-red: #ff5555;",
        "    --accent-yellow: #f1fa8c;",
        "    --accent-purple: #bd93f9;",
        "    --font-main: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
        "    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;",
        "}",
        "",
        "/* Base Styles */",
        "body {",
        "    font-family: var(--font-main);",
        "    color: var(--text-color);",
        "    background: var(--bg-color);",
        "    margin: 0;",
        "    padding: 0;",
        "    display: flex;",
        "    min-height: 100vh;",
        "}",
        "a { color: inherit; text-decoration: none; }",
        "h1, h2, h3 { margin: 0; font-weight: 700; }",
        "",
        "/* Sidebar Nav */",
        " .sidebar {",
        "    width: 240px;",
        "    background: #21222c;",
        "    padding: 30px 20px;",
        "    position: sticky;",
        "    top: 0;",
        "    height: 100vh;",
        "    box-sizing: border-box;",
        "    display: flex;",
        "    flex-direction: column;",
        "    border-right: 1px solid rgba(255,255,255,0.05);",
        "}",
        " .brand {",
        "    font-size: 1.5rem;",
        "    color: var(--accent-pink);",
        "    margin-bottom: 5px;",
        "    letter-spacing: -0.5px;",
        "}",
        " .brand-meta { font-size: 0.8rem; color: var(--muted-color); margin-bottom: 40px; font-family: var(--font-mono); }",
        "",
        " .nav-links { list-style: none; padding: 0; margin: 0; }",
        " .nav-item { margin-bottom: 15px; }",
        " .nav-link {",
        "    display: flex;",
        "    justify-content: space-between;",
        "    align-items: center;",
        "    padding: 10px 15px;",
        "    border-radius: 8px;",
        "    color: var(--text-color);",
        "    transition: background 0.2s;",
        "}",
        " .nav-link:hover { background: var(--card-bg); }",
        " .nav-count {",
        "    background: rgba(255,255,255,0.1);",
        "    padding: 2px 8px;",
        "    border-radius: 12px;",
        "    font-size: 0.75rem;",
        "    font-family: var(--font-mono);",
        "}",
        "",
        "/* Main Content Area */",
        " .main-content {",
        "    flex-grow: 1;",
        "    padding: 40px;",
        "    overflow-y: auto;",
        "}",
        "",
        "/* Section Layout (Tetris Grid) */",
        " .section-block { margin-bottom: 60px; scroll-margin-top: 20px; }",
        " .section-header {",
        "    display: flex;",
        "    align-items: center;",
        "    margin-bottom: 25px;",
        "    padding-bottom: 10px;",
        "    border-bottom: 2px solid var(--card-bg);",
        "}",
        " .section-title { font-size: 1.8rem; margin-right: 15px; color: var(--accent-cyan); }",
        " .section-tag { text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; color: var(--muted-color); border: 1px solid var(--muted-color); padding: 4px 8px; border-radius: 4px; }",
        "",
                " .bento-grid {",
                "    display: grid;",
                "    /* Desktop: 4 Columns */",
                "    grid-template-columns: repeat(4, 1fr);",
                "    gap: 20px;",
                "    grid-auto-flow: dense;",
                "    grid-auto-rows: 110px; /* Base Unit adjusted for meta + title */",
                "}",
                "",
                "/* Card Base */",
                " .card {",
                "    background: var(--card-bg);",
                "    border-radius: 16px;",
                "    padding: 20px;",
                "    display: flex;",
                "    flex-direction: column;",
                "    transition: transform 0.2s, box-shadow 0.2s;",
                "    border: 1px solid rgba(255,255,255,0.05);",
                "    overflow: hidden;",
                "    position: relative; /* Relative for debug overlay */",
                "}",
                " .card:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); border-color: var(--muted-color); }",
                "",
                " /* Typography Clamping */",
                " .card h3 {",
                "    display: -webkit-box;",
                "    -webkit-box-orient: vertical;",
                "    overflow: hidden;",
                "    margin: 0;",
                "    line-height: 1.3;",
                " }",
                "",
                " /* --- Type A: LEAD (Big Block) --- */",
                " /* 2 Cols x 2 Rows (Square-ish) */",
                " .card.feature {",
                "    grid-column: span 2;",
                "    grid-row: span 2;",
                "}",
                " .card.feature h3 { ",
                "    font-size: 1.8rem; /* Slightly bigger */",
                "    font-weight: 800;",
                "    -webkit-line-clamp: 5; ",
                "    line-height: 1.2;",
                "}",
                "",
                " /* --- Type B: STANDARD (Vertical) --- */",
                " /* 1 Col x 2 Rows */",
                " .card.standard {",
                "    grid-column: span 1;",
                "    grid-row: span 2;",
                " }",
                " .card.standard h3 { ",
                "    font-size: 1.3rem; ",
                "    font-weight: 700;",
                "    -webkit-line-clamp: 6; /* Reduced from 7 */",
                " }",
                "",
                " /* --- Type C: COMPACT (Square) --- */",
                " /* 1 Col x 1 Row */",
                " .card.compact {",
                "    grid-column: span 1;",
                "    grid-row: span 1;",
                "    padding: 20px;",
                "}",
                " .card.compact h3 { ",
                "    font-size: 0.8rem; /* Slightly smaller */",
                "    font-weight: 600;",
                "    -webkit-line-clamp: 3; /* Reduced from 4 */",
                " }",
                "",
                " .card-meta {",
                "    display: flex;",
                "    justify-content: space-between;",
                "    font-size: 0.75rem;",
                "    color: var(--muted-color);",
                "    margin-bottom: 8px;",
                "    font-family: var(--font-mono);",
                "    text-transform: uppercase;",
                "    letter-spacing: 0.5px;",
                "}",
                " .domain { font-weight: 700; color: var(--accent-cyan); }"
        ,
        "",
        " .card-footer {",
        "    margin-top: auto;",
        "    padding-top: 15px;",
        "    border-top: 1px solid rgba(255,255,255,0.1);",
        "    display: flex;",
        "    justify-content: space-between;",
        "    align-items: center;",
        "    font-size: 0.85rem;",
        "}",
        " .read-link { color: var(--accent-green); font-weight: 600; }",
        " .read-link:hover { text-decoration: underline; }",
        "",
        "/* Responsive Tweaks */",
        "@media (max-width: 1100px) {",
        "    .bento-grid { grid-template-columns: repeat(2, 1fr); }",
        "}",
        "@media (max-width: 768px) {",
        "    body { flex-direction: column; }",
        "    .sidebar { width: 100%; height: auto; position: relative; padding: 20px; border-right: none; border-bottom: 1px solid rgba(255,255,255,0.1); }",
        "    .main-content { padding: 20px; }",
        "    .nav-links { display: flex; overflow-x: auto; gap: 10px; padding-bottom: 10px; }",
        "    .nav-item { margin: 0; white-space: nowrap; }",
        "    .nav-link { background: var(--card-bg); }",
        "    /* Stack everything on mobile */",
        "    .bento-grid { grid-template-columns: 1fr; grid-auto-rows: auto; }",
        "    .card.feature, .card.standard, .card.compact { grid-column: auto; grid-row: auto; min-height: 150px; }",
        "}"
    ]
    return "\n".join(css_lines)


def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return "Unknown"

def render(data, stats, vol_issue_str, date_str):
    """
    Renders the HTML issue as a modern Bento Grid Dashboard.
    """
    
    # --- Sidebar Navigation ---
    nav_html = ""
    for section_def in _config.SECTIONS:
        sid = section_def['id']
        count = len(data.get(sid, []))
        if count == 0: continue
        nav_html += f"""
        <li class="nav-item">
            <a href="#{sid}" class="nav-link">
                <span>{section_def['title']}</span>
            </a>
        </li>
        """

    # --- Main Content Generation ---
    content_html = ""
    
    # Define Dracula accent colors for random selection
    accent_colors = [
        "#ff79c6", # pink
        "#50fa7b", # green
        "#8be9fd", # cyan
        "#ffb86c", # orange
        "#ff5555", # red
        "#f1fa8c", # yellow
        "#bd93f9"  # purple
    ]

    for section_def in _config.SECTIONS:
        sid = section_def['id']
        articles = data.get(sid, [])
        if not articles: continue
        
        # Ensure Descending Order by Score
        articles.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        
        # Section Header
        content_html += f"""
        <div id="{sid}" class="section-block">
            <div class="section-header">
                <h2 class="section-title">{section_def['title']}</h2>
                <span class="section-tag">{section_def['description']}</span>
            </div>
            <div class="bento-grid">
        """
        
        # Process Articles into Grid Slots
        
        # --- Smart Hierarchy Limiter ---
        # "Shorter Leash": Enforce a strict visual shape regardless of scores.
        lead_count = 0
        feature_count = 0
        MAX_LEADS = 2
        MAX_FEATURES = 4
        
        for i, article in enumerate(articles):
            score = article.get('impact_score', 0)
            thresholds = _config.VISUAL_THRESHOLDS.get(sid, _config.VISUAL_THRESHOLDS['news'])
            
            # Determine ideal type based on score
            if score >= thresholds['lead']:
                proposed_type = "feature" # CSS class name
            elif score >= thresholds['feature']:
                proposed_type = "standard"
            else:
                proposed_type = "compact"
                
            # Apply Quotas (Downgrade if full)
            if proposed_type == "feature":
                if lead_count < MAX_LEADS:
                    card_type = "feature"
                    lead_count += 1
                elif feature_count < MAX_FEATURES:
                    card_type = "standard" # Downgrade to Standard
                    feature_count += 1
                else:
                    card_type = "compact" # Downgrade to Compact
            elif proposed_type == "standard":
                if feature_count < MAX_FEATURES:
                    card_type = "standard"
                    feature_count += 1
                else:
                    card_type = "compact"
            else:
                card_type = "compact"
            
            # Choose a random accent color for each card
            rand_col = random.choice(accent_colors)
            inline_style = f'style="border-color: {rand_col};"'

            if card_type == "feature": 
                # For feature cards, also apply a background gradient
                inline_style = f'style="background: linear-gradient(135deg, var(--card-bg) 0%, {rand_col}40 100%); border-left-color: {rand_col};"'
            
            # Data Extraction
            title = html.escape(article.get('title', 'No Title'))
            link = article.get('link', '#')
            domain = get_domain(link)
            
            # Use HN Comments URL if available
            # 1. explicit comments_url (newly fetched)
            # 2. id is the HN link (historically fetched via hnrss.org)
            if (domain == 'news.ycombinator.com' or 'hnrss.org' in article.get('source_url', '')):
                if article.get('comments_url'):
                    link = article['comments_url']
                elif 'news.ycombinator.com/item' in article.get('id', ''):
                    link = article['id']
            
            # --- Content Streamlining: Source + Headline ONLY ---
            # No excerpts for any card type.
            
            # Debug Overlay ("Score Card")
            debug_html = ""
            # Always generate debug info (hidden by CSS)
            bd = article.get('score_breakdown', {})
            cls_debug = article.get('classification_debug', {})
            
            if bd or cls_debug:
                # Classification Debug
                class_html = ""
                if cls_debug:
                    scores = cls_debug.get('scores', {})
                    s_str = " ".join([f"{k[0].upper()}:{v}" for k,v in scores.items() if v > 0])
                    reason = cls_debug.get('reason', 'n/a')
                    class_html = f"""
                    <div class="debug-section">
                        <div class="debug-header">CLASSIFICATION</div>
                        <div class="debug-row"><span class="label">Reason</span><span class="val">{reason}</span></div>
                        <div class="debug-row"><span class="label">Hits</span><span class="val">{s_str or "None"}</span></div>
                    </div>
                    """

                unit = bd.get('boost_unit', 500)
                
                # Build Impact List
                impacts = []
                
                # 1. Base
                base_pts = bd.get('base_boosts', 0) * unit
                if base_pts != 0:
                    impacts.append(("Base Profile", base_pts))
                    
                # 2. Stats
                stats_pts = bd.get('stats_part', 0)
                if stats_pts != 0:
                    impacts.append((f"Stats (S:{bd.get('stats_score')} C:{bd.get('stats_comments')})", stats_pts))
                    
                # 3. Policies
                for pol_name, pol_boosts in bd.get('policy_hits', []):
                    impacts.append((f"Policy: {pol_name}", pol_boosts * unit))
                    
                # 4. Fetcher Merges
                fetcher_pts = bd.get('fetcher_boosts', 0) * unit
                if fetcher_pts > 0:
                    impacts.append((f"Cross-Feed Merge (x{bd.get('fetcher_boosts')})", fetcher_pts))
                    
                # 5. Fuzzy Cluster
                fuzzy_boosts = bd.get('total_boosts', 0) - bd.get('base_boosts', 0) - bd.get('policy_boosts', 0) - bd.get('fetcher_boosts', 0)
                fuzzy_pts = fuzzy_boosts * unit
                if fuzzy_pts > 0:
                    impacts.append((f"Editorial Cluster (x{fuzzy_boosts})", fuzzy_pts))
                    
                # Render Rows
                rows_html = ""
                for label, val in impacts:
                    color = "#50fa7b" if val > 0 else "#ff5555"
                    if val == 0: color = "#6272a4"
                    rows_html += f"<div class='debug-row'><span class='label'>{label}</span><span class='val' style='color:{color}'>{val:+}</span></div>"
                    
                # Render Fuzzy Matches List
                if bd.get('fuzzy_matches'):
                    rows_html += f"<div class='debug-note'>Merged: {', '.join(bd['fuzzy_matches'])}</div>"

                debug_html = f"""
                <div class="debug-card">
                    {class_html}
                    <div class="debug-section">
                        <div class="debug-header">SCORING BREAKDOWN</div>
                        {rows_html}
                        <div class="debug-total">
                            <span>FINAL</span>
                            <span>{bd.get('final_score', 0)}</span>
                        </div>
                    </div>
                </div>
                """

            # Conditionally render card-meta (always for all cards now)
            card_meta_html = f"""
            <div class="card-meta">
                <span class="domain">{domain}</span>
            </div>
            """
            
            # Render Card
            content_html += f"""
            <a href="{link}" target="_blank" class="card {card_type}" {inline_style}>
                {card_meta_html}
                <h3>{title}</h3>
                {debug_html}
            </a>
            """
            
        content_html += "</div></div>" # End Grid / Section

    css_block = get_css_block() + """
    /* Debug UI - Hidden by default */
    .debug-card {
        display: none;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(40, 42, 54, 0.95); /* High opacity Dracula bg */
        padding: 15px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        z-index: 100;
        overflow-y: auto;
        backdrop-filter: blur(2px);
    }

    body.debug-active .debug-card {
        display: block;
        animation: fadeIn 0.3s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .debug-header {
        font-weight: 700;
        color: var(--muted-color);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.65rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 4px;
    }

    .debug-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        line-height: 1.4;
    }
    
    .debug-note {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px dashed rgba(255,255,255,0.1);
        color: var(--accent-yellow);
        font-style: italic;
    }

    .debug-total {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid rgba(255,255,255,0.2);
        display: flex;
        justify-content: space-between;
        font-weight: 700;
        color: var(--accent-cyan);
        font-size: 0.9rem;
    }
    
    /* Sidebar Layout */
    .sidebar-header {
        margin-bottom: 40px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 20px;
    }
    .brand {
        font-size: 1.8rem;
        color: var(--accent-pink);
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1;
        margin-bottom: 5px;
    }
    .motto {
        font-family: var(--font-main);
        font-size: 0.9rem;
        color: var(--accent-purple);
        font-style: italic;
        margin-bottom: 15px;
        opacity: 0.9;
    }
    .meta-block {
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--muted-color);
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .meta-date { color: var(--text-color); font-weight: 600; }
    
    .nav-links { margin-top: 20px; }
    .nav-link {
        padding: 12px 15px;
        margin-bottom: 8px;
        border-radius: 8px;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    .nav-link:hover {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.1);
        transform: translateX(4px);
    }
    
    .sidebar-footer {
        margin-top: auto;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }

    .icon-link, .debug-toggle {
        background: none;
        border: none;
        font-size: 1.2rem;
        opacity: 0.3;
        cursor: pointer;
        transition: all 0.2s;
        padding: 5px;
        color: var(--text-color);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .icon-link:hover, .debug-toggle:hover { opacity: 1; transform: scale(1.1); }
    .debug-toggle:hover { transform: rotate(15deg) scale(1.1); }
    
    .icon-link svg { width: 20px; height: 20px; fill: currentColor; }

    /* ... (Rest of CSS) */
    """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily Clamour - {date_str}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <style>
{css_block}
    </style>
</head>
<body>

<nav class="sidebar">
    <div class="sidebar-header">
        <div class="brand">The Daily Clamour</div>
        <div class="motto">"Often Wrong, Never in Doubt"</div>
        
        <div class="meta-block">
            <span class="meta-date">{date_str}</span>
            <span>{vol_issue_str}</span>
        </div>
    </div>
    
    <ul class="nav-links">
        {nav_html}
    </ul>
    
    <div class="sidebar-footer">
        <a href="https://github.com/maxspevack/fishwrap" target="_blank" class="icon-link" title="View Source on GitHub">
            <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>GitHub</title><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
        </a>
        <button class="debug-toggle" onclick="document.body.classList.toggle('debug-active')" title="Toggle Debug Overlay">
            🛠️
        </button>
    </div>
</nav>

<main class="main-content">
    {content_html}
</main>

</body>
</html>
"""
    return full_html