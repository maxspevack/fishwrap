# --- 1. Feeds (Sources) ---
FEEDS = [
  "https://feeds.feedburner.com/TheHackersNews",  # The Hacker News
  "https://www.bleepingcomputer.com/feed/",       # BleepingComputer
  "https://krebsonsecurity.com/feed/",            # Krebs on Security
  "https://www.cisa.gov/uscert/ncas/alerts.xml",  # CISA Alerts
  "https://hnrss.org/newest?q=security",          # HN Security (newest)
  "https://hnrss.org/frontpage?q=vulnerability"   # HN Vulnerability (frontpage)
]

import os

# --- 2. File Paths ---
ARTICLES_DB_FILE = 'demo/data/cyber_articles_db.json'
RUN_SHEET_FILE = 'demo/data/cyber_run_sheet.json'
ENHANCED_ISSUE_FILE = 'demo/data/cyber_enhanced_issue.json'
SECRETS_FILE = 'demo/secrets.json' # Re-use generic secrets file
STATS_FILE = 'demo/data/cyber_publication_stats.json'
LATEST_HTML_FILE = 'demo/output/cyber_latest.html'
LATEST_PDF_FILE = 'demo/output/cyber_latest.pdf'

# --- 3. Pipeline Settings ---
TIMEZONE = "US/Pacific"
FOUNDING_DATE = "2025-12-07"
THEME = "demo/themes/basic"
MAX_ARTICLE_LENGTH = 15000
EXPIRATION_HOURS = 48
USER_AGENT = 'Fishwrap-Cyber-Pilot/1.0 (+https://github.com/maxspevack/fishwrap)'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'zero-days': 5,
    'threat-intel': 8,
    'vulnerability-news': 10,
    'community-watch': 7
}

MIN_SECTION_SCORES = {
    'zero-days': 15000,
    'threat-intel': 10000,
    'vulnerability-news': 7000,
    'community-watch': 5000
}

# --- 5. Source Affinity (Cyber-specific) ---
SOURCE_SECTIONS = {
    'thehackernews.com': 'vulnerability-news',
    'www.cisa.gov': 'threat-intel',
    'krebsonsecurity.com': 'threat-intel',
    'www.bleepingcomputer.com': 'vulnerability-news',
    'hnrss.org': 'community-watch'
}

# --- 6. Classification Keywords ---
KEYWORDS = {
    'zero-days': ['zero-day', '0day', 'exploit', 'CVE-\d{4}-\d{4,}', 'critical vulnerability'],
    'threat-intel': ['APT', 'threat actor', 'campaign', 'advisory', 'alert', 'patch tuesday', 'ransomware'],
    'vulnerability-news': ['vulnerability', 'bug', 'flaw', 'fix', 'patch', 'disclosure', 'research'],
    'community-watch': ['tool', 'github', 'poc', 'discussion', 'opinion', 'analysis', 'how-to']
}

# --- 7. Editorial Policies ---
BOOST_UNIT_VALUE = 500
FUZZY_BOOST_MULTIPLIER = 2

SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0, 'score_weight': 1.0, 'comment_weight': 1.5},
    'static':  {'base_boosts': 10, 'score_weight': 0, 'comment_weight': 0},
}

EDITORIAL_POLICIES = [
    # Explicit boosts for critical keywords
    {'type': 'keyword_boost', 'phrases': ['zero-day', 'CVE-', 'exploit', 'ransomware attack'], 'boosts': 5},
    {'type': 'keyword_boost', 'phrases': ['critical vulnerability', 'APT', 'state-sponsored'], 'boosts': 3},

    # Penalties
    {'type': 'keyword_penalty', 'phrases': ['marketing', 'webinar', 'product launch', 'new feature'], 'boosts': -10},
    {'type': 'domain_penalty', 'domains': ['youtube.com', 'youtu.be'], 'boosts': -5}
]

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'zero-days', 'title': '🚨 Zero-Days & Critical Exploits', 'description': 'Immediate threats and active exploitation.'},
    {'id': 'threat-intel', 'title': 'Threat Intelligence', 'description': 'Major advisories, APT activity, and campaign analysis.'},
    {'id': 'vulnerability-news', 'title': 'Vulnerability News', 'description': 'Latest CVEs, research, and patch releases.'},
    {'id': 'community-watch', 'title': 'Community Watch', 'description': 'Discussions, tools, and deeper analysis from the community.'}
]

# --- 9. Visual Formatting Thresholds ---
VISUAL_THRESHOLDS = {
    'zero-days':         {'lead': 20000, 'feature': 15000},
    'threat-intel':      {'lead': 15000, 'feature': 10000},
    'vulnerability-news':{'lead': 10000, 'feature': 7000},
    'community-watch':   {'lead': 8000,  'feature': 5000}
}