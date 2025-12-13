import argparse
import os
import sys
import time
import random
import uuid
from datetime import datetime, timedelta
import importlib

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Placeholder modules
_config = None
repository = None

def configure_repository(config_path):
    """Sets FISHWRAP_CONFIG env var and reloads _config and repository module."""
    global _config, repository
    
    if config_path:
        os.environ['FISHWRAP_CONFIG'] = config_path
    
    # Reload modules
    _config = importlib.import_module('fishwrap._config')
    importlib.reload(_config)
    repository = importlib.import_module('fishwrap.db.repository')
    importlib.reload(repository)

def generate_semantic_title(day_offset, tier, category, idx):
    """Generates a title like '[D-7] [GOLD] Tech - Semantic Headline #4'"""
    headlines = [
        "Major Breakthrough Announced",
        "Controversy Erupts Over Policy",
        "Team Wins Championship",
        "New Framework Released",
        "Market Crashes Unexpectedly",
        "Celebrity Spotted at Event",
        "Scientific Discovery Confirmed",
        "Election Results Finalized",
        "Merger Talks Stalled",
        "Patch Issued for Critical Bug"
    ]
    headline = random.choice(headlines)
    return f"[D-{day_offset}] [{tier}] {category.capitalize()} - {headline} #{idx}"

def get_tier_score(tier):
    if tier == 'PLATINUM': return 20000
    if tier == 'GOLD': return 10000
    if tier == 'SILVER': return 5000
    if tier == 'BRONZE': return 1000
    return 100

def seed_history(days=14):
    """Seeds the database with structured history."""
    print(f"Seeding history for {days} days...")
    
    tiers = ['PLATINUM', 'GOLD', 'SILVER', 'BRONZE', 'NOISE']
    categories = ['news', 'tech', 'sports', 'culture']
    
    # Distribution per day
    daily_mix = {
        'PLATINUM': 1,
        'GOLD': 3,
        'SILVER': 10,
        'BRONZE': 20,
        'NOISE': 20
    }
    
    base_time = time.time()
    total_inserted = 0
    
    for d in range(days):
        day_ts = base_time - (d * 86400)
        print(f"  Generating Day -{d} ({datetime.fromtimestamp(day_ts).strftime('%Y-%m-%d')})...")
        
        idx = 0
        for tier, count in daily_mix.items():
            score = get_tier_score(tier)
            
            for _ in range(count):
                idx += 1
                cat = random.choice(categories)
                title = generate_semantic_title(d, tier, cat, idx)
                
                article = {
                    'title': title,
                    'link': f"https://example.com/{uuid.uuid4()}",
                    'source_url': f"https://{cat}-source.com/feed",
                    'external_id': str(uuid.uuid4()),
                    'timestamp': day_ts + random.randint(-3600, 3600), # Jitter within 1h
                    'content': f"Content for {title}. This is verifying the Weekly logic.",
                    'categories': [cat, tier.lower()],
                    'stats_score': 0,
                    'stats_comments': 0,
                    'computed_score': float(score), # Pre-set the score
                    'computed_category': cat,
                    'computed_breakdown': {'base_boosts': 0, 'final_score': float(score), 'reason': f'Seeded {tier}'},
                    'computed_debug': {'default_section': cat}
                }
                
                res = repository.upsert_article(article)
                if res == 'new': total_inserted += 1
                
    print(f"Seeding complete. Inserted {total_inserted} articles.")

def main():
    parser = argparse.ArgumentParser(description="Seed database with synthetic history.")
    parser.add_argument('--config', type=str, required=True, help='Path to config file')
    parser.add_argument('--days', type=int, default=14, help='Number of days to generate')
    
    args = parser.parse_args()
    
    configure_repository(args.config)
    seed_history(args.days)

if __name__ == "__main__":
    main()
