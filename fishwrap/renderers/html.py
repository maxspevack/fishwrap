import json
import os
import html
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from fishwrap import _config
from fishwrap import utils

def get_css_block():
    css_lines = [
        "/* Variables - Vintage Clamour Theme */",
        ":root {",
        "    --bg-color: #fdfbf7; /* Cream Paper */",
        "    --card-bg: #ffffff; /* Slightly lighter than bg */",
        "    --text-color: #2f2f2f; /* Deep Sepia/Black Ink */",
        "    --muted-color: #7f8c8d;",
        "    --accent-primary: #2c3e50; /* Slate */",
        "    --accent-red: #c0392b; /* Urgent News Red */",
        "    --accent-blue: #2980b9; /* Link Blue */",
        "    --border-color: #dcdcdc;",
        "    --font-head: 'Special Elite', cursive;",
        "    --font-body: 'Georgia', serif;",
        "    --font-mono: 'Courier Prime', monospace;",
        "}",
        "",
        "/* Base Styles */",
        "body {",
        "    font-family: var(--font-body);",
        "    color: var(--text-color);",
        "    background-color: var(--bg-color);",
        "    background-image: url('static/textures/newsprint.png');",
        "    background-repeat: repeat;",
        "    margin: 0;",
        "    padding: 0;",
        "    display: flex;",
        "    min-height: 100vh;",
        "}",
        "a { color: var(--text-color); text-decoration: none; }",
        "a:hover { text-decoration: underline; color: var(--accent-blue); }",
        "h1, h2, h3 { margin: 0; font-weight: 700; font-family: var(--font-head); }",
        "",
        "/* Sidebar Nav */",
        " .sidebar {",
        "    width: 280px;",
        "    background-color: var(--bg-color);",
        "    background-image: url('static/textures/newsprint-texture.png');",
        "    background-repeat: repeat;",
        "    color: var(--text-color);",
        "    padding: 30px 20px;",
        "    position: sticky;",
        "    top: 0;",
        "    height: 100vh;",
        "    box-sizing: border-box;",
        "    display: flex;",
        "    flex-direction: column;",
        "    border-right: 8px double var(--text-color); /* Thicker double line gutter */",
        "    box-shadow: 2px 0 10px rgba(0,0,0,0.2);",
        "    z-index: 50;",
        "}",
        " .sidebar a { color: var(--text-color); text-decoration: none; }",
        " .sidebar a:hover { color: var(--accent-blue); }",
        "",
        " .brand-logo {",
        "    width: 100%;",
        "    max-width: 220px;",
        "    margin: 0 auto 10px auto;",
        "    display: block;",
        "    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));",
        "}",
        " .mascot-container {",
        "    text-align: center;",
        "    margin-bottom: 20px;",
        "    padding-bottom: 20px;",
        "    border-bottom: 1px dashed var(--text-color);",
        "}",
        " .mascot-img {",
        "    width: 140px;",
        "    height: auto;",
        "    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);",
        "}",
        " .mascot-img:hover { transform: scale(1.1) rotate(-5deg); }",
        "",
        " .motto {",
        "    font-family: var(--font-mono);",
        "    font-size: 0.8rem;",
        "    color: var(--muted-color);",
        "    font-style: italic;",
        "    margin-bottom: 5px;",
        "    text-align: center;",
        "}",
        " .meta-block {",
        "    font-family: var(--font-mono);",
        "    font-size: 0.7rem;",
        "    color: var(--muted-color);",
        "    text-align: center;",
        "    display: flex;",
        "    flex-direction: column;",
        "    gap: 2px;",
        "}",
        "",
        " .nav-links {",
        "    list-style: none;",
        "    padding: 0;",
        "    margin: 20px 0 0 0;",
        "    flex-grow: 1;",
        "    overflow-y: auto;",
        "    -webkit-overflow-scrolling: touch; /* For smoother iOS scrolling */",
        " }",
        " .nav-item { margin-bottom: 10px; }",
        " .nav-link {",
        "    display: flex;",
        "    justify-content: flex-start;",
        "    align-items: center;",
        "    gap: 15px;",
        "    padding: 10px 15px;",
        "    border-radius: 4px;",
        "    background: rgba(0,0,0,0.03); /* Slight background for hover */",
        "    transition: all 0.2s;",
        "    border-left: 3px solid transparent;",
        "    color: var(--text-color);",
        "    min-height: 60px;",
        "}",
        " .nav-link:hover { background: rgba(0,0,0,0.08); border-left-color: var(--accent-red); transform: translateX(5px); }",
        " .nav-icon {",
        "    height: 50px;",
        "    width: auto;",
        "    object-fit: contain;",
        "    filter: drop-shadow(1px 1px 0 rgba(0,0,0,0.2));",
        "    transition: transform 0.2s;",
        " }",
        " .nav-link:hover .nav-icon { transform: scale(1.1) rotate(5deg); }",
        " .nav-label {",
        "    font-family: var(--font-head);",
        "    letter-spacing: 1px;",
        "    font-size: 1.2rem;",
        "    font-weight: 700;",
        "    text-transform: uppercase;",
        " }",
        "",
        "/* Sidebar Footer */",
        " .sidebar-footer {",
        "    margin-top: auto;",
        "    display: flex;",
        "    align-items: center;",
        "    justify-content: center;",
        "    gap: 20px;",
        "    padding-top: 20px;",
        "    border-top: 1px dashed var(--text-color);",
        "}",
        " .icon-btn {",
        "    background: none;",
        "    border: none;",
        "    cursor: pointer;",
        "    opacity: 0.8;",
        "    transition: all 0.2s;",
        "    padding: 0;",
        "    display: block;",
        "}",
        " .icon-btn img, .icon-btn svg { width: 28px; height: 28px; display: block; }",
        " .icon-btn:hover { opacity: 1; transform: scale(1.1); }",
        "",
        "/* Main Content Area */",
        " .main-content {",
        "    flex-grow: 1;",
        "    padding: 40px;",
        "    overflow-y: auto;",
        "}",
        "",
        "/* Section Layout */",
        " .section-block { margin-bottom: 60px; scroll-margin-top: 20px; }",
        " .section-header {",
        "    display: flex;",
        "    align-items: baseline;",
        "    margin-bottom: 25px;",
        "    padding-bottom: 10px;",
        "    border-bottom: 3px double var(--text-color);",
        "}",
        " .section-title { font-size: 2.2rem; margin-right: 15px; text-transform: uppercase; letter-spacing: -1px; }",
        " .section-tag { font-family: var(--font-mono); font-size: 0.9rem; color: var(--muted-color); text-transform: uppercase; }",
        "",
        " .bento-grid {",
        "    display: grid;",
        "    grid-template-columns: repeat(4, 1fr);",
        "    gap: 25px;",
        "    grid-auto-flow: dense;",
        "    grid-auto-rows: 120px;",
        "}",
        "",
        "/* Card Styles (Newspaper Clipping Look) */",
        " .card {",
        "    background: var(--card-bg);",
        "    padding: 20px;",
        "    display: flex;",
        "    flex-direction: column;",
        "    transition: transform 0.2s, box-shadow 0.2s;",
        "    border: 1px solid var(--border-color);",
        "    box-shadow: 3px 3px 0 rgba(0,0,0,0.1);",
        "    overflow: hidden;",
        "    position: relative;",
        "    color: var(--text-color);",
        "}",
        " .card:hover {",
        "    transform: translateY(-2px) rotate(0.5deg);",
        "    box-shadow: 5px 5px 0 rgba(0,0,0,0.2);",
        "    border-color: var(--accent-primary);",
        "}",
        " .card-meta {",
        "    display: flex;",
        "    justify-content: space-between;",
        "    font-size: 0.75rem;",
        "    color: var(--muted-color);",
        "    margin-bottom: 10px;",
        "    font-family: var(--font-mono);",
        "    text-transform: uppercase;",
        "    letter-spacing: 0.5px;",
        "    border-bottom: 1px dotted #ccc;",
        "    padding-bottom: 4px;",
        "}",
        " .domain { font-weight: 700; color: var(--accent-primary); }",
        "",
        " /* Typography Clamping */",
        " .card h3 {",
        "    display: -webkit-box;",
        "    -webkit-box-orient: vertical;",
        "    overflow: hidden;",
        "    margin: 0;",
        "    line-height: 1.3;",
        "    font-family: var(--font-head);",
        " }",
        "",
        " /* Type Sizes */",
        " .card.feature { grid-column: span 2; grid-row: span 2; background: #fffdf0; }",
        " .card.feature h3 { font-size: 2.0rem; font-weight: 400; -webkit-line-clamp: 5; line-height: 1.1; }",
        "",
        " .card.standard { grid-column: span 1; grid-row: span 2; }",
        " .card.standard h3 { font-size: 1.4rem; -webkit-line-clamp: 6; }",
        "",
        " .card.compact { grid-column: span 1; grid-row: span 1; padding: 15px; }",
        " .card.compact h3 { font-size: 1.0rem; -webkit-line-clamp: 3; }",
        "",
        "/* Responsive */",
        "@media (max-width: 1100px) { .bento-grid { grid-template-columns: repeat(2, 1fr); } }",
        "@media (max-width: 768px) {",
        "    body { flex-direction: column; }",
        "    .sidebar { width: 100%; height: auto; position: relative; padding: 20px; border-right: none; border-bottom: 4px solid var(--text-color); box-shadow: none; }",
        "    .nav-links { display: flex; overflow-x: auto; gap: 10px; margin-top: 10px; }",
        "    .nav-item { margin: 0; white-space: nowrap; }",
        "    .bento-grid { grid-template-columns: 1fr; grid-auto-rows: auto; }",
        "    .card.feature, .card.standard, .card.compact { grid-column: auto; grid-row: auto; min-height: 150px; }",
        "}",
        "",
        "/* Debug Overlay (Vintage Style) */",
        " .debug-card {",
        "    display: none;",
        "    position: absolute; top: 0; left: 0; right: 0; bottom: 0;",
        "    background: rgba(255, 255, 255, 0.95);",
        "    padding: 15px;",
        "    font-family: var(--font-mono);",
        "    font-size: 0.75rem;",
        "    z-index: 100;",
        "    overflow-y: auto;",
        "    color: #000;",
        "    border: 2px solid red;",
        "}",
        "body.debug-active .debug-card { display: block; }",
        " .debug-header { font-weight: 700; border-bottom: 1px solid #000; margin-bottom: 5px; }",
        " .debug-row { display: flex; justify-content: space-between; margin-bottom: 2px; }",
        " .debug-total { border-top: 2px solid #000; margin-top: 5px; font-weight: 700; display: flex; justify-content: space-between; font-size: 0.9rem; }"
    ]
    return "\n".join(css_lines)


def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return "Unknown"

def render(data, stats, vol_issue_str, date_str):
    """
    Renders the HTML issue as a Vintage Clamour Newspaper.
    """
    
    # --- Sidebar Navigation ---
    nav_html = ""
    for section_def in _config.SECTIONS:
        sid = section_def['id']
        count = len(data.get(sid, []))
        if count == 0: continue
        
        # Mascots for each section
        nav_html += f"""
        <li class="nav-item">
            <a href="#{sid}" class="nav-link">
                <img src="static/images/{sid}-scoop.png" class="nav-icon" alt="{section_def['title']}">
                <span class="nav-label">{section_def['title']}</span>
            </a>
        </li>
        """

    # --- Main Content Generation ---
    content_html = ""
    
    # Vintage accent colors (Ink Stamps)
    accent_colors = ["#c0392b", "#27ae60", "#2980b9", "#8e44ad", "#d35400"]

    for section_def in _config.SECTIONS:
        sid = section_def['id']
        articles = data.get(sid, [])
        if not articles: continue
        
        articles.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        
        content_html += f"""
        <div id="{sid}" class="section-block">
            <div class="section-header">
                <h2 class="section-title">{section_def['title']}</h2>
                <span class="section-tag">{section_def['description']}</span>
            </div>
            <div class="bento-grid">
        """
        
        lead_count = 0
        feature_count = 0
        MAX_LEADS = 2
        MAX_FEATURES = 4
        
        for i, article in enumerate(articles):
            score = article.get('impact_score', 0)
            thresholds = _config.VISUAL_THRESHOLDS.get(sid, _config.VISUAL_THRESHOLDS['news'])
            
            if score >= thresholds['lead']: proposed_type = "feature"
            elif score >= thresholds['feature']: proposed_type = "standard"
            else: proposed_type = "compact"
                
            if proposed_type == "feature":
                if lead_count < MAX_LEADS: card_type = "feature"; lead_count += 1
                elif feature_count < MAX_FEATURES: card_type = "standard"; feature_count += 1
                else: card_type = "compact"
            elif proposed_type == "standard":
                if feature_count < MAX_FEATURES: card_type = "standard"; feature_count += 1
                else: card_type = "compact"
            else:
                card_type = "compact"
            
            # Random "Stamped" Border Color
            rand_col = random.choice(accent_colors)
            inline_style = f'style="border-top: 4px solid {rand_col};"'

            title = html.escape(article.get('title', 'No Title'))
            link = article.get('link', '#')
            domain = get_domain(link)
            
            if (domain == 'news.ycombinator.com' or 'hnrss.org' in article.get('source_url', '')):
                if article.get('comments_url'): link = article['comments_url']
                elif 'news.ycombinator.com/item' in article.get('id', ''): link = article['id']
            
            # Debug Overlay
            debug_html = ""
            bd = article.get('score_breakdown', {})
            cls_debug = article.get('classification_debug', {})
            
            if bd or cls_debug:
                class_html = ""
                if cls_debug:
                    reason = cls_debug.get('reason', 'n/a')
                    class_html = f"""
                    <div class="debug-section">
                        <div class="debug-header">CLASSIFICATION</div>
                        <div class="debug-row"><span class="label">Reason</span><span class="val">{reason}</span></div>
                    </div>
                    """
                
                rows_html = ""
                unit = bd.get('boost_unit', 500)
                
                base_pts = bd.get('base_boosts', 0) * unit
                if base_pts: rows_html += f"<div class='debug-row'><span class='label'>Base</span><span class='val'>{base_pts:+}</span></div>"
                
                stats_pts = bd.get('stats_part', 0)
                if stats_pts: rows_html += f"<div class='debug-row'><span class='label'>Stats</span><span class='val'>{stats_pts:+}</span></div>"
                
                for pol_name, pol_boosts in bd.get('policy_hits', []):
                    rows_html += f"<div class='debug-row'><span class='label'>{pol_name[:15]}</span><span class='val'>{pol_boosts*unit:+}</span></div>"
                
                fuzzy_pts = (bd.get('total_boosts', 0) - bd.get('base_boosts', 0) - bd.get('policy_boosts', 0)) * unit
                if fuzzy_pts > 0: rows_html += f"<div class='debug-row'><span class='label'>Cluster</span><span class='val'>{fuzzy_pts:+}</span></div>"

                debug_html = f"""
                <div class="debug-card">
                    {class_html}
                    <div class="debug-section">
                        <div class="debug-header">SCORE CARD</div>
                        {rows_html}
                        <div class="debug-total">
                            <span>TOTAL</span>
                            <span>{bd.get('final_score', 0)}</span>
                        </div>
                    </div>
                </div>
                """

            content_html += f"""
            <a href="{link}" target="_blank" class="card {card_type}" {inline_style}>
                <div class="card-meta">
                    <span class="domain">{domain}</span>
                </div>
                <h3>{title}</h3>
                {debug_html}
            </a>
            """
            
        content_html += "</div></div>"

    css_block = get_css_block()

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily Clamour - {date_str}</title>
    <!-- Fonts: Special Elite (Headlines), Courier Prime (Mono), Georgia (Body) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Special+Elite&display=swap" rel="stylesheet">
    <link rel="apple-touch-icon" sizes="180x180" href="static/images/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="static/images/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="static/images/favicon-16x16.png">
    <link rel="shortcut icon" href="static/images/favicon.ico">
    <style>
{css_block}
    </style>
</head>
<body>

<nav class="sidebar">
    <div class="mascot-container">
        <img src="static/images/daily-clamour-logo.png" alt="The Daily Clamour" class="brand-logo">
        <div class="motto">"Often Wrong, Never in Doubt"</div>
        <img src="static/images/scoop.png" alt="Scoop the Pearl" class="mascot-img">
        
        <div class="meta-block">
            <span class="meta-date">{date_str}</span>
            <span>{vol_issue_str}</span>
        </div>
    </div>
    
    <ul class="nav-links">
        {nav_html}
    </ul>
    
    <div class="sidebar-footer">
        <a href="https://github.com/maxspevack/fishwrap" target="_blank" class="icon-btn" title="View Source on GitHub">
            <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>GitHub</title><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"></path></svg>
        </a>
        <button class="icon-btn" onclick="document.body.classList.toggle('debug-active')" title="Toggle Debug Overlay">
            <img src="static/images/debug-scoop.png" alt="Debug Tools">
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
