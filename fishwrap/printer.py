import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fishwrap import _config
from fishwrap.renderers import html as html_renderer
from fishwrap.renderers import pdf as pdf_renderer

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
    
    # --- 2. Generate PDF ---
    # print("[PRINTER] Generating PDF Edition...")
    # pdf_renderer.render(data, stats, vol_issue_str, date_str, _config.LATEST_PDF_FILE)
    
    print("\n" + "="*40)
    print(f" PRINTER SUMMARY")
    print("="*40)
    print(f" Issue:     {vol_issue_str}")
    print(f" HTML:      {_config.LATEST_HTML_FILE}")
    # print(f" PDF:       {_config.LATEST_PDF_FILE}")
    print("="*40 + "\n")

if __name__ == "__main__":
    generate_issues()