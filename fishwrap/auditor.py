import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from fishwrap.db import repository
from fishwrap import _config

def audit_run(run_sheet, candidates, stats_context):
    """
    The Auditor:
    1. Calculates Funnel Metrics.
    2. Persists the Run to the DB.
    3. Generates the Transparency Report (Artifact).
    """
    
    # 1. Calculate Metrics
    input_count = stats_context.get('input_count', 0) # Total DB size / items seen
    pool_count = len(candidates) # Candidates considered (freshness)
    
    selected_articles_flat = []
    selected_count = 0
    
    # Track Output Counts
    output_source_counts = {}
    
    for section, articles in run_sheet.items():
        selected_count += len(articles)
        for idx, art in enumerate(articles):
            # Flat list for DB
            selected_articles_flat.append({
                'article_id': art.get('id'), # UUID
                'rank': idx + 1,
                'score': art.get('computed_score'),
                'section': section
            })
            
            # Output Source Counting
            try:
                domain = art.get('source_url', '').split('/')[2]
                output_source_counts[domain] = output_source_counts.get(domain, 0) + 1
            except:
                pass
            
    # Track Input Counts (Pool)
    input_source_counts = {}
    for art in candidates:
        try:
            domain = art.get('source_url', '').split('/')[2]
            input_source_counts[domain] = input_source_counts.get(domain, 0) + 1
        except:
            pass
    
    # Top 10 Input Sources (Snapshot for DB)
    dominance_snapshot = sorted(input_source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 2. Persist Run
    run_data = {
        'run_type': 'daily',
        'stats_input': input_count,
        'stats_pool': pool_count,
        'stats_selected': selected_count,
        'source_dominance': dominance_snapshot
    }
    
    run_id = repository.save_run(run_data, selected_articles_flat)
    print(f"\n[AUDITOR] Run recorded: {run_id}")
    
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
    
    render_context = {
        'run_id': run_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'date_str': datetime.now().strftime("%Y-%m-%d"),
        'stats_input': input_count,
        'stats_pool': pool_count,
        'stats_selected': selected_count,
        'yield_rate': (selected_count / pool_count * 100) if pool_count else 0,
        'source_velocity': velocity_data[:20],
        'bubble': bubble_data
    }
    
    generate_report(render_context)

def generate_report(context):
    """
    Renders the Jinja2 template.
    """
    # Locate Template
    # We look in the configured theme directory
    theme_dir = _config.THEME
    template_dir = os.path.join(theme_dir, 'templates')
    
    # Fallback to internal if not found (e.g. for default themes)
    if not os.path.exists(template_dir):
        # Try finding relative to repo root if _config.THEME is "basic"
        # This logic is brittle. Better to trust _config.THEME is absolute or correct relative.
        # But for 'demo/themes/basic', we need to be careful.
        pass

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('transparency.html')
    
    output = template.render(**context)
    
    output_dir = os.path.dirname(_config.LATEST_HTML_FILE)
    report_path = os.path.join(output_dir, 'transparency.html')
    
    with open(report_path, 'w') as f:
        f.write(output)
        
    print(f"[AUDITOR] Transparency Report generated: {report_path}\n")