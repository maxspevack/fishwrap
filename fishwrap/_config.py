import os
import sys

# --- 1. Feeds (Sources) ---
# Intentionally empty in the core engine. Must be provided by config.
FEEDS = []

# --- 2. File Paths ---
# Default placeholders. Should be overridden by config.
ARTICLES_DB_FILE = 'articles_db.json' # Deprecated, kept for legacy ref
DATABASE_URL = 'sqlite:///newsroom.db'
RUN_SHEET_FILE = 'run_sheet.json'
ENHANCED_ISSUE_FILE = 'enhanced_issue.json'
SECRETS_FILE = 'secrets.json'
STATS_FILE = 'publication_stats.json'
LATEST_HTML_FILE = 'index.html'
LATEST_PDF_FILE = 'edition.pdf'

# --- 3. Pipeline Settings ---
TIMEZONE = "UTC"
FOUNDING_DATE = "2024-01-01"
THEME = "basic" 
MAX_ARTICLE_LENGTH = 10000
EXPIRATION_HOURS = 24
USER_AGENT = 'Fishwrap/1.0 (+https://github.com/maxspevack/fishwrap)'

# --- 4. Editor Settings ---
EDITION_SIZE = {}
MIN_SECTION_SCORES = {}

# --- 5. Source Affinity ---
SOURCE_SECTIONS = {}

# --- 6. Classification Keywords ---
KEYWORDS = {}

# --- 7. Editorial Policies ---
BOOST_UNIT_VALUE = 100
FUZZY_BOOST_MULTIPLIER = 1.5
SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0,  'score_weight': 1.0, 'comment_weight': 1.0},
    'static':  {'base_boosts': 10, 'score_weight': 0,   'comment_weight': 0},
}
EDITORIAL_POLICIES = []

# --- 8. Printer Settings ---
SECTIONS = []

# --- 9. Visual Thresholds ---
VISUAL_THRESHOLDS = {}

# -----------------------------------------------------------------------------
# DYNAMIC CONFIG LOADING
# -----------------------------------------------------------------------------
# If FISHWRAP_CONFIG is set in the environment, load it and override these values.
config_path = os.environ.get('FISHWRAP_CONFIG')
if config_path:
    if os.path.exists(config_path):
        # print(f"[CONFIG] Loading external config from: {config_path}")
        try:
            # Create a namespace for execution and inject __file__
            config_globals = {'__file__': config_path}
            
            with open(config_path, 'r') as f:
                exec(f.read(), config_globals)
            
            # Update local globals with values from the config
            for k, v in config_globals.items():
                if not k.startswith('__'):
                    globals()[k] = v
                    
        except Exception as e:
            print(f"[CONFIG] Error loading {config_path}: {e}")
            sys.exit(1)
    else:
        print(f"[CONFIG] Warning: FISHWRAP_CONFIG set to {config_path} but file not found.")
