import os

# --- The Showrunner Config (Christina Edition v1.3) ---

FEEDS = [
    # --- The Primary Intelligence (RSS) ---
    "https://tvline.com/feed",
    "https://www.cinemablend.com/rss/topic/television",
    "https://telltaletv.com/feed/",
    "https://variety.com/feed",
    "https://deadline.com/feed",
    "https://fangirlish.com/tag/ncis/feed/",
    "https://fangirlish.com/tag/bridgerton/feed/",
    "https://fangirlish.com/tag/outlander/feed/",
    "https://fangirlish.com/tag/virgin-river/feed/",
    "https://fangirlish.com/tag/sweet-magnolias/feed/",
    
    # --- Reviews & Recaps (New) ---
    "https://www.vulture.com/tv/rss.xml",
    "https://www.avclub.com/article-category/tv/rss",
    "https://www.primetimer.com/rss/news",
    
    # --- The Deep State (Reddit RSS) ---
    "https://www.reddit.com/r/NCIS/.rss",
    "https://www.reddit.com/r/BridgertonNetflix/.rss",
    "https://www.reddit.com/r/GreysAnatomy/.rss",
    "https://www.reddit.com/r/Outlander/.rss",
    "https://www.reddit.com/r/VirginRiverNetflix/.rss",
    "https://www.reddit.com/r/SweetMagnolias/.rss",
    "https://www.reddit.com/r/TheDiplomat/.rss"
]

# --- File Paths ---
DATABASE_URL = 'sqlite:///demo/data/showrunner.db'
ARTICLES_DB_FILE = 'demo/data/showrunner_articles.json'
RUN_SHEET_FILE = 'demo/data/showrunner_run_sheet.json'
LATEST_HTML_FILE = 'demo/output/showrunner_edition.html'
LATEST_PDF_FILE = 'demo/output/showrunner_edition.pdf'

# --- Theme ---
THEME = "demo/themes/showrunner" 

# --- Editorial Sections ---
SECTIONS = [
    {'id': 'procedural', 'title': 'The Situation Room', 'description': 'Procedurals & Justice: NCIS, JAG, The Pitt, Tracker.'},
    {'id': 'drama', 'title': 'Lady Whistledown’s Desk', 'description': 'Scandal, Bridgerton, Grey’s, The Diplomat.'},
    {'id': 'cozy', 'title': 'Comfort & Coffee', 'description': 'Virgin River, Sweet Magnolias, Outlander.'},
    {'id': 'legacy', 'title': 'The Legacy File', 'description': 'Quantum Leap, General Hospital, and Deep Lore.'}
]

# --- Editor Configuration ---
EDITION_SIZE = {
    'procedural': 12, # Increased for more coverage
    'drama': 12,      # Increased for more coverage
    'cozy': 8,
    'legacy': 6
}

# ZERO THRESHOLD to force population
MIN_SECTION_SCORES = {
    'procedural': 0,
    'drama': 0,
    'cozy': 0,
    'legacy': 0
}

# --- Source Affinity (Forced Classification) ---
# This ensures that even if keywords fail, the source itself routes the content.
SOURCE_SECTIONS = {
    'reddit.com/r/NCIS': 'procedural',
    'reddit.com/r/BridgertonNetflix': 'drama',
    'reddit.com/r/GreysAnatomy': 'drama',
    'reddit.com/r/TheDiplomat': 'drama',
    'reddit.com/r/Outlander': 'cozy',
    'reddit.com/r/VirginRiverNetflix': 'cozy',
    'reddit.com/r/SweetMagnolias': 'cozy',
    'fangirlish.com/tag/ncis': 'procedural',
    'fangirlish.com/tag/bridgerton': 'drama',
    'fangirlish.com/tag/outlander': 'cozy'
}

# --- Keyword Whitelist (Fallback for General Feeds) ---
KEYWORDS = {
    'procedural': [
        'NCIS', 'Mark Harmon', 'JAG', 'The Pitt', 'Tracker', 'Justin Hartley', 'Leroy Jethro Gibbs', 
        'Sean Murray', 'Wilmer Valderrama', 'Cote de Pablo', 'Michael Weatherly', 'CBS', 'Procedural',
        'Crime', 'Investigation', 'Navy', 'Marine', 'Episode', 'Recap', 'Review', 'Noah Wyle'
    ],
    'drama': [
        'Bridgerton', 'Scandal', 'The Diplomat', 'Grey\'s Anatomy', 'Shonda Rhimes', 'Lady Whistledown',
        'Ellen Pompeo', 'Keri Russell', 'Shondaland', 'Netflix', 'Romance', 'Drama', 'Period Piece',
        'Regency', 'Meredith Grey', 'Season', 'Series', 'Recap', 'Review', 'Keri Russell'
    ],
    'cozy': [
        'Virgin River', 'Sweet Magnolias', 'Outlander', 'Sam Heughan', 'Caitriona Balfe', 
        'Alexandra Breckenridge', 'Martin Henderson', 'Netflix', 'Hallmark', 'Comfort TV',
        'Small Town', 'Romance', 'Recap', 'Review'
    ],
    'legacy': [
        'Quantum Leap', 'General Hospital', 'Scott Bakula', 'Legacy', 'Returns', 'Reboot', 
        'Soap Opera', 'ABC', 'Hospital', 'Daytime', 'Soap'
    ]
}

# Editorial Policies
EDITORIAL_POLICIES = [
    {'type': 'keyword_boost', 'phrases': ['Mark Harmon', 'NCIS: Origins', 'Whistledown', 'Tony & Ziva'], 'boosts': 500},
    {'type': 'keyword_boost', 'phrases': ['Season Renewal', 'Release Date', 'Returning', 'The Pitt'], 'boosts': 200},
    {'type': 'keyword_boost', 'phrases': ['Review', 'Recap', 'Explained'], 'boosts': 100}, # Boost professional analysis
    {'type': 'keyword_penalty', 'phrases': ['Top 10', 'Best deals', 'Amazon', 'Gift Guide'], 'boosts': -50}
]

# Standard overrides
TIMEZONE = "US/Pacific"
FOUNDING_DATE = "2026-02-02"
MAX_ARTICLE_LENGTH = 15000
EXPIRATION_HOURS = 168 # 1 Week lookback to ensure content
USER_AGENT = 'Fishwrap-Showrunner/1.3 (+https://github.com/maxspevack/fishwrap)'