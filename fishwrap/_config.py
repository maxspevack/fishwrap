import os
import sys

# --- 1. Default Feeds (Generic Demo) ---
FEEDS = [
  # News
  "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
  "https://feeds.bbci.co.uk/news/world/rss.xml",
  
  # Sports
  "https://www.espn.com/espn/rss/news",
  "https://sports.yahoo.com/rss/",
  
  # Tech
  "https://www.theverge.com/rss/index.xml",
  "https://feeds.arstechnica.com/arstechnica/index",
  
  # Culture
  "https://www.rollingstone.com/feed",
  "https://variety.com/feed"
]

# --- 2. File Paths ---
# By default, data lives in the current working directory
ARTICLES_DB_FILE = 'articles_db.json'
RUN_SHEET_FILE = 'run_sheet.json'
ENHANCED_ISSUE_FILE = 'enhanced_issue.json'
SECRETS_FILE = 'secrets.json'
STATS_FILE = 'publication_stats.json'
LATEST_HTML_FILE = 'latest.html'
LATEST_PDF_FILE = 'latest.pdf'

# --- 3. Pipeline Settings ---
TIMEZONE = "UTC"
FOUNDING_DATE = "2024-01-01"
THEME = "basic" # Points to fishwrap/themes/basic
MAX_ARTICLE_LENGTH = 10000
EXPIRATION_HOURS = 24
USER_AGENT = 'Fishwrap/1.0 (+https://github.com/maxspevack/fishwrap)'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'news': 10,
    'sports': 5,
    'tech': 10,
    'culture': 5 
}

MIN_SECTION_SCORES = {
    'news': 1000,
    'sports': 1000,
    'tech': 1000,
    'culture': 1000 
}

# --- 5. Source Affinity ---
SOURCE_SECTIONS = {
    'rss.nytimes.com': 'news',
    'feeds.bbci.co.uk': 'news',
    'www.espn.com': 'sports',
    'sports.yahoo.com': 'sports',
    'www.theverge.com': 'tech',
    'feeds.arstechnica.com': 'tech',
    'www.rollingstone.com': 'culture',
    'variety.com': 'culture'
}

# --- 6. Classification Keywords ---
KEYWORDS = {
    'news': ['government', 'election', 'war', 'economy', 'world', 'politics', 'senate', 'biden', 'trump'],
    'sports': ['football', 'basketball', 'soccer', 'tennis', 'nfl', 'nba', 'mlb', 'league', 'game', 'score'],
    'tech': ['software', 'ai', 'crypto', 'linux', 'apple', 'google', 'microsoft', 'app', 'device', 'code'],
    'culture': ['movie', 'music', 'book', 'art', 'celebrity', 'film', 'star', 'hollywood', 'album']
}

# --- 7. Editorial Policies ---
# (Empty by default)
BOOST_UNIT_VALUE = 100
FUZZY_BOOST_MULTIPLIER = 1.5
SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0,  'score_weight': 1.0, 'comment_weight': 1.0},
    'static':  {'base_boosts': 10, 'score_weight': 0,   'comment_weight': 0},
}
EDITORIAL_POLICIES = []

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'news', 'title': 'News', 'description': 'World Events'},
    {'id': 'sports', 'title': 'Sports', 'description': 'Games & Scores'},
    {'id': 'tech', 'title': 'Technology', 'description': 'Computing & Science'},
    {'id': 'culture', 'title': 'Culture', 'description': 'Arts & Entertainment'}
]

# --- 9. Visual Thresholds ---
VISUAL_THRESHOLDS = {
    'news':    {'lead': 5000,  'feature': 3000},
    'tech':    {'lead': 5000,  'feature': 3000},
    'culture': {'lead': 5000,  'feature': 3000},
    'sports':  {'lead': 5000, 'feature': 3000}
}

# -----------------------------------------------------------------------------
# DYNAMIC CONFIG LOADING
# -----------------------------------------------------------------------------
# If FISHWRAP_CONFIG is set in the environment, load it and override these values.
config_path = os.environ.get('FISHWRAP_CONFIG')
if config_path:
    if os.path.exists(config_path):
        # print(f"[CONFIG] Loading external config from: {config_path}")
        
        # We use exec to run the config file in this namespace
        # This allows the config file to access 'os', 'sys', etc if needed
        # and simply set variables like THEME = "vintage"
        try:
            with open(config_path, 'r') as f:
                exec(f.read())
        except Exception as e:
            print(f"[CONFIG] Error loading {config_path}: {e}")
            sys.exit(1)
    else:
        print(f"[CONFIG] Warning: FISHWRAP_CONFIG set to {config_path} but file not found.")