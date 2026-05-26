import os

# --- The Showrunner Config (Christina Edition v1.5) ---

FEEDS = [
    # --- The Primary Intelligence (RSS) ---
    "https://tvline.com/feed",
    "https://www.cinemablend.com/rss/topic/television",
    "https://telltaletv.com/feed/",
    "https://variety.com/v/tv/feed",
    "https://deadline.com/v/tv/feed/",
    "https://www.hollywoodreporter.com/c/tv/feed/",
    "https://www.indiewire.com/t/tv/feed/",
    "https://www.thewrap.com/feed",
    "https://www.tvinsider.com/feed/",
    "https://decider.com/feed/",
    "https://www.rollingstone.com/tv-movies/feed/",
    "https://fangirlish.com/tag/ncis/feed/",
    "https://fangirlish.com/tag/bridgerton/feed/",
    "https://fangirlish.com/tag/outlander/feed/",
    "https://fangirlish.com/tag/virgin-river/feed/",
    "https://fangirlish.com/tag/sweet-magnolias/feed/",

    # --- Reviews & Recaps ---
    "https://feeds.feedburner.com/Vulture",
    "https://www.avclub.com/article-category/tv/rss",
    "https://www.tomandlorenzo.com/category/television/feed/",

    # --- The Insider (Veteran Beat Reporter) ---
    "https://mattmitovich.ghost.io/rss/",

    # --- The Deep State (Reddit RSS) ---
    "https://www.reddit.com/r/NCIS/.rss",
    "https://www.reddit.com/r/BridgertonNetflix/.rss",
    "https://www.reddit.com/r/GreysAnatomy/.rss",
    "https://www.reddit.com/r/Outlander/.rss",
    "https://www.reddit.com/r/Homeland/.rss",
    "https://www.reddit.com/r/VirginRiverNetflix/.rss",
    "https://www.reddit.com/r/SweetMagnolias/.rss",
    "https://www.reddit.com/r/TheDiplomat/.rss",
    "https://www.reddit.com/r/ThePitt/.rss"
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
    {'id': 'procedural', 'title': 'The Situation Room', 'description': 'Badges, scrubs, and bullpens: the NCIS-verse, The Pitt, Tracker, Sheriff Country, Criminal Minds.'},
    {'id': 'drama', 'title': 'Lady Whistledown’s Desk', 'description': 'Bridgerton, Grey’s Anatomy, The Diplomat, Scandal — Shondaland and the ton.'},
    {'id': 'cozy', 'title': 'Comfort & Coffee', 'description': 'Virgin River, Sweet Magnolias, Outlander, When Calls the Heart — small towns and big feelings.'},
    {'id': 'legacy', 'title': 'The Legacy File', 'description': 'Quantum Leap, General Hospital, Daytime soaps, and the revival beat.'}
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
    'reddit.com/r/ThePitt': 'procedural',
    'reddit.com/r/BridgertonNetflix': 'drama',
    'reddit.com/r/GreysAnatomy': 'drama',
    'reddit.com/r/TheDiplomat': 'drama',
    'reddit.com/r/Outlander': 'cozy',
    'reddit.com/r/VirginRiverNetflix': 'cozy',
    'reddit.com/r/SweetMagnolias': 'cozy',
    'fangirlish.com/tag/ncis': 'procedural',
    'fangirlish.com/tag/bridgerton': 'drama',
    'fangirlish.com/tag/outlander': 'cozy',
    'fangirlish.com/tag/virgin-river': 'cozy',
    'fangirlish.com/tag/sweet-magnolias': 'cozy'
}

# --- Keyword Whitelist (Fallback for General Feeds) ---
# NOTE: keywords are intentionally lowercase. The classifier in editor.py
# lowercases the article text blob but matches keywords as-given, so any
# mixed-case keyword silently fails. Keep this list lowercase until the
# engine is patched to normalize both sides.
KEYWORDS = {
    'procedural': [
        # NCIS-verse
        'ncis', 'ncis: origins', 'ncis: sydney', 'ncis: hawai\'i', 'ncis-verse',
        'mark harmon', 'sean murray', 'wilmer valderrama', 'cote de pablo',
        'michael weatherly', 'brian dietzen', 'david mccallum',
        'leroy jethro gibbs', 'gibbs', 'tony dinozzo', 'ziva david',
        # The Pitt
        'the pitt', 'noah wyle', 'robby robinavitch',
        # Tracker
        'tracker', 'justin hartley', 'colter shaw',
        # The CBS/network procedural slate
        'jag', 'sheriff country', 'the hunting party', 'criminal minds',
        'the rookie', 'fbi', 'will trent', 'elsbeth', 'matlock', 'ghosts',
        # Genre signal
        'procedural'
    ],
    'drama': [
        # Bridgerton-verse
        'bridgerton', 'queen charlotte', 'lady whistledown',
        'sophie beckett', 'benedict bridgerton', 'penelope featherington',
        'colin bridgerton', 'anthony bridgerton', 'eloise bridgerton',
        'daphne bridgerton', 'kate sharma', 'lady danbury',
        'nicola coughlan', 'luke newton', 'phoebe dynevor',
        'jonathan bailey', 'simone ashley', 'jess brownell', 'chris van dusen',
        # Grey's Anatomy / Station 19
        'grey\'s anatomy', 'station 19', 'meredith grey', 'grey sloan',
        'ellen pompeo', 'patrick dempsey', 'sandra oh',
        # Scandal / Shondaland
        'scandal', 'olivia pope', 'kerry washington', 'shonda rhimes', 'shondaland',
        # The Diplomat
        'the diplomat', 'kate wyler', 'hal wyler', 'keri russell',
        # Genre signal
        'regency', 'period piece'
    ],
    'cozy': [
        # Virgin River
        'virgin river', 'mel monroe', 'jack sheridan',
        'alexandra breckenridge', 'martin henderson',
        # Sweet Magnolias
        'sweet magnolias', 'serenity', 'joanna garcia swisher',
        'brooke elliott', 'heather headley',
        # Outlander-verse
        'outlander', 'outlander: blood of my blood',
        'jamie fraser', 'claire fraser', 'lallybroch',
        'sam heughan', 'caitriona balfe',
        # Adjacent Hallmark / cozy slate
        'when calls the heart', 'when hope calls', 'the way home',
        'chesapeake shores',
        # Genre signal
        'hallmark', 'comfort tv', 'small town'
    ],
    'legacy': [
        # Quantum Leap
        'quantum leap', 'scott bakula', 'dean stockwell', 'sam beckett',
        # Daytime soaps
        'general hospital', 'days of our lives', 'the young and the restless',
        'the bold and the beautiful', 'port charles',
        # Genre signal
        'soap opera', 'daytime', 'daytime emmy', 'soap',
        # Industry beat
        'revival', 'reboot', 'classic tv'
    ]
}

# Editorial Policies
# Note: scoring.py lowercases phrases before matching, so case here is cosmetic.
EDITORIAL_POLICIES = [
    # Tier 1: Christina's named obsessions — push to the top of the run sheet.
    {'type': 'keyword_boost',
     'phrases': ['Mark Harmon', 'NCIS: Origins', 'Tony DiNozzo', 'Ziva David',
                 'Whistledown', 'Sophie Beckett', 'Benedict Bridgerton',
                 'Sam Heughan', 'Caitriona Balfe'],
     'boosts': 500},

    # Tier 2: News-of-the-show — premieres, finales, renewals, casting.
    {'type': 'keyword_boost',
     'phrases': ['Season Renewal', 'Renewed', 'Cancelled', 'Release Date',
                 'Returning', 'Season Premiere', 'Season Finale',
                 'First Look', 'Trailer', 'Casting News', 'The Pitt'],
     'boosts': 200},

    # Tier 3: Professional analysis beats commodity coverage.
    {'type': 'keyword_boost',
     'phrases': ['Review', 'Recap', 'Explained', 'Ending Explained', 'Breakdown'],
     'boosts': 100},

    # Bury commerce, listicles, and SEO bait.
    {'type': 'keyword_penalty',
     'phrases': ['Top 10', 'Top 5', 'Best Deals', 'Amazon Deal', 'Gift Guide',
                 'Where to Stream', 'Streaming Deal', 'Coupon', 'Discount Code',
                 'Black Friday', 'Affiliate'],
     'boosts': -50}
]

# Standard overrides
TIMEZONE = "America/Los_Angeles"
FOUNDING_DATE = "2026-02-02"
MAX_ARTICLE_LENGTH = 15000
EXPIRATION_HOURS = 168 # 1 Week lookback to ensure content
USER_AGENT = 'Fishwrap-Showrunner/1.5 (+https://github.com/maxspevack/fishwrap)'
