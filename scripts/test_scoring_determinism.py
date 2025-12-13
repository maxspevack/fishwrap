import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import scoring
from fishwrap import _config

def test_scoring_determinism():
    print("[TEST] Verifying Scoring Determinism...")
    
    article = {
        'title': "The Future of AI is Open Source",
        'content': "Llama 3 release weights github",
        'categories': ['tech', 'ai'],
        'source_url': 'https://huggingface.co/blog',
        'timestamp': 1700000000.0,
        'stats_score': 100,
        'stats_comments': 50
    }
    
    # Configure mock scoring profile
    _config.SCORING_PROFILES = {
        'static': {'base_boosts': 10, 'score_weight': 1.0, 'comment_weight': 1.0}
    }
    _config.EDITORIAL_POLICIES = [
        {'type': 'keyword_boost', 'phrases': ['Open Source'], 'boosts': 5}
    ]
    
    # Baseline
    base_score, _ = scoring.compute_score(article, section='tech')
    
    print(f"  Baseline Score: {base_score}")
    
    for i in range(100):
        score, _ = scoring.compute_score(article, section='tech')
        if score != base_score:
            print(f"[FAIL] Score changed on iteration {i}: {score}")
            sys.exit(1)
            
    print("[PASS] Scoring is deterministic over 100 iterations.")

if __name__ == "__main__":
    test_scoring_determinism()
