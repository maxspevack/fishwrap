import sys
import os
import uuid
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap.db import repository
# Ensure we use a test config/db
os.environ['FISHWRAP_CONFIG'] = 'demo/test_config.py'
import importlib
import fishwrap._config
importlib.reload(fishwrap._config)
importlib.reload(repository)

def test_enhancer_persistence():
    print("[TEST] Testing Enhancer DB Persistence...")
    
    # 1. Create Article
    aid = str(uuid.uuid4())
    art = {
        'id': aid,
        'title': 'Enhancer Test',
        'link': f'http://test.com/{aid}',
        'source_url': 'http://test.com',
        'timestamp': time.time(),
        'is_enhanced': False
    }
    
    repository.upsert_article(art)
    print("[TEST] Article inserted.")
    
    # 2. Update Enhancement
    content = "This is the full text content."
    comments = ["Comment 1", "Comment 2"]
    
    success = repository.update_enhancement(aid, content, comments)
    if not success:
        print("[FAIL] update_enhancement returned False")
        return
        
    print("[TEST] update_enhancement returned True.")
    
    # 3. Verify
    fetched = repository.get_article_by_id(aid)
    
    if fetched['full_content'] == content:
        print("[PASS] Full Content matches.")
    else:
        print(f"[FAIL] Content mismatch: {fetched.get('full_content')}")
        
    if fetched['comments_full'] == comments:
        print("[PASS] Comments match.")
    else:
        print(f"[FAIL] Comments mismatch: {fetched.get('comments_full')}")
        
    if fetched['is_enhanced'] is True:
        print("[PASS] is_enhanced is True.")
    else:
        print(f"[FAIL] is_enhanced is {fetched.get('is_enhanced')}")

if __name__ == "__main__":
    test_enhancer_persistence()
