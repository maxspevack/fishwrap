import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from fishwrap import _config
from fishwrap import __version__

def generate_edition(run_sheet):
    """
    Generates the final HTML artifact from the Run Sheet.
    """
    
    # 1. Prepare Context
    tz = ZoneInfo(_config.TIMEZONE)
    now = datetime.now(tz)
    
    # Determine Issue Number (Days since Founding)
    founding_date = datetime.strptime(_config.FOUNDING_DATE, "%Y-%m-%d").replace(tzinfo=tz)
    delta = now - founding_date
    issue_num = delta.days + 1
    
    vol_num = 1 # Hardcoded for now, or logic for yearly volume?
    
    # Organize Content for Template
    sections_data = []
    
    for section_def in _config.SECTIONS:
        sid = section_def['id']
        articles = run_sheet.get(sid, [])
        if not articles: continue
        
        # Apply Visual Formatting logic based on scores
        formatted_articles = []
        thresholds = _config.VISUAL_THRESHOLDS.get(sid)
        
        for idx, art in enumerate(articles):
            score = art.get('impact_score', 0)
            art_type = 'standard' # Default
            
            if idx == 0 and thresholds and score >= thresholds['lead']:
                art_type = 'feature'
            elif thresholds and score >= thresholds['feature']:
                art_type = 'standard'
            elif idx > 3:
                art_type = 'compact'
                
            art['visual_class'] = art_type
            
            # Clean domain for display
            try:
                domain = art.get('source_url', '').split('/')[2].replace('www.', '')
                art['domain'] = domain
            except:
                art['domain'] = 'web'

            # Calculate Time Ago
            try:
                ts = art.get('timestamp', 0)
                if ts:
                    art_dt = datetime.fromtimestamp(float(ts), tz)
                    delta = now - art_dt
                    
                    days = delta.days
                    seconds = delta.seconds
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    
                    if days > 365:
                         art['time_ago'] = f"{days // 365}y"
                    elif days > 30:
                        art['time_ago'] = f"{days // 30}mo"
                    elif days > 0:
                        art['time_ago'] = f"{days}d"
                    elif hours > 0:
                        art['time_ago'] = f"{hours}h"
                    else:
                        art['time_ago'] = f"{minutes}m"
                else:
                    art['time_ago'] = ""
            except Exception:
                art['time_ago'] = ""
                
            formatted_articles.append(art)
            
        sections_data.append({
            'id': sid,
            'title': section_def['title'],
            'description': section_def['description'],
            'articles': formatted_articles
        })

    # Load Transparency Fragment
    transparency_frag = ""
    frag_path = _config.RUN_SHEET_FILE.replace('run_sheet.json', 'transparency_fragment.html')
    if os.path.exists(frag_path):
        with open(frag_path, 'r') as f:
            transparency_frag = f.read()

    # 2. Render HTML
    theme_dir = _config.THEME
    template_dir = os.path.join(theme_dir, 'templates')
    
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Fix: Use 'layout.html' as the standard entry point, not 'index.html'
    template_name = 'layout.html'
    if not os.path.exists(os.path.join(template_dir, template_name)):
         # Fallback check if index.html exists (e.g. legacy themes?)
         if os.path.exists(os.path.join(template_dir, 'index.html')):
             template_name = 'index.html'
    
    template = env.get_template(template_name)
    
    # Inject CSS for inline email/single-file portability if needed
    css_path = os.path.join(theme_dir, 'css', 'style.css')
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            css_content = f.read()
            
    html_out = template.render(
        issue_number=issue_num,
        volume_number=vol_num,
        date_str=now.strftime("%A, %B %d, %Y"),
        time_str=now.strftime("%I:%M %p %Z"), # New: 08:00 AM PST
        vol_issue_str=f"Vol. {vol_num}, No. {issue_num}",
        sections=sections_data,
        css_block=css_content,
        transparency_report=transparency_frag,
        engine_version=f"v{__version__}"
    )
    
    # 3. Save Artifacts
    output_path = _config.LATEST_HTML_FILE
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(html_out)
        
    print(f"\n[PRINTER] Edition Published: {output_path}")
    
    # 4. Generate PDF (Optional/Bonus)
    if _config.LATEST_PDF_FILE:
        try:
            HTML(string=html_out, base_url=os.path.dirname(output_path)).write_pdf(_config.LATEST_PDF_FILE)
            print(f"[PRINTER] PDF Generated: {_config.LATEST_PDF_FILE}")
        except Exception as e:
            print(f"[PRINTER] PDF Generation Failed: {e}")

if __name__ == "__main__":
    with open(_config.RUN_SHEET_FILE, 'r') as f:
        data = json.load(f)
    generate_edition(data)
