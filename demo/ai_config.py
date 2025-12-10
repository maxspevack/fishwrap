# --- 1. Feeds (Sources) ---
FEEDS = [
  "https://www.reddit.com/r/LocalLLaMA.json",      # Open Source Models & Engineering
  "https://www.reddit.com/r/MachineLearning.json", # Academic Discussion
  "https://simonwillison.net/atom/entries/",       # Simon Willison (Engineering)
  "http://export.arxiv.org/rss/cs.CL",             # Arxiv: Computation and Language (LLMs)
  "http://export.arxiv.org/rss/cs.LG",             # Arxiv: Machine Learning
  "https://hnrss.org/newest?q=llm+OR+gpt+OR+transformer+OR+generative+ai" # HN AI Stream
]

import os

# --- 2. File Paths ---
ARTICLES_DB_FILE = 'demo/data/ai_articles_db.json'
RUN_SHEET_FILE = 'demo/data/ai_run_sheet.json'
ENHANCED_ISSUE_FILE = 'demo/data/ai_enhanced_issue.json'
SECRETS_FILE = 'demo/secrets.json'
STATS_FILE = 'demo/data/ai_publication_stats.json'
LATEST_HTML_FILE = 'demo/output/ai_latest.html'
LATEST_PDF_FILE = 'demo/output/ai_latest.pdf'

# --- 3. Pipeline Settings ---
TIMEZONE = "UTC"
FOUNDING_DATE = "2025-12-07"
THEME = "demo/themes/basic"
MAX_ARTICLE_LENGTH = 20000 # Papers can be long
EXPIRATION_HOURS = 24 
USER_AGENT = 'Fishwrap-AI-Pilot/1.0 (+https://github.com/maxspevack/fishwrap)'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'research': 5,
    'models': 5,
    'engineering': 8,
    'discussion': 5
}

MIN_SECTION_SCORES = {
    'research': 2000,
    'models': 3000,
    'engineering': 500,
    'discussion': 500
}

# --- 5. Source Affinity ---
SOURCE_SECTIONS = {
    'arxiv.org': 'research',
    'reddit.com/r/MachineLearning': 'research',
    'reddit.com/r/LocalLLaMA': 'models',
    'simonwillison.net': 'engineering',
    'hnrss.org': 'engineering'
}

# --- 6. Classification Keywords ---
KEYWORDS = {
    'research': ['arxiv', 'paper', 'citation', 'novel', 'state of the art', 'sota', 'method', 'abstract'],
    'models': ['release', 'weights', 'huggingface', 'gguf', 'quantized', 'llama', 'mixtral', 'fine-tune', 'lora'],
    'engineering': ['code', 'github', 'implementation', 'python', 'api', 'library', 'tool', 'optimization', 'rag'],
    'discussion': ['opinion', 'ethics', 'regulation', 'agi', 'future', 'prediction', 'market', 'openai', 'sam altman']
}

# --- 7. Editorial Policies ---
BOOST_UNIT_VALUE = 200
FUZZY_BOOST_MULTIPLIER = 1.5

SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0, 'score_weight': 1.0, 'comment_weight': 2.0}, # High weight on comments to find consensus
    'static':  {'base_boosts': 10, 'score_weight': 0, 'comment_weight': 0},
}

EDITORIAL_POLICIES = [
    # Boost Working Code & Artifacts
    {'type': 'keyword_boost', 'phrases': ['github.com', 'huggingface.co', 'colab', 'demo'], 'boosts': 10},
    {'type': 'keyword_boost', 'phrases': ['release', 'open source', 'weights available'], 'boosts': 5},
    
    # Boost High-Signal Authors/Topics
    {'type': 'content_boost', 'phrases': ['Simon Willison', 'Karpathy', 'LeCun'], 'boosts': 3},
    
    # Penalties for Hype
    {'type': 'keyword_penalty', 'phrases': ['game changer', 'will change everything', 'shocking', 'mind blowing'], 'boosts': -20},
    {'type': 'keyword_penalty', 'phrases': ['AGI', 'consciousness', 'is dead', 'top 10'], 'boosts': -10}
]

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'models', 'title': '✨ New Models & Weights', 'description': 'Fresh releases you can run.'},
    {'id': 'research', 'title': 'Research Papers', 'description': 'Arxiv preprints and academic breakthroughs.'},
    {'id': 'engineering', 'title': 'Engineering & Code', 'description': 'Tools, libraries, and implementation details.'},
    {'id': 'discussion', 'title': 'The Discourse', 'description': 'Debates, ethics, and industry moves.'}
]

# --- 9. Visual Formatting Thresholds ---
VISUAL_THRESHOLDS = {
    'models':      {'lead': 8000, 'feature': 5000},
    'research':    {'lead': 6000, 'feature': 4000},
    'engineering': {'lead': 5000, 'feature': 3000},
    'discussion':  {'lead': 4000, 'feature': 2000}
}
