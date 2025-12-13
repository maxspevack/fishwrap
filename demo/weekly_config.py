# Weekly Config (The Sunday Edition)
import os

# --- 2. File Paths ---
# Reuse the seeded history
DATABASE_URL = 'sqlite:///demo/data/test_history.db' 
ARTICLES_DB_FILE = 'demo/data/test_history.json'
RUN_SHEET_FILE = 'demo/data/weekly_run_sheet.json'
ENHANCED_ISSUE_FILE = 'demo/data/weekly_enhanced.json'
SECRETS_FILE = 'demo/secrets.json'
LATEST_HTML_FILE = 'demo/output/weekly_index.html'

# --- 3. Pipeline Settings ---
TIMEZONE = "UTC"
FOUNDING_DATE = "2025-12-07"
THEME = "demo/themes/basic"
MAX_ARTICLE_LENGTH = 15000
EXPIRATION_HOURS = 168 # 7 Days
USER_AGENT = 'Fishwrap-Weekly/1.0'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'news': 5,
    'tech': 5,
    'sports': 5,
    'culture': 5
}

MIN_SECTION_SCORES = {
    'news': 5000, # Only Gold/Platinum
    'tech': 5000,
    'sports': 5000,
    'culture': 5000
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
    {'id': 'news', 'title': 'News', 'description': 'The Week in News'},
    {'id': 'tech', 'title': 'Tech', 'description': 'The Week in Tech'},
    {'id': 'sports', 'title': 'Sports', 'description': 'The Week in Sports'},
    {'id': 'culture', 'title': 'Culture', 'description': 'The Week in Culture'}
]

# --- 9. Visual Formatting Thresholds ---
VISUAL_THRESHOLDS = {}
