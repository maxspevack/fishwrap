# --- 1. Feeds (Sources) ---
FEEDS = [
  "https://cms.zerohedge.com/fullrss2.xml",
  "https://defector.com/feed",
  "https://feeds.feedburner.com/americanthinker_articles",
  "https://feeds.feedburner.com/americanthinker_blog",
  "https://feeds.feedburner.com/breitbart",
  "https://feeds.feedburner.com/foxnews/latest",
  "https://hnrss.org/bestcomments",
  "https://hnrss.org/frontpage?comments=25",
  "https://justthenews.com/rss.xml",
  "https://lwn.net/headlines/full_text?key=6804e49d958d5519",
  "https://newsbusters.org/blog/feed",
  "https://nypost.com/opinion/feed/",
  "https://nypost.com/politics/feed/",
  "https://old.reddit.com/r/Conservative.json",
  "https://old.reddit.com/r/cfb.json",
  "https://old.reddit.com/r/movies.json",
  "https://old.reddit.com/r/nfl.json",
  "https://old.reddit.com/r/sports.json",
  "https://old.reddit.com/r/technology.json",
  "https://old.reddit.com/r/television.json",
  "https://pagesix.com/feed/",
  "https://rantingly.com/feed/",
  "https://reason.com/latest/feed/",
  "https://redstate.com/feed/",
  "https://thepostmillennial.com/index.rss"
]

# --- 2. File Paths ---
ARTICLES_DB_FILE = 'fishwrap/articles_db.json'
RUN_SHEET_FILE = 'fishwrap/run_sheet.json'
ENHANCED_ISSUE_FILE = 'fishwrap/enhanced_issue.json'
SECRETS_FILE = 'fishwrap/secrets.json'
STATS_FILE = 'fishwrap/publication_stats.json'
LATEST_HTML_FILE = 'fishwrap/latest.html'
LATEST_PDF_FILE = 'fishwrap/latest.pdf'

# --- 3. Pipeline Settings ---
TIMEZONE = "US/Pacific"
FOUNDING_DATE = "2025-12-07"
MAX_ARTICLE_LENGTH = 15000
EXPIRATION_HOURS = 24
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'news': 25,
    'sports': 25,
    'tech': 15,
    'culture': 15 
}

MIN_SECTION_SCORES = { # Minimum impact_score to be included in the edition, per section
    'news': 7500,
    'sports': 3000,
    'tech': 2000,
    'culture': 2000 
}

# --- 5. Source Affinity (Soft Defaults) ---
SOURCE_SECTIONS = {
    # Sports
    'defector.com': 'sports',
    'old.reddit.com/r/nfl': 'sports',
    'old.reddit.com/r/cfb': 'sports',
    'old.reddit.com/r/sports': 'sports',
    
    # Tech
    'old.reddit.com/r/technology': 'tech',
    'lwn.net': 'tech',
    'hnrss': 'tech',
    
    # Culture
    'pagesix.com': 'culture',
    'old.reddit.com/r/movies': 'culture',
    'old.reddit.com/r/television': 'culture',
    
    # News (Conservative/Political/General)
    'zerohedge': 'news',
    'breitbart': 'news',
    'thepostmillennial': 'news',
    'rantingly': 'news',
    'reason.com': 'news',
    'justthenews': 'news',
    'foxnews': 'news',
    'redstate': 'news',
    'nypost': 'news',
    'americanthinker': 'news',
    'newsbusters': 'news',
    'old.reddit.com/r/Conservative': 'news'
}

# --- 6. Classification Keywords ---
KEYWORDS = {
    'news': [
        'government', 'policy', 'law', 'court', 'crime', 'police', 'protest', 'scandal',
        'biden', 'trump', 'congress', 'senate', 'house', 'democrat', 'republican', 'gop',
        'election', 'vote', 'campaign', 'poll', 'candidate', 'ballot', 'debate',
        'war', 'military', 'ukraine', 'russia', 'israel', 'gaza', 'china', 'iran', 'conflict',
        'economy', 'inflation', 'market', 'stock', 'bank', 'finance', 'trade', 'tariff', 'tax',
        'border', 'immigration', 'migrant', 'illegal', 'alien', 'deported', 'arrested',
        'judge', 'ruling', 'scotus', 'doj', 'fbi', 'cia', 'investigation',
        'mayor', 'mayoral', 'governor', 'state'
    ],
    'sports': [
        'nfl', 'nba', 'mlb', 'nhl', 'cfb', 'football', 'basketball', 'baseball', 'hockey', 'soccer',
        'team', 'coach', 'player', 'athlete', 'roster', 'standings', 'rankings', 'stats',
        'championship', 'tournament', 'playoff', 'final', 'medal', 'trophy', 'cup',
        'draft', 'trade', 'contract', 'signing', 'transfer', 'portal',
        'formula 1', 'racing', 'driver', 'grand prix', 'f1',
        'olympic', 'wrestle', 'ufc', 'boxing', 'fifa', 'uefa'
    ],
    'tech': [
        'technology', 'tech', 'software', 'hardware', 'code', 'programming', 'developer',
        'ai', 'artificial intelligence', 'chatgpt', 'llm', 'model', 'machine learning',
        'crypto', 'bitcoin', 'ethereum', 'blockchain', 'wallet', 'gemini', 'fedora',
        'security', 'hacker', 'exploit', 'vulnerability', 'breach', 'privacy', 'cyber',
        'startup', 'venture', 'funding', 'ipo', 'acquisition', 'merger',
        'google', 'apple', 'microsoft', 'amazon', 'meta', 'facebook', 'twitter', 'x.com', 'tesla',
        'linux', 'open source', 'kernel', 'browser', 'app', 'device', 'chip', 'semiconductor'
    ],
    'culture': [
        'movie', 'film', 'cinema', 'theatre', 'director', 'actor', 'actress', 'cast',
        'tv', 'series', 'show', 'episode', 'streaming', 'netflix', 'hbo', 'disney', 'hulu',
        'music', 'album', 'song', 'artist', 'band', 'concert', 'tour', 'grammy',
        'celebrity', 'fame', 'gossip', 'rumor', 'scandal', 'fashion', 'trend', 'style',
        'book', 'novel', 'author', 'writing', 'publishing',
        'review', 'interview', 'opinion', 'commentary', 'culture', 'society'
    ]
}

# --- 6. Scoring Settings ---
BOOST_UNIT_VALUE = 500 # Points per boost unit
FUZZY_BOOST_MULTIPLIER = 2 # Multiplier for fuzzy match boosts (2 * 500 = 1000)

SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0,  'score_weight': 1.0, 'comment_weight': 2.0},
    'static':  {'base_boosts': 13, 'score_weight': 0,   'comment_weight': 0}, # 13 * 500 = 6500 baseline
}

# --- 7. Editorial Policies ---
EDITORIAL_POLICIES = [
    # Source Boosts
    {'type': 'source_boost', 'match': 'defector.com', 'boosts': 3},
    {'type': 'source_boost', 'match': 'lwn.net', 'boosts': 1},
    
    # Topic/Content Boosts (Sports)
    {'type': 'keyword_boost', 'phrases': ["49ers"], 'boosts': 1},
    {'type': 'keyword_boost', 'phrases': ["NFL"], 'boosts': 1},
    {'type': 'keyword_boost', 'phrases': ["Playoff", "Playoffs"], 'boosts': 1},
    {'type': 'content_boost', 'phrases': ["Drew Magary"], 'boosts': 1},
    
    # Political Figures (+1)
    {'type': 'keyword_boost', 'phrases': [
        "Trump", "Biden", "Rubio", "Leavitt", 
        "Carlson", "Musk"
    ], 'boosts': 1},

    # Political Topics (+1)
    {'type': 'keyword_boost', 'phrases': [
        "GOP", "Epstein", "Election", "Supreme Court", 
        "Executive Order", "White House", "DOGE", "Midterm"
    ], 'boosts': 1},

    # Global Affairs & Policy (+1)
    {'type': 'keyword_boost', 'phrases': [
        "Immigration", "Border", "Israel", "Ukraine", "Russia", "MAGA"
    ], 'boosts': 1},

    # Economics (+1)
    {'type': 'keyword_boost', 'phrases': [
        "Economy", "Tariff", "Inflation"
    ], 'boosts': 1},
    
    # Penalties
    {'type': 'keyword_penalty', 'phrases': [
        "open thread", 
        "join me in donating to reason", 
        "today in supreme court history",
        "weekend wrapup",
        "[video]", "watch:", "video:", "(video)", "vid:", "watch --",
        "new comment by", "cardi b", "50% off", "luxury gifts for women",
        "crossword", "security updates for"
    ], 'boosts': -20},
    
    {'type': 'domain_penalty', 'domains': [
        'youtube.com', 'youtu.be', 'vimeo.com', 'bitchute.com', 'rumble.com'
    ], 'boosts': -10},
]

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'news', 'title': 'News', 'description': 'Scoops, Scandals, & Scoundrels'},
    {'id': 'sports', 'title': 'Sports', 'description': 'The Toy Department'},
    {'id': 'tech', 'title': 'Technology', 'description': 'Indistinguishable From Magic'},
    {'id': 'culture', 'title': 'Culture', 'description': 'Bread & Circuses'}
]

# --- 9. Visual Formatting Thresholds ---
# Maps User Terms to Scores:
# "Lead" -> CSS .feature (Big, span 2 columns)
# "Feature" -> CSS .standard (Normal card with excerpt)
# "Standard" -> CSS .compact (Small, list item)
VISUAL_THRESHOLDS = {
    'news':    {'lead': 9000,  'feature': 8000},
    'tech':    {'lead': 9000,  'feature': 8000},
    'culture': {'lead': 9000,  'feature': 8000},
    'sports':  {'lead': 15000, 'feature': 10000}
}
