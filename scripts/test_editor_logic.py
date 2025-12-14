import sys
import os
import time
import random
import string

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import editor
from fishwrap import _config

def test_editor_selection():
    print("[TEST] Testing Editor Selection Logic...")
    
    # Mock Candidates
    now = time.time()
    candidates = []
    
    # Vocabulary to ensure distinctness
    vocab = ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape", "Honeydew", "Igloo", "Jackfruit",
             "Kiwi", "Lemon", "Mango", "Nectarine", "Orange", "Papaya", "Quince", "Raspberry", "Strawberry", "Tangerine",
             "Ugli", "Vanilla", "Watermelon", "Xigua", "Yellow", "Zucchini", "Alpha", "Beta", "Gamma", "Delta",
             "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi",
             "Omicron", "Pi", "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"]
    
    # Create 50 candidates for 'news', scores 100..5000
    for i in range(50):
        # Use vocab to be distinct
        word = vocab[i] if i < len(vocab) else f"Generic{i}"
        
        candidates.append({
            'id': f'news-{i}',
            'title': word,
            'timestamp': now,
            'computed_category': 'news',
            'temp_section': 'news',
            'computed_score': i * 100, # 0 to 4900
            'impact_score': i * 100, # Initialize impact_score
            'source_url': 'http://test.com'
        })
        
    # Configure Editor Settings Mock
    _config.SECTIONS = [{'id': 'news', 'title': 'News', 'description': ''}]
    _config.EDITION_SIZE = {'news': 10}
    _config.MIN_SECTION_SCORES = {'news': 2000}
    _config.EXPIRATION_HOURS = 24
    
    # Run Logic
    buckets = editor.organize_and_cluster(candidates)
    
    # Verify Selection
    items = buckets.get('news', [])
    items.sort(key=lambda x: x['impact_score'], reverse=True)
    qualified = [i for i in items if i['impact_score'] >= 2000]
    selected = qualified[:10]
    
    print(f"  Pool: {len(candidates)}")
    print(f"  Bucketed: {len(items)}")
    print(f"  Qualified (>2000): {len(qualified)}")
    print(f"  Selected (Top 10): {len(selected)}")
    
    if len(selected) != 10:
        print(f"[FAIL] Expected 10 selected, got {len(selected)}")
        sys.exit(1)
        
    if selected[0]['impact_score'] < 4900:
        print(f"[FAIL] Top score wrong. Expected >= 4900, got {selected[0]['impact_score']}")
        sys.exit(1)
        
    print("[PASS] Editor selection logic is sound.")

if __name__ == "__main__":
    test_editor_selection()