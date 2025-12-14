import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader
from fishwrap.db import repository
from fishwrap import _config

def audit_run(run_sheet, candidates, stats_context):
    """
    The Auditor:
    1. Calculates Funnel Metrics.
    2. Persists the Run to the DB.
    3. Generates the Transparency Report (Artifact).
    4. Records detailed Audit Logs for Tuning.
    """
    
    # 1. Calculate Metrics
    input_count = stats_context.get('input_count', 0) # Total DB size / items seen
    pool_count = len(candidates) # Candidates considered (freshness)
    
    selected_articles_flat = []
    selected_ids = set() # For fast lookup
    selected_count = 0
    
    # Track Output Counts
    output_source_counts = {}
    
    for section, articles in run_sheet.items():
        selected_count += len(articles)
        for idx, art in enumerate(articles):
            # Flat list for DB (RunArticle)
            selected_articles_flat.append({
                'article_id': art.get('id'), # UUID
                'rank': idx + 1,
                'score': art.get('computed_score'),
                'section': section
            })
            selected_ids.add(art.get('id'))
            
            # Output Source Counting
            try:
                domain = art.get('source_url', '').split('/')[2]
                output_source_counts[domain] = output_source_counts.get(domain, 0) + 1
            except:
                pass
            
    # Track Input Counts (Pool) & Build Audit Log
    input_source_counts = {}
    audit_logs = []
    
    for art in candidates:
        # Source Counting
        try:
            domain = art.get('source_url', '').split('/')[2]
            input_source_counts[domain] = input_source_counts.get(domain, 0) + 1
        except:
            pass
            
        # Build Audit Log Entry
        # Decision Logic:
        decision = 'SELECTED' if art.get('id') in selected_ids else 'REJECTED'
        
        # Check if Buried (Negative Score)
        score = art.get('computed_score', 0)
        if score < 0:
            decision = 'BURIED'
            
        # Parse Breakdown for Scores
        breakdown = art.get('computed_breakdown', {})
        
        audit_entry = {
            'article_id': art.get('id'),
            'original_section': art.get('computed_category'),
            'final_section': art.get('computed_category'),
            'base_score': 0,
            'modifier_score': 0,
            'final_score': score,
            'decision': decision,
            'trace': breakdown
        }
        audit_logs.append(audit_entry)
    
    # Top 10 Input Sources (Snapshot for DB)
    dominance_snapshot = sorted(input_source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 2. Persist Run
    run_data = {
        'run_type': 'daily',
        'stats_input': input_count,
        'stats_pool': pool_count,
        'stats_selected': selected_count,
        'source_dominance': dominance_snapshot,
        'perf_metrics': stats_context.get('perf_metrics', {})
    }
    
    run_id = repository.save_run(run_data, selected_articles_flat)
    
    # 2.5 Persist Audit Logs
    repository.save_audit_logs(run_id, audit_logs)
    
    print(f"\n[AUDITOR] Run recorded: {run_id}. Audit logs saved: {len(audit_logs)}.")
    
    # 3. Generate Artifact (Transparency Report)
    # Calculate Velocity Data for Report
    velocity_data = []
    all_domains = set(input_source_counts.keys()) | set(output_source_counts.keys())
    
    for d in all_domains:
        in_c = input_source_counts.get(d, 0)
        out_c = output_source_counts.get(d, 0)
        
        in_pct = (in_c / pool_count * 100) if pool_count else 0
        out_pct = (out_c / selected_count * 100) if selected_count else 0
        
        velocity_data.append({
            'domain': d,
            'input_count': in_c,
            'output_count': out_c,
            'input_pct': in_pct,
            'output_pct': out_pct,
            'delta': out_pct - in_pct,
            'sort_metric': out_pct - in_pct # Sort by Delta (Signal Strength)
        })
        
    # Sort by Delta descending (High Signal top, High Noise bottom)
    velocity_data.sort(key=lambda x: x['sort_metric'], reverse=True)
    
    bubble_data = stats_context.get('bubble', {})
    
    # Timezone handling
    tz = ZoneInfo(_config.TIMEZONE)
    now = datetime.now(tz)

    # Map Section IDs to Titles (e.g., 'news' -> 'Beat')
    section_map = {s['id']: s['title'] for s in _config.SECTIONS} if hasattr(_config, 'SECTIONS') else {}

    render_context = {
        'run_id': run_id,
        'timestamp': now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        'date_str': now.strftime("%Y-%m-%d"),
        'stats_input': input_count,
        'stats_pool': pool_count,
        'stats_selected': selected_count,
        'anti_feed_protection': ((input_count - selected_count) / input_count * 100) if input_count else 0,
        'filtered_count': input_count - selected_count,
        'source_velocity': velocity_data,
        'bubble': bubble_data,
        'section_map': section_map
    }
    
    # 3. Generate Artifact (Transparency Report HTML)
    transparency_html = generate_report(render_context)
    
    return run_id, transparency_html

def generate_report(context):
    """
    Renders the Jinja2 template and returns HTML string.
    """
    theme_dir = _config.THEME
    template_dir = os.path.join(theme_dir, 'templates')
    
    if not os.path.exists(template_dir):
        pass

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('transparency.html')
    
    output = template.render(**context)
    
    return output
