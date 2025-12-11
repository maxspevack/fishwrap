# --- 1. Feeds (Sources) ---
FEEDS = [
    # --- News & Vulnerabilities ---
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://threatpost.com/feed/",
    "https://thecyberwire.com/feeds/rss.xml",
    "https://securityaffairs.co/wordpress/feed",
    "https://therecord.media/feed",
    "https://www.helpnetsecurity.com/feed/",
    "https://grahamcluley.com/feed/",
    
    # --- Threat Intel & Vendor Research ---
    "https://research.checkpoint.com/feed/",
    "https://www.mcafee.com/blogs/other-blogs/mcafee-labs/feed/",
    "https://securelist.com/feed/", 
    "https://blog.talosintelligence.com/feeds/posts/default", 
    "https://unit42.paloaltonetworks.com/feed/",
    "https://www.mandiant.com/resources/blog/rss.xml",
    "https://www.crowdstrike.com/blog/feed/",
    "https://www.microsoft.com/security/blog/feed/",
    "https://googleprojectzero.blogspot.com/feeds/posts/default",

    # --- Government & Alerts ---
    "https://www.cisa.gov/uscert/ncas/alerts.xml",
    "https://www.cisa.gov/uscert/ncas/current-activity.xml",
    
    # --- Independent & Analysis ---
    "https://krebsonsecurity.com/feed/",
    "https://www.schneier.com/blog/atom.xml",
    "https://www.troyhunt.com/rss/",
    
    # --- Community & Signals ---
    "https://otx.alienvault.com/otxapi/pulses/subscribe/public/atom",
    "https://www.reddit.com/r/netsec.json",
    "https://www.reddit.com/r/cybersecurity.json",
    "https://hnrss.org/newest?q=security+OR+vulnerability+OR+exploit+OR+breach",
]

import os

# --- 2. File Paths ---
ARTICLES_DB_FILE = 'demo/data/cyber_articles_db.json'
RUN_SHEET_FILE = 'demo/data/cyber_run_sheet.json'
ENHANCED_ISSUE_FILE = 'demo/data/cyber_enhanced_issue.json'
SECRETS_FILE = 'demo/secrets.json' 
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

# --- 5. Source Affinity ---
SOURCE_SECTIONS = {
    'cisa.gov': 'threat-intel',
    'checkpoint.com': 'threat-intel',
    'paloaltonetworks.com': 'threat-intel',
    'mandiant.com': 'threat-intel',
    'crowdstrike.com': 'threat-intel',
    'krebsonsecurity.com': 'threat-intel',
    
    'thehackernews.com': 'vulnerability-news',
    'bleepingcomputer.com': 'vulnerability-news',
    'darkreading.com': 'vulnerability-news',
    
    'googleprojectzero': 'zero-days',
    
    'reddit.com/r/netsec': 'community-watch',
    'schneier.com': 'community-watch',
    'troyhunt.com': 'community-watch'
}

# --- 6. Classification Keywords ---
KEYWORDS = {
    'zero-days': [
        'zero-day', '0day', 'exploit', 'CVE-\d{4}-\d{4,}', 'critical vulnerability', 
        'rce', 'remote code execution', 'active exploitation', 'poc', 'proof of concept'
    ],
    'threat-intel': [
        'APT', 'threat actor', 'campaign', 'advisory', 'alert', 'malware', 'ransomware',
        'botnet', 'state-sponsored', 'espionage', 'phishing', 'indicator', 'ioc'
    ],
    'vulnerability-news': [
        'vulnerability', 'bug', 'flaw', 'fix', 'patch', 'disclosure', 'research',
        'update', 'security update', 'bypass', 'weakness'
    ],
    'community-watch': [
        'tool', 'github', 'discussion', 'opinion', 'analysis', 'how-to', 'tutorial',
        'conference', 'defcon', 'blackhat', 'bsides', 'reverse engineering'
    ]
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
    {'type': 'keyword_boost', 'phrases': ['zero-day', 'active exploitation', 'wild', 'critical'], 'boosts': 10},
    {'type': 'keyword_boost', 'phrases': ['ransomware', 'data breach', 'supply chain'], 'boosts': 5},
    {'type': 'keyword_boost', 'phrases': ['CVE-'], 'boosts': 3},

    # Boost Authoritative Sources for Signals
    {'type': 'source_boost', 'match': 'cisa.gov', 'boosts': 5},
    {'type': 'source_boost', 'match': 'googleprojectzero', 'boosts': 5},

    # Penalties
    {'type': 'keyword_penalty', 'phrases': ['marketing', 'webinar', 'product launch', 'best practice', 'whitepaper'], 'boosts': -15},
    {'type': 'keyword_penalty', 'phrases': ['buy now', 'free trial', 'promo'], 'boosts': -50},
    {'type': 'domain_penalty', 'domains': ['youtube.com', 'youtu.be'], 'boosts': -5}
]

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'zero-days', 'title': '🚨 Zero-Days & Critical Exploits', 'description': 'Immediate threats and active exploitation.'},
    {'id': 'threat-intel', 'title': 'Threat Intelligence', 'description': 'Major advisories, APT activity, and campaign analysis.'},
    {'id': 'vulnerability-news', 'title': 'Vulnerability News', 'description': 'Latest CVEs, research, and patch releases.'},
    {'id': 'community-watch', 'title': 'Community Watch', 'description': 'Discussions, tools, and deeper analysis.'}
]

# --- 9. Visual Formatting Thresholds ---
VISUAL_THRESHOLDS = {
    'zero-days':         {'lead': 20000, 'feature': 15000},
    'threat-intel':      {'lead': 15000, 'feature': 10000},
    'vulnerability-news':{'lead': 10000, 'feature': 7000},
    'community-watch':   {'lead': 8000,  'feature': 5000}
}
