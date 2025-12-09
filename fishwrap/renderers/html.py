import json
import os
import html
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from fishwrap import _config
from fishwrap import utils

import json
import os
import html
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from fishwrap import _config
from fishwrap import utils

def load_template(template_name):
    """Loads a template file from the configured theme directory."""
    # Base dir is the package root (fishwrap/fishwrap/)
    package_dir = os.path.dirname(os.path.dirname(__file__))
    # Project root is one level up (fishwrap/)
    project_root = os.path.dirname(package_dir)
    
    # 1. Try resolving relative to Project Root (User Themes)
    theme_path = os.path.join(project_root, _config.THEME)
    
    # 2. If not found, try resolving relative to Package Internal Themes
    if not os.path.exists(theme_path):
         theme_path = os.path.join(package_dir, 'themes', _config.THEME)

    if template_name == 'css':
        path = os.path.join(theme_path, 'css', 'style.css')
    else:
        path = os.path.join(theme_path, 'templates', f'{template_name}.html')
        
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] Template not found: {path}")
        return ""

def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return "Unknown"

def render(data, stats, vol_issue_str, date_str):
    """
    Renders the HTML issue using external templates.
    """
    
    # Load Templates
    tpl_layout = load_template('layout')
    tpl_sidebar_item = load_template('sidebar_item')
    tpl_section = load_template('section')
    tpl_card = load_template('card')
    tpl_debug_card = load_template('debug_card')
    css_block = load_template('css')

    # --- Sidebar Navigation ---
    nav_html = ""
    for section_def in _config.SECTIONS:
        sid = section_def['id']
        count = len(data.get(sid, []))
        if count == 0: continue
        
        nav_html += tpl_sidebar_item.format(
            sid=sid,
            title=section_def['title']
        )

    # --- Main Content Generation ---
    content_html = ""
    
    # Vintage accent colors (Ink Stamps)
    accent_colors = ["#c0392b", "#27ae60", "#2980b9", "#8e44ad", "#d35400"]

    for section_def in _config.SECTIONS:
        sid = section_def['id']
        articles = data.get(sid, [])
        if not articles: continue
        
        articles.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        
        articles_html = ""
        
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

                debug_html = tpl_debug_card.format(
                    class_html=class_html,
                    rows_html=rows_html,
                    final_score=bd.get('final_score', 0)
                )

            articles_html += tpl_card.format(
                link=link,
                card_type=card_type,
                inline_style=inline_style,
                domain=domain,
                title=title,
                debug_html=debug_html
            )
            
        content_html += tpl_section.format(
            sid=sid,
            title=section_def['title'],
            description=section_def['description'],
            articles_html=articles_html
        )

    full_html = tpl_layout.format(
        date_str=date_str,
        css_block=css_block,
        vol_issue_str=vol_issue_str,
        nav_html=nav_html,
        content_html=content_html
    )
    return full_html
    return full_html