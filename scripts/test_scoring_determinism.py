import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import scoring
from fishwrap import _config

def test_scoring_determinism():
    print("[TEST] Verifying Scoring Determinism...")
    
    # Mock Config
    _config.SCORING_PROFILES = {
        'dynamic': {'base_boosts': 0, 'score_weight': 1.0, 'comment_weight': 1.0},
        'static': {'base_boosts': 10, 'score_weight': 0, 'comment_weight': 0}
    }
    _config.EDITORIAL_POLICIES = [
        {'type': 'keyword_penalty', 'phrases': ['bad'], 'boosts': -50}
    ]
    _config.BOOST_UNIT_VALUE = 100
    
    article = {
        'title': 'Good Article',
        'stats_score': 100,
        'stats_comments': 50
    }
    
    # Run 1
    base_score, _ = scoring.compute_score(article, section='tech')
    
    # Run 2 (Should be identical)
    base_score_2, _ = scoring.compute_score(article, section='tech')
    
    if base_score != base_score_2:
        print(f"[FAIL] Scoring is non-deterministic! {base_score} != {base_score_2}")
        sys.exit(1)
        
    print("[PASS] Scoring is deterministic.")

if __name__ == "__main__":
    test_scoring_determinism()