import os
import sys

# --- 1. Default Feeds (Generic Demo) ---
FEEDS = [
    # --- Global News ---
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.reutersagency.com/feed/?best-regions=north-america&post_type=best",
    "https://feeds.npr.org/1001/rss.xml",
    "https://apnews.com/rss/fronts/topnews",
    "https://www.aljazeera.com/xml/rss/all.xml",
    
    # --- Technology ---
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://techcrunch.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://www.engadget.com/rss.xml",
    "https://www.polygon.com/rss/index.xml", # Gaming/Tech overlap
    "https://hnrss.org/frontpage",
    "https://old.reddit.com/r/technology.json",

    # --- Sports ---
    "https://www.espn.com/espn/rss/news",
    "https://sports.yahoo.com/rss/",
    "https://www.cbssports.com/rss/headlines/",
    "https://bleacherreport.com/articles/feed",
    "https://old.reddit.com/r/nfl.json",
    "https://old.reddit.com/r/nba.json",
    "https://old.reddit.com/r/soccer.json",

    # --- Culture & Entertainment ---
    "https://www.rollingstone.com/feed",
    "https://variety.com/feed",
    "https://pitchfork.com/feed/feed-news/rss",
    "https://gizmodo.com/rss",
    "https://mashable.com/feed",
    "https://lifehacker.com/rss",
    "https://www.avclub.com/rss",
    "https://old.reddit.com/r/movies.json",
    "https://old.reddit.com/r/books.json"
]

# --- 2. File Paths ---
ARTICLES_DB_FILE = 'demo/data/articles_db.json'
RUN_SHEET_FILE = 'demo/data/run_sheet.json'
ENHANCED_ISSUE_FILE = 'demo/data/enhanced_issue.json'
SECRETS_FILE = 'demo/secrets.json'
STATS_FILE = 'demo/data/publication_stats.json'
LATEST_HTML_FILE = 'demo/output/index.html'
LATEST_PDF_FILE = 'demo/output/edition.pdf'

# --- 3. Pipeline Settings ---
TIMEZONE = "US/Pacific"
FOUNDING_DATE = "2025-12-07"
THEME = "demo/themes/basic" 
MAX_ARTICLE_LENGTH = 12000
EXPIRATION_HOURS = 24
USER_AGENT = 'Fishwrap/1.0 (+https://github.com/maxspevack/fishwrap)'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'news': 10,
    'sports': 8,
    'tech': 10,
    'culture': 8
}

MIN_SECTION_SCORES = {
    'news': 1000,
    'sports': 1000,
    'tech': 1000,
    'culture': 1000 
}

# --- 5. Source Affinity ---
SOURCE_SECTIONS = {
    # News
    'nytimes.com': 'news',
    'bbc.co.uk': 'news',
    'reuters.com': 'news',
    'npr.org': 'news',
    'apnews.com': 'news',
    'aljazeera.com': 'news',
    
    # Tech
    'theverge.com': 'tech',
    'arstechnica.com': 'tech',
    'techcrunch.com': 'tech',
    'wired.com': 'tech',
    'engadget.com': 'tech',
    'hnrss.org': 'tech',
    'reddit.com/r/technology': 'tech',
    
    # Sports
    'espn.com': 'sports',
    'sports.yahoo.com': 'sports',
    'cbssports.com': 'sports',
    'bleacherreport.com': 'sports',
    'reddit.com/r/nfl': 'sports',
    'reddit.com/r/nba': 'sports',
    'reddit.com/r/soccer': 'sports',
    
    # Culture
    'rollingstone.com': 'culture',
    'variety.com': 'culture',
    'pitchfork.com': 'culture',
    'mashable.com': 'culture',
    'avclub.com': 'culture',
    'reddit.com/r/movies': 'culture',
    'reddit.com/r/books': 'culture'
}

# --- 6. Classification Keywords ---
KEYWORDS = {
    'news': [
        'government', 'election', 'war', 'economy', 'world', 'politics', 'senate', 'biden', 'trump', 
        'congress', 'policy', 'ukraine', 'gaza', 'israel', 'china', 'russia', 'inflation', 'market'
    ],
    'sports': [
        'football', 'basketball', 'soccer', 'tennis', 'nfl', 'nba', 'mlb', 'league', 'game', 'score', 
        'championship', 'playoff', 'trade', 'roster', 'coach', 'athlete', 'olympics'
    ],
    'tech': [
        'software', 'ai', 'crypto', 'linux', 'apple', 'google', 'microsoft', 'app', 'device', 'code', 
        'startup', 'venture', 'silicon valley', 'meta', 'amazon', 'musk', 'tesla', 'gadget'
    ],
    'culture': [
        'movie', 'music', 'book', 'art', 'celebrity', 'film', 'star', 'hollywood', 'album', 'review', 
        'fashion', 'trend', 'streaming', 'netflix', 'hbo', 'disney', 'marvel'
    ]
}

# --- 7. Editorial Policies ---
BOOST_UNIT_VALUE = 100
FUZZY_BOOST_MULTIPLIER = 1.5

SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0,  'score_weight': 1.0, 'comment_weight': 1.0},
    'static':  {'base_boosts': 10, 'score_weight': 0,   'comment_weight': 0},
}

EDITORIAL_POLICIES = [
    # Penalty for clickbait/noise
    {'type': 'keyword_penalty', 'phrases': ['top 10', 'deals', 'amazon prime day', 'coupon'], 'boosts': -20},
    {'type': 'keyword_penalty', 'phrases': ['video:', 'watch:', 'listen:'], 'boosts': -5}
]

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'news', 'title': 'News', 'description': 'World Events & Politics'},
    {'id': 'tech', 'title': 'Technology', 'description': 'The Future, Distributed.'},
    {'id': 'sports', 'title': 'Sports', 'description': 'Games & Scores'},
    {'id': 'culture', 'title': 'Culture', 'description': 'Arts & Entertainment'}
]

# --- 9. Visual Thresholds ---
VISUAL_THRESHOLDS = {
    'news':    {'lead': 8000,  'feature': 5000},
    'tech':    {'lead': 8000,  'feature': 5000},
    'culture': {'lead': 8000,  'feature': 5000},
    'sports':  {'lead': 8000, 'feature': 5000}
}