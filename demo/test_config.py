# Test Config for Weekly Logic Verification
import os

# --- 2. File Paths ---
DATABASE_URL = 'sqlite:///demo/data/test_history.db'
ARTICLES_DB_FILE = 'demo/data/test_history.json' # Legacy
RUN_SHEET_FILE = 'demo/data/test_run_sheet.json'
ENHANCED_ISSUE_FILE = 'demo/data/test_enhanced.json'
SECRETS_FILE = 'demo/secrets.json'
LATEST_HTML_FILE = 'demo/output/test_index.html'

# --- 3. Pipeline Settings ---
TIMEZONE = "UTC"
FOUNDING_DATE = "2025-12-07"
THEME = "demo/themes/basic"
MAX_ARTICLE_LENGTH = 15000
EXPIRATION_HOURS = 24 # Standard Daily window
USER_AGENT = 'Fishwrap-Test/1.0'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'news': 10,
    'tech': 10,
    'sports': 5,
    'culture': 5
}

MIN_SECTION_SCORES = {
    'news': 1000,
    'tech': 1000,
    'sports': 1000,
    'culture': 1000
}

# --- 5. Source Affinity ---
SOURCE_SECTIONS = {}

# --- 6. Classification Keywords ---
KEYWORDS = { 'news': [], 'tech': [], 'sports': [], 'culture': [] }

# --- 7. Editorial Policies ---
BOOST_UNIT_VALUE = 500
SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0, 'score_weight': 1.0, 'comment_weight': 1.0},
    'static':  {'base_boosts': 10, 'score_weight': 0, 'comment_weight': 0},
}
EDITORIAL_POLICIES = []

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'news', 'title': 'News', 'description': 'Test News'},
    {'id': 'tech', 'title': 'Tech', 'description': 'Test Tech'},
    {'id': 'sports', 'title': 'Sports', 'description': 'Test Sports'},
    {'id': 'culture', 'title': 'Culture', 'description': 'Test Culture'}
]

# --- 9. Visual Formatting Thresholds ---
VISUAL_THRESHOLDS = {}
