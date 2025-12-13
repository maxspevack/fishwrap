import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import fetcher

class TestFetcherResilience(unittest.TestCase):
    
    @patch('fishwrap.utils.fetch_url')
    def test_process_feed_garbage(self, mock_fetch):
        print("[TEST] Verifying Fetcher Resilience (Garbage Input)...")
        
        # Scenario 1: Garbage XML
        mock_fetch.return_value = "<rss>Garbage<broken>"
        
        items = fetcher.process_feed('http://bad-feed.com', 0)
        
        if items == []:
            print("  [PASS] Handled Garbage XML (Empty list returned).")
        else:
            print(f"  [FAIL] Did not handle garbage XML: {items}")
            sys.exit(1)
            
    @patch('fishwrap.utils.fetch_url')
    def test_process_feed_none(self, mock_fetch):
        # Scenario 2: Network Failure (None)
        mock_fetch.return_value = None
        
        items = fetcher.process_feed('http://dead-feed.com', 0)
        
        if items == []:
            print("  [PASS] Handled Network Failure (Empty list returned).")
        else:
            print(f"  [FAIL] Did not handle None: {items}")
            sys.exit(1)

if __name__ == "__main__":
    unittest.main()
