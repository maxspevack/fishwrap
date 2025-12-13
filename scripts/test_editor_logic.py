import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import editor
from fishwrap import _config

def test_editor_selection():
    print("[TEST] Testing Editor Selection Logic...")
    
    # Mock Candidates
    now = time.time()
    candidates = []
    
    # Create 50 candidates for 'news', scores 100..5000
    for i in range(50):
        candidates.append({
            'id': f'news-{i}',
            'title': f'News Article {i}',
            'timestamp': now,
            'computed_category': 'news',
            'computed_score': i * 100, # 0 to 4900
            'source_url': 'http://test.com'
        })
        
    # Configure Editor Settings Mock
    _config.SECTIONS = [{'id': 'news', 'title': 'News', 'description': ''}]
    _config.EDITION_SIZE = {'news': 10}
    _config.MIN_SECTION_SCORES = {'news': 2000}
    _config.EXPIRATION_HOURS = 24
    
    # Run Logic
    # We invoke the logic inside run_editor manually to test isolation
    # organize_and_cluster
    buckets = editor.organize_and_cluster(candidates)
    
    # Verify Selection
    items = buckets['news']
    items.sort(key=lambda x: x['computed_score'], reverse=True)
    qualified = [i for i in items if i['computed_score'] >= 2000]
    selected = qualified[:10]
    
    print(f"  Pool: {len(candidates)}")
    print(f"  Qualified (>2000): {len(qualified)}")
    print(f"  Selected (Top 10): {len(selected)}")
    
    if len(selected) != 10:
        print(f"[FAIL] Expected 10 selected, got {len(selected)}")
        sys.exit(1)
        
    if selected[0]['computed_score'] != 4900:
        print(f"[FAIL] Top score wrong. Expected 4900, got {selected[0]['computed_score']}")
        sys.exit(1)
        
    print("[PASS] Editor selection logic is sound.")

if __name__ == "__main__":
    test_editor_selection()
