import json
import os
import shutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fishwrap import _config
from fishwrap.renderers import html as html_renderer
from fishwrap.renderers import pdf as pdf_renderer

def copy_static_assets():
    """Copies static assets from the active theme to the output directory."""
    # Resolve Theme Directory
    package_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(package_dir)
    
    # 1. Try resolving relative to Project Root (User Themes)
    theme_path = os.path.join(project_root, _config.THEME)
    
    # 2. If not found, try resolving relative to Package Internal Themes
    if not os.path.exists(theme_path):
         theme_path = os.path.join(package_dir, 'themes', _config.THEME)
    
    src_static = os.path.join(theme_path, 'static')
    
    # Resolve Output Directory
    output_dir = os.path.dirname(_config.LATEST_HTML_FILE)
    # Handle case where output dir is empty (current dir)
    if not output_dir:
        output_dir = "."
        
    dest_static = os.path.join(output_dir, 'static')

    if os.path.exists(src_static):
        # Remove existing static in output to ensure clean state
        if os.path.exists(dest_static):
            shutil.rmtree(dest_static)
        
        shutil.copytree(src_static, dest_static)
        # print(f"[PRINTER] Copied static assets from {src_static} to {dest_static}")
    else:
        # Create empty static dir if theme has none, to prevent 404s if referenced
        os.makedirs(dest_static, exist_ok=True)
        # print(f"[PRINTER] No static assets found in {theme_path}")
        
    return dest_static

def generate_issues():
    if not os.path.exists(_config.ENHANCED_ISSUE_FILE):
        print("Error: No enhanced issue file found.")
        return

    with open(_config.ENHANCED_ISSUE_FILE, 'r') as f:
        data = json.load(f)
    
    total_articles_to_print = sum(len(v) for v in data.values())
    print(f"[PRINTER] Loaded {total_articles_to_print} articles for printing.")
    
    # Timezone and Date setup
    pacific_tz = ZoneInfo(_config.TIMEZONE)
    now_pacific = datetime.now(pacific_tz)
    date_str = now_pacific.strftime("%A, %B %d, %Y")
    current_date = now_pacific.date() # Get only date part for comparison

    founding_date_dt = datetime.strptime(_config.FOUNDING_DATE, "%Y-%m-%d").date() # Get only date part

    # Calculate Volume
    volume = current_date.year - founding_date_dt.year + 1
    # Adjust volume if the founding month/day hasn't passed yet in the current year
    if (current_date.month, current_date.day) < (founding_date_dt.month, founding_date_dt.day):
        volume -= 1
    # Ensure volume is at least 1
    volume = max(1, volume)

    # Calculate Issue
    # The start date for counting issues within the current volume
    if volume == 1:
        start_of_issue_counting = founding_date_dt
    else:
        # For subsequent volumes, issues count from Jan 1 of that year
        start_of_issue_counting = datetime(current_date.year, 1, 1).date()

    issue = (current_date - start_of_issue_counting).days + 1
    
    # Load or Initialize Stats
    stats = {}
    if os.path.exists(_config.STATS_FILE):
        with open(_config.STATS_FILE, 'r') as f:
            stats = json.load(f)
    
    # Update stats for persistence
    stats["volume"] = volume
    stats["issue"] = issue
    stats["last_date"] = current_date.isoformat() # Store as ISO format
    
    with open(_config.STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)
            
    vol_issue_str = f"Vol. {volume}, Issue {issue}"

    # --- 1. Generate HTML ---
    html_content = html_renderer.render(data, stats, vol_issue_str, date_str)
    
    with open(_config.LATEST_HTML_FILE, 'w') as f:
        f.write(html_content)
    
    # --- 2. Copy Static Assets ---
    static_path = copy_static_assets()
    
    # --- 3. Generate PDF ---
    # print("[PRINTER] Generating PDF Edition...")
    # pdf_renderer.render(data, stats, vol_issue_str, date_str, _config.LATEST_PDF_FILE)
    
    print(f"\n[PRINTER] Generated {vol_issue_str}: {total_articles_to_print} articles. HTML: {_config.LATEST_HTML_FILE}")


if __name__ == "__main__":
    generate_issues()