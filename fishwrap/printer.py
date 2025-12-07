import json
import os
from datetime import datetime
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
    current_date_iso = now_pacific.strftime("%Y-%m-%d")
    
    # Load or Initialize Stats (Volume/Issue logic)
    if os.path.exists(_config.STATS_FILE):
        with open(_config.STATS_FILE, 'r') as f:
            stats = json.load(f)
    else:
        stats = {"volume": 1, "issue": 0, "last_date": "1970-01-01"}
    
    last_date = stats.get("last_date", "1970-01-01")
    current_stored_volume = stats.get("volume", 1)
    current_stored_issue = stats.get("issue", 0)
    
    # Logic to increment Issue/Volume
    if current_date_iso != last_date:
        founding_date = datetime.strptime(_config.FOUNDING_DATE, "%Y-%m-%d")
        years_diff = now_pacific.year - founding_date.year
        if (now_pacific.month, now_pacific.day) < (founding_date.month, founding_date.day):
            years_diff -= 1
        
        calculated_volume = max(1, years_diff + 1)
        
        if calculated_volume > current_stored_volume:
            volume = calculated_volume
            issue = 1
        else:
            volume = current_stored_volume
            issue = current_stored_issue + 1
            
        # Update stats
        stats["volume"] = volume
        stats["issue"] = issue
        stats["last_date"] = current_date_iso
        
        with open(_config.STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4)
    else:
        volume = current_stored_volume
        issue = current_stored_issue
            
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
