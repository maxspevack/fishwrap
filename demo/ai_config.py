# --- 1. Feeds (Sources) ---
FEEDS = [
    # --- Official Labs & Research ---
    "https://openai.com/blog/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://blogs.microsoft.com/ai/feed/",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://blogs.nvidia.com/feed/",
    "https://bair.berkeley.edu/blog/feed.xml",
    
    # --- Arxiv (The Firehose) ---
    "http://export.arxiv.org/rss/cs.CL", # Computation and Language
    "http://export.arxiv.org/rss/cs.LG", # Machine Learning
    "http://export.arxiv.org/rss/stat.ML", # Machine Learning (Stats)
    "http://export.arxiv.org/rss/cs.AI", # Artificial Intelligence

    # --- Engineering & Code ---
    "https://huggingface.co/blog/feed.xml",
    "https://blog.tensorflow.org/feeds/posts/default",
    "https://simonwillison.net/atom/entries/",
    "https://lilianweng.github.io/index.xml",
    
    # --- Community & News ---
    "https://www.reddit.com/r/LocalLLaMA.json",
    "https://www.reddit.com/r/MachineLearning.json",
    "https://www.reddit.com/r/artificial.json",
    "https://hnrss.org/newest?q=llm+OR+gpt+OR+transformer+OR+generative+ai",
    "https://hnrss.org/newest?q=open+source+ai",
    
    # --- Analysis & Tutorials ---
    "https://machinelearningmastery.com/feed/",
    "https://towardsdatascience.com/feed",
    "https://www.kdnuggets.com/feed",
    "https://thegradient.pub/rss/",
    "https://lastweekin.ai/feed"
]

import os

# --- 2. File Paths ---
ARTICLES_DB_FILE = 'demo/data/ai_articles_db.json'
RUN_SHEET_FILE = 'demo/data/ai_run_sheet.json'
ENHANCED_ISSUE_FILE = 'demo/data/ai_enhanced_issue.json'
SECRETS_FILE = 'demo/secrets.json'
STATS_FILE = 'demo/data/ai_publication_stats.json'
LATEST_HTML_FILE = 'demo/output/ai_index.html'
LATEST_PDF_FILE = 'demo/output/ai_edition.pdf'

# --- 3. Pipeline Settings ---
TIMEZONE = "US/Pacific"
FOUNDING_DATE = "2025-12-07"
THEME = "demo/themes/basic"
MAX_ARTICLE_LENGTH = 25000 
EXPIRATION_HOURS = 24 
USER_AGENT = 'Fishwrap-AI-Pilot/1.0 (+https://github.com/maxspevack/fishwrap)'

# --- 4. Editor Settings ---
EDITION_SIZE = {
    'models': 6,
    'research': 6,
    'engineering': 8,
    'discussion': 6
}

MIN_SECTION_SCORES = {
    'models': 1000,
    'research': 1000,
    'engineering': 500,
    'discussion': 500
}

# --- 5. Source Affinity ---
SOURCE_SECTIONS = {
    'arxiv.org': 'research',
    'bair.berkeley.edu': 'research',
    'research.google': 'research',
    'reddit.com/r/MachineLearning': 'research',
    
    'huggingface.co': 'models',
    'reddit.com/r/LocalLLaMA': 'models',
    'openai.com': 'models',
    
    'simonwillison.net': 'engineering',
    'pytorch.org': 'engineering',
    'tensorflow.org': 'engineering',
    'aws.amazon.com': 'engineering',
    
    'reddit.com/r/artificial': 'discussion',
    'lastweekin.ai': 'discussion',
    'thegradient.pub': 'discussion'
}

# --- 6. Classification Keywords ---
KEYWORDS = {
    'research': [
        'paper', 'abstract', 'citation', 'novel', 'state of the art', 'sota', 'method', 
        'experiment', 'results', 'dataset', 'benchmark', 'survey', 'review'
    ],
    'models': [
        'release', 'weights', 'huggingface', 'gguf', 'quantized', 'llama', 'mixtral', 
        'mistral', 'gemma', 'claude', 'gpt-4', 'fine-tune', 'lora', '7b', '70b'
    ],
    'engineering': [
        'code', 'github', 'implementation', 'python', 'api', 'library', 'tool', 
        'optimization', 'rag', 'inference', 'deploy', 'gpu', 'cuda', 'docker'
    ],
    'discussion': [
        'opinion', 'ethics', 'regulation', 'agi', 'future', 'prediction', 'market', 
        'openai', 'sam altman', 'safety', 'alignment', 'policy', 'copyright'
    ]
}

# --- 7. Editorial Policies ---
BOOST_UNIT_VALUE = 200
FUZZY_BOOST_MULTIPLIER = 1.5

SCORING_PROFILES = {
    'dynamic': {'base_boosts': 0, 'score_weight': 1.0, 'comment_weight': 2.0}, 
    'static':  {'base_boosts': 10, 'score_weight': 0, 'comment_weight': 0},
}

EDITORIAL_POLICIES = [
    # Boost Working Code & Artifacts
    {'type': 'keyword_boost', 'phrases': ['github.com', 'huggingface.co', 'colab', 'demo'], 'boosts': 10},
    {'type': 'keyword_boost', 'phrases': ['weights released', 'open source', 'apache 2.0', 'mit license'], 'boosts': 5},
    
    # Boost High-Signal Authors/Topics
    {'type': 'content_boost', 'phrases': ['Simon Willison', 'Karpathy', 'LeCun', 'Ng'], 'boosts': 3},
    {'type': 'keyword_boost', 'phrases': ['Llama 3', 'GPT-5', 'Gemini'], 'boosts': 2},
    
    # Penalties for Hype
    {'type': 'keyword_penalty', 'phrases': ['game changer', 'will change everything', 'shocking', 'mind blowing'], 'boosts': -20},
    {'type': 'keyword_penalty', 'phrases': ['top 10', 'making money with ai', 'passive income'], 'boosts': -50},
    {'type': 'keyword_penalty', 'phrases': ['consciousness', 'sentient'], 'boosts': -10}
]

# --- 8. Printer Settings ---
SECTIONS = [
    {'id': 'models', 'title': '✨ New Models & Weights', 'description': 'Fresh releases you can run locally.'},
    {'id': 'research', 'title': '🔬 Research Papers', 'description': 'Arxiv preprints and academic breakthroughs.'},
    {'id': 'engineering', 'title': '🛠️ Engineering & Code', 'description': 'Tools, libraries, and implementation details.'},
    {'id': 'discussion', 'title': '💬 The Discourse', 'description': 'Debates, ethics, and industry moves.'}
]

# --- 9. Visual Formatting Thresholds ---
VISUAL_THRESHOLDS = {
    'models':      {'lead': 8000, 'feature': 5000},
    'research':    {'lead': 6000, 'feature': 4000},
    'engineering': {'lead': 5000, 'feature': 3000},
    'discussion':  {'lead': 4000, 'feature': 2000}
}