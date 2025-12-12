import json
import os
from datetime import datetime
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
    input_count = stats_context.get('input_count', 0) # From Fetcher or DB
    pool_count = len(candidates) # Candidates considered by Editor
    
    selected_articles_flat = []
    selected_count = 0
    
    for section, articles in run_sheet.items():
        selected_count += len(articles)
        for idx, art in enumerate(articles):
            selected_articles_flat.append({
                'article_id': art.get('id'), # UUID
                'rank': idx + 1,
                'score': art.get('computed_score'),
                'section': section
            })
            
    # Calculate Source Dominance (Snapshot)
    source_counts = {}
    for art in candidates:
        try:
            domain = art.get('source_url', '').split('/')[2]
            source_counts[domain] = source_counts.get(domain, 0) + 1
        except:
            pass
    
    # Top 10 Sources in Pool
    dominance_snapshot = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 2. Persist Run
    run_data = {
        'run_type': 'daily', # Default for now
        'stats_input': input_count,
        'stats_pool': pool_count,
        'stats_selected': selected_count,
        'source_dominance': dominance_snapshot
        # 'cut_line_report': ... (Can pass this in too if Editor exposes it)
    }
    
    run_id = repository.save_run(run_data, selected_articles_flat)
    print(f"\n[AUDITOR] Run recorded: {run_id}")
    
    # 3. Generate Artifact (Transparency Report)
    generate_report(run_data, run_sheet)

def generate_report(run_data, run_sheet):
    """
    Generates transparency.html
    For now, a simple HTML dump. Later, use Jinja2.
    """
    output_dir = os.path.dirname(_config.LATEST_HTML_FILE)
    report_path = os.path.join(output_dir, 'transparency.html')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Transparency Report - {datetime.now().strftime('%Y-%m-%d')}</title>
        <style>
            body {{ font-family: monospace; padding: 2em; background: #fdfbf7; color: #333; }}
            h1 {{ border-bottom: 2px solid #333; }}
            .metric {{ margin: 1em 0; }}
            .label {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Transparency Report</h1>
        <p>Generated: {datetime.now()}</p>
        
        <div class="metric">
            <span class="label">Funnel:</span>
            {run_data['stats_input']} Seen &rarr; 
            {run_data['stats_pool']} Candidates &rarr; 
            {run_data['stats_selected']} Published
        </div>
        
        <div class="metric">
            <span class="label">Yield Rate:</span>
            {(run_data['stats_selected'] / run_data['stats_pool'] * 100) if run_data['stats_pool'] else 0:.2f}%
        </div>
        
        <h2>Source Dominance (Input Pool)</h2>
        <ul>
    """
    
    for domain, count in run_data['source_dominance']:
        html += f"<li>{domain}: {count}</li>"
        
    html += """
        </ul>
    </body>
    </html>
    """
    
    with open(report_path, 'w') as f:
        f.write(html)
        
    print(f"[AUDITOR] Transparency Report generated: {report_path}\n")
